#!/usr/bin/env python3
"""Insight writer/harvester for /sc:insight command and session-lifecycle hooks.

Subcommands:
    append      Write a structured insight to .claude/insights.jsonl (stdin or --json)
    list        Show recent insights (jq required)
    query       Filter insights by key=value (jq required)
    stats       Type/tag distribution (jq required)
    harvest     Scan current session transcript for INSIGHT: markers → pending
    review      List entries in .claude/insights.pending.jsonl
    promote     Move a pending entry to insights.jsonl as a structured insight
    pending-count   Print count of pending entries (for SessionStart notice)

Read paths require jq; write paths are pure Python. Missing jq prints install
hint to stderr and exits 1.

Hook integration:
    SessionEnd / PreCompact → harvest --source <reason>
    SessionStart            → pending-count

Transcript discovery: ~/.claude/projects/<encoded-cwd>/<session_id>.jsonl
where encoded-cwd replaces [:\\/] with '-'.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

INSIGHT_FILE = Path(".claude/insights.jsonl")
PENDING_FILE = Path(".claude/insights.pending.jsonl")
VALID_TYPES = {"feedback", "decision", "discovery", "pattern", "metric", "annotation"}
# Match INSIGHT: at line start OR inline ('text INSIGHT: rest'). Word boundary
# prevents matching 'INSIGHTS:' or 'INSIGHTFUL:'. Lazy + lookahead lets multiple
# markers on the same physical line each produce their own entry. MULTILINE so
# $ binds end-of-line, not end-of-string.
MARKER_RE = re.compile(
    r"\bINSIGHT\s*:\s*(.+?)(?=\s*\bINSIGHT\s*:|$)",
    re.MULTILINE,
)
# Cap transcript scan to keep hook within 10s timeout on huge sessions.
TRANSCRIPT_TAIL_BYTES = 5 * 1024 * 1024  # 5 MB


# ---------- helpers ----------


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    """ISO 8601 with second precision and colon offset (matches existing schema)."""
    now = _dt.datetime.now().astimezone()
    s = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    return s[:-2] + ":" + s[-2:] if s[-5] in "+-" else s


def _git_user() -> str:
    try:
        r = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, timeout=3
        )
        if r.returncode == 0:
            return r.stdout.strip().lower().replace(" ", "")
    except (OSError, subprocess.TimeoutExpired):
        pass
    return os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"


def _require_jq() -> str:
    jq = shutil.which("jq")
    if not jq:
        print(
            "jq not found — install: https://jqlang.github.io/jq/download/",
            file=sys.stderr,
        )
        sys.exit(1)
    return jq


def _encode_cwd(cwd: str) -> str:
    """Replicate Claude Code's projects-dir encoding: each [:\\/] → '-' (no coalescing).

    e.g. 'C:\\Users\\ajitta' → 'C--Users-ajitta' (':\\' becomes '--').
    """
    return re.sub(r"[:\\/]", "-", cwd)


def _project_dir(cwd: str) -> Path:
    return Path.home() / ".claude" / "projects" / _encode_cwd(cwd)


def _find_transcript(session_id: str | None, cwd: str) -> Path | None:
    pdir = _project_dir(cwd)
    if not pdir.exists():
        return None
    if session_id:
        cand = pdir / f"{session_id}.jsonl"
        if cand.exists():
            return cand
    # Fallback: most recently modified jsonl in the project dir
    files = sorted(pdir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


# ---------- write paths ----------


def cmd_append(args: argparse.Namespace) -> int:
    raw = args.json if args.json else sys.stdin.read()
    if not raw.strip():
        print("append: empty input", file=sys.stderr)
        return 2
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"append: invalid JSON — {e}", file=sys.stderr)
        return 2

    entries = payload if isinstance(payload, list) else [payload]
    cleaned: list[dict] = []
    for entry in entries:
        if not isinstance(entry, dict):
            print(f"append: entry must be object, got {type(entry).__name__}", file=sys.stderr)
            return 2
        # Defensive copy: avoid mutating caller's dict (cmd_promote etc.).
        entry = dict(entry)
        if "ts" not in entry:
            entry["ts"] = _now_iso()
        if "author" not in entry:
            entry["author"] = _git_user()
        for required in ("type", "insight"):
            if required not in entry:
                print(f"append: missing required field '{required}'", file=sys.stderr)
                return 2
        if not isinstance(entry["insight"], str) or not entry["insight"].strip():
            print("append: 'insight' must be a non-empty string", file=sys.stderr)
            return 2
        if entry["type"] not in VALID_TYPES:
            print(
                f"append: invalid type '{entry['type']}' — must be one of {sorted(VALID_TYPES)}",
                file=sys.stderr,
            )
            return 2
        if entry["type"] == "annotation":
            ref_ts = entry.get("ref_ts")
            if not ref_ts:
                print("append: annotation requires ref_ts", file=sys.stderr)
                return 2
            if not _annotation_target_exists(ref_ts):
                print(f"append: ref_ts '{ref_ts}' does not match any non-annotation entry", file=sys.stderr)
                return 2
        cleaned.append(entry)

    _ensure_parent(INSIGHT_FILE)
    with INSIGHT_FILE.open("a", encoding="utf-8") as f:
        for entry in cleaned:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"appended {len(cleaned)} insight(s) to {INSIGHT_FILE}")
    return 0


def _annotation_target_exists(ref_ts: str) -> bool:
    if not INSIGHT_FILE.exists():
        return False
    with INSIGHT_FILE.open(encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("ts") == ref_ts and d.get("type") != "annotation":
                return True
    return False


# ---------- read paths (jq) ----------


def cmd_list(args: argparse.Namespace) -> int:
    if not INSIGHT_FILE.exists():
        print("(no insights yet)")
        return 0
    jq = _require_jq()
    r = subprocess.run(
        [jq, "-r", r'"\(.ts) [\(.author // "unknown")] [\(.type)] \(.insight)"', str(INSIGHT_FILE)],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return r.returncode
    lines = r.stdout.strip().split("\n")
    for line in lines[-args.limit :]:
        print(line)
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    if not INSIGHT_FILE.exists():
        print("(no insights yet)")
        return 0
    if "=" not in args.expr:
        print("query: expected key=value", file=sys.stderr)
        return 2
    key, value = args.expr.split("=", 1)
    if not key.isidentifier():
        print(f"query: invalid key '{key}' (must be identifier)", file=sys.stderr)
        return 2
    jq = _require_jq()
    # Pass value via --arg to prevent jq-syntax injection from model-supplied text.
    if key == "tags":
        filt = "select(.tags // [] | index($v))"
    else:
        filt = f"select(.{key}==$v)"
    r = subprocess.run([jq, "--arg", "v", value, filt, str(INSIGHT_FILE)], text=True)
    return r.returncode


def cmd_stats(args: argparse.Namespace) -> int:
    if not INSIGHT_FILE.exists():
        print("(no insights yet)")
        return 0
    jq = _require_jq()
    type_filt = ".type" if args.all else 'select(.type != "annotation") | .type'
    r = subprocess.run(
        [jq, "-r", type_filt, str(INSIGHT_FILE)],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return r.returncode
    counts: dict[str, int] = {}
    for line in r.stdout.strip().split("\n"):
        if line:
            counts[line] = counts.get(line, 0) + 1
    print("Type distribution:")
    for t, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {n:>4}  {t}")
    print(f"Total: {sum(counts.values())}")
    return 0


# ---------- harvest ----------


def cmd_harvest(args: argparse.Namespace) -> int:
    """Scan transcript for INSIGHT: markers → append unique entries to pending.

    Pending file is anchored to args.cwd (the project the hook fired from), not
    the script's process cwd, so harvest writes to the correct project even if
    a non-default hook config invoked us from elsewhere.
    """
    cwd = args.cwd or os.getcwd()
    transcript = _find_transcript(args.session_id, cwd)
    if not transcript:
        return 0  # silent: no transcript yet (e.g., first session)

    pending_path = Path(cwd) / ".claude" / "insights.pending.jsonl"

    existing_uuids: set[str] = set()
    if pending_path.exists():
        with pending_path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    existing_uuids.add(json.loads(line).get("uuid", ""))
                except json.JSONDecodeError:
                    continue

    new_entries: list[dict] = []
    with transcript.open("rb") as raw_f:
        # Tail-only scan for huge transcripts. Small files read in full.
        size = transcript.stat().st_size
        if size > TRANSCRIPT_TAIL_BYTES:
            seek_pos = size - TRANSCRIPT_TAIL_BYTES
            # Only discard the first line if we landed mid-line. Peek the byte
            # before seek_pos: if it's '\n', we're already at line start.
            raw_f.seek(seek_pos - 1)
            prev = raw_f.read(1)
            if prev != b"\n":
                raw_f.readline()  # discard partial line
        # Decode after seek so we don't break inside a multi-byte sequence.
        f = (line.decode("utf-8", errors="replace") for line in raw_f)
        for raw in f:
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if rec.get("type") != "user" or rec.get("isMeta"):
                continue
            msg = rec.get("message", {})
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    c.get("text", "") if isinstance(c, dict) else str(c) for c in content
                )
            if not isinstance(content, str):
                continue
            for m in MARKER_RE.finditer(content):
                marker_text = m.group(1).strip()
                if not marker_text:
                    continue
                # Per-marker uuid: message uuid + offset hash for stable dedup
                base_uuid = rec.get("uuid", "")
                marker_id = (
                    f"{base_uuid}:{hashlib.md5(marker_text.encode('utf-8')).hexdigest()[:8]}"
                )
                if marker_id in existing_uuids:
                    continue
                existing_uuids.add(marker_id)
                new_entries.append(
                    {
                        "harvested_at": _now_iso(),
                        "session_id": rec.get("sessionId") or args.session_id,
                        "source": args.source,
                        "user_ts": rec.get("timestamp"),
                        "raw_text": marker_text,
                        "uuid": marker_id,
                        "transcript": str(transcript),
                    }
                )

    if not new_entries:
        return 0

    _ensure_parent(pending_path)
    with pending_path.open("a", encoding="utf-8") as f:
        for e in new_entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    print(f"🟡 harvested {len(new_entries)} pending insight(s) — /sc:insight --review")
    return 0


# ---------- review / promote / pending-count ----------


def _read_pending() -> list[dict]:
    if not PENDING_FILE.exists():
        return []
    out: list[dict] = []
    with PENDING_FILE.open(encoding="utf-8") as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _write_pending(entries: list[dict]) -> None:
    if not entries:
        if PENDING_FILE.exists():
            PENDING_FILE.unlink()
        return
    _ensure_parent(PENDING_FILE)
    with PENDING_FILE.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def cmd_review(args: argparse.Namespace) -> int:
    pending = _read_pending()
    if not pending:
        print("(no pending insights)")
        return 0
    print(f"# {len(pending)} pending insight(s) — promote with: insight_writer.py promote --index N --type TYPE")
    for i, e in enumerate(pending):
        ts = e.get("user_ts") or e.get("harvested_at", "")
        src = e.get("source", "?")
        text = e.get("raw_text", "").replace("\n", " ")
        print(f"[{i}] ts={ts} source={src}")
        print(f"    {text[:200]}")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    pending = _read_pending()
    if args.index < 0 or args.index >= len(pending):
        print(f"promote: index {args.index} out of range (have {len(pending)})", file=sys.stderr)
        return 2
    p = pending[args.index]
    insight_text = (args.insight or p.get("raw_text", "")).strip()
    if not insight_text:
        print(
            f"promote: pending entry {args.index} has empty raw_text; pass --insight \"...\"",
            file=sys.stderr,
        )
        return 2
    entry = {
        "ts": _now_iso(),
        "type": args.type,
        "insight": insight_text,
        "author": _git_user(),
        "context": f"harvested from session {p.get('session_id','?')} ({p.get('source','?')})",
    }
    if args.tags:
        entry["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]

    payload = json.dumps(entry, ensure_ascii=False)
    rc = cmd_append(argparse.Namespace(json=payload))
    if rc != 0:
        # Append failed (validation error): preserve pending so user can retry.
        return rc

    # Append succeeded — only now is it safe to remove from pending.
    pending.pop(args.index)
    _write_pending(pending)
    print(f"promoted index {args.index} → {INSIGHT_FILE} (remaining pending: {len(pending)})")
    return 0


def cmd_pending_count(args: argparse.Namespace) -> int:
    n = len(_read_pending())
    if n > 0:
        print(f"🟡 {n} pending insight(s) — run /sc:insight --review")
    return 0


# ---------- main ----------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="insight_writer", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("append")
    a.add_argument("--json", help="JSON object or array (default: stdin)")
    a.set_defaults(fn=cmd_append)

    ls = sub.add_parser("list")
    ls.add_argument("--limit", type=int, default=20)
    ls.set_defaults(fn=cmd_list)

    q = sub.add_parser("query")
    q.add_argument("expr", help="key=value (e.g. type=feedback, tags=rules)")
    q.set_defaults(fn=cmd_query)

    s = sub.add_parser("stats")
    s.add_argument("--all", action="store_true", help="include annotations")
    s.set_defaults(fn=cmd_stats)

    h = sub.add_parser("harvest")
    h.add_argument("--source", default="other", help="hook source (clear|compact|other|...)")
    h.add_argument("--session-id", default=os.environ.get("CLAUDE_SESSION_ID"))
    h.add_argument("--cwd", default=None)
    h.set_defaults(fn=cmd_harvest)

    r = sub.add_parser("review")
    r.set_defaults(fn=cmd_review)

    pr = sub.add_parser("promote")
    pr.add_argument("--index", type=int, required=True)
    pr.add_argument("--type", required=True, choices=sorted(VALID_TYPES))
    pr.add_argument("--insight", help="override raw_text")
    pr.add_argument("--tags", help="comma-separated tags")
    pr.set_defaults(fn=cmd_promote)

    pc = sub.add_parser("pending-count")
    pc.set_defaults(fn=cmd_pending_count)

    return p


def main(argv: list[str] | None = None) -> int:
    # Special hook entry point: when invoked from PreCompact/SessionEnd hooks,
    # the harness pipes JSON to stdin. If first arg is "harvest-from-hook",
    # parse stdin to extract session_id / cwd / source automatically.
    if argv is None:
        argv = sys.argv[1:]

    if argv and argv[0] == "harvest-from-hook":
        try:
            data = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            data = {}
        source = (
            data.get("source")  # SessionEnd
            or data.get("trigger")  # PreCompact
            or "other"
        )
        argv = [
            "harvest",
            "--source",
            str(source),
            "--session-id",
            str(data.get("session_id", "")),
            "--cwd",
            str(data.get("cwd", os.getcwd())),
        ]

    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
