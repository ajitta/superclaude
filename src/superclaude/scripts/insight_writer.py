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
    SessionEnd / PreCompact → harvest-from-hook (stdin JSON: reason/trigger + cwd)
    SessionStart            → pending-count-from-hook (stdin JSON: cwd)

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

from superclaude.utils import (
    hook_state_dir,
    project_key,
    project_root,
    session_slug,
)


def _insight_file() -> Path:
    """Durable insight history — user data, anchored at the project root.

    Resolved per call rather than at import: the project anchor comes from the
    environment, and a CWD-relative literal would split the history whenever a
    hook or Bash call runs from a subdirectory.
    """
    return project_root() / ".claude" / "insights.jsonl"


def _pending_file() -> Path:
    """Raw INSIGHT: markers awaiting promotion. Same anchor as _insight_file()."""
    return project_root() / ".claude" / "insights.pending.jsonl"


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
            print(
                f"append: entry must be object, got {type(entry).__name__}",
                file=sys.stderr,
            )
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
                print(
                    f"append: ref_ts '{ref_ts}' does not match any non-annotation entry",
                    file=sys.stderr,
                )
                return 2
        cleaned.append(entry)

    _ensure_parent(_insight_file())
    with _insight_file().open("a", encoding="utf-8") as f:
        for entry in cleaned:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"appended {len(cleaned)} insight(s) to {_insight_file()}")
    return 0


def _annotation_target_exists(ref_ts: str) -> bool:
    if not _insight_file().exists():
        return False
    with _insight_file().open(encoding="utf-8") as f:
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
    if not _insight_file().exists():
        print("(no insights yet)")
        return 0
    jq = _require_jq()
    r = subprocess.run(
        [
            jq,
            "-r",
            r'"\(.ts) [\(.author // "unknown")] [\(.type)] \(.insight)"',
            str(_insight_file()),
        ],
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
    if not _insight_file().exists():
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
    r = subprocess.run([jq, "--arg", "v", value, filt, str(_insight_file())], text=True)
    return r.returncode


def cmd_stats(args: argparse.Namespace) -> int:
    if not _insight_file().exists():
        print("(no insights yet)")
        return 0
    jq = _require_jq()
    type_filt = ".type" if args.all else 'select(.type != "annotation") | .type'
    r = subprocess.run(
        [jq, "-r", type_filt, str(_insight_file())],
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

    Pending file resolves through _pending_file() like every other writer, so
    harvest and promote never disagree about which project's file they are on.
    args.cwd stays the transcript anchor: Claude Code encodes the *session* cwd
    into the transcript directory name, which is not always the project root.
    """
    cwd = args.cwd or os.getcwd()
    transcript = _find_transcript(args.session_id, cwd)
    if not transcript:
        return 0  # silent: no transcript yet (e.g., first session)

    pending_path = _pending_file()

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
            # Assistant records are scanned too. Harvesting user records alone
            # meant the only producer was the user typing INSIGHT: by hand, which
            # happened 5 times in 10 months — the subsystem had no other source.
            if rec.get("type") not in ("user", "assistant") or rec.get("isMeta"):
                continue
            msg = rec.get("message", {})
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    c.get("text", "") if isinstance(c, dict) else str(c)
                    for c in content
                )
            if not isinstance(content, str):
                continue
            # The Stop hook's own request names the marker it is asking for.
            # Without this, every request would harvest as an insight.
            if REQUEST_SENTINEL in content:
                continue
            for m in MARKER_RE.finditer(content):
                marker_text = m.group(1).strip()
                if not marker_text:
                    continue
                # Per-marker uuid: message uuid + offset hash for stable dedup
                base_uuid = rec.get("uuid", "")
                marker_id = f"{base_uuid}:{hashlib.md5(marker_text.encode('utf-8')).hexdigest()[:8]}"
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


def _read_pending(path: Path | None = None) -> list[dict]:
    path = path if path is not None else _pending_file()
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _write_pending(entries: list[dict]) -> None:
    if not entries:
        if _pending_file().exists():
            _pending_file().unlink()
        return
    _ensure_parent(_pending_file())
    with _pending_file().open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def cmd_review(args: argparse.Namespace) -> int:
    pending = _read_pending()
    if not pending:
        print("(no pending insights)")
        return 0
    print(
        f"# {len(pending)} pending insight(s) — promote with: insight_writer.py promote --index N --type TYPE"
    )
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
        print(
            f"promote: index {args.index} out of range (have {len(pending)})",
            file=sys.stderr,
        )
        return 2
    p = pending[args.index]
    insight_text = (args.insight or p.get("raw_text", "")).strip()
    if not insight_text:
        print(
            f'promote: pending entry {args.index} has empty raw_text; pass --insight "..."',
            file=sys.stderr,
        )
        return 2
    entry = {
        "ts": _now_iso(),
        "type": args.type,
        "insight": insight_text,
        "author": _git_user(),
        "context": f"harvested from session {p.get('session_id', '?')} ({p.get('source', '?')})",
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
    print(
        f"promoted index {args.index} → {_insight_file()} (remaining pending: {len(pending)})"
    )
    return 0


def cmd_pending_count(args: argparse.Namespace) -> int:
    # Same resolver as cmd_harvest, so the SessionStart notice always reads the
    # pending file harvest wrote.
    n = len(_read_pending())
    if n > 0:
        print(f"🟡 {n} pending insight(s) — run /sc:insight --review")
    return 0


# Marks the Stop hook's own request so harvest does not read it back as an
# insight, and so the model can see which turn it is answering.
REQUEST_SENTINEL = "[sc-insight-request]"

REQUEST_REASON = (
    f"{REQUEST_SENTINEL} Before finishing: if this session produced a lesson "
    "worth keeping — a non-obvious cause, a decision and its reasoning, a trap "
    "that cost time — end your reply with one line beginning with the word "
    "INSIGHT followed by a colon and the lesson. One line, specific enough to "
    "act on months from now. If nothing this session qualifies, say so in a few "
    "words and stop; do not invent one."
)


def _request_guard_file(session_id: str | None) -> Path:
    """One-shot marker so a session is asked at most once."""
    slug = session_slug(session_id) or "nosession"
    return hook_state_dir() / f"insight_prompt_{project_key()}_{slug}.json"


# Paths the framework itself writes inside a project worktree. A project- or
# local-scope install keeps its runtime cache, its pending markers and its agent
# memory store under <project>/.claude, and project scope gets no git-exclude
# block at all — so without this filter the framework's own files answered
# "did the session change code?" with yes, and a read-only session ended on a
# blocking Stop. Filtering here holds in every scope, which the exclude list
# alone cannot do.
_FRAMEWORK_OWNED_PATHS = (
    ".claude/.superclaude_hooks/",
    ".claude/insights.jsonl",
    ".claude/insights.pending.jsonl",
    ".claude/agent-memory/",
    ".claude/agent-memory-local/",
)


def _status_lines() -> list[str] | None:
    """Sorted `git status --porcelain` lines, framework-owned paths removed.

    Returns None when git cannot answer at all — no repository, no git on PATH,
    a timeout — which every caller treats as "do not prompt".
    """
    try:
        result = subprocess.run(
            # -uall: without it git collapses an untracked directory to a
            # single `?? .claude/` line, and a framework-owned path inside it
            # can no longer be recognised or filtered.
            ["git", "status", "--porcelain", "-uall"],
            cwd=str(project_root()),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None

    lines = []
    for raw in result.stdout.splitlines():
        if len(raw) < 4:
            continue
        path = raw[3:]
        if " -> " in path:  # rename/copy: the destination is what exists now
            path = path.split(" -> ", 1)[1]
        path = path.strip().strip('"')
        if any(path.startswith(owned) for owned in _FRAMEWORK_OWNED_PATHS):
            continue
        lines.append(raw)
    return sorted(lines)


def _working_tree_changed() -> bool:
    """Whether this project has uncommitted changes the user cares about.

    The fallback proxy, used when no session baseline was recorded. Any git
    failure means no prompt.
    """
    return bool(_status_lines())


def _tree_fingerprint() -> str | None:
    """A hash of the working tree's status, or None when git cannot answer."""
    lines = _status_lines()
    if lines is None:
        return None
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _session_baseline_file(session_id: str | None) -> Path:
    """Where SessionStart records what the tree looked like before the session."""
    slug = session_slug(session_id) or "nosession"
    return hook_state_dir() / f"insight_baseline_{project_key()}_{slug}.json"


def cmd_session_baseline(args: argparse.Namespace) -> int:
    """SessionStart: remember the tree so Stop can tell what this session did.

    Without it the gate could only ask "is the tree dirty now", which a
    repository dirty before the session started answers yes on the very first
    turn — spending the one request a session gets on a turn that changed
    nothing.
    """
    fingerprint = _tree_fingerprint()
    if fingerprint is None:
        return 0
    path = _session_baseline_file(getattr(args, "session_id", None))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"fingerprint": fingerprint, "at": _now_iso()}),
            encoding="utf-8",
        )
    except OSError:
        pass  # a missing baseline degrades to the proxy, it does not break Stop
    return 0


def _session_changed_code(session_id: str | None) -> bool:
    """Did *this* session change code, rather than "is the tree dirty"."""
    current = _tree_fingerprint()
    if current is None:
        return False
    try:
        recorded = json.loads(
            _session_baseline_file(session_id).read_text(encoding="utf-8")
        ).get("fingerprint")
    except (OSError, json.JSONDecodeError, AttributeError):
        recorded = None
    if not recorded:
        return bool(_status_lines())
    return current != recorded


def cmd_request(args: argparse.Namespace) -> int:
    """Stop hook: ask the model for one INSIGHT: line, at most once per session.

    The harvester works and has always worked; nothing produced the markers it
    scans for, so it returned zero for three and a half months. The manual entry
    point, /sc:insight, is typed a handful of times a year, and a rule attached to
    /sc:reflect or /sc:save inherits the same problem — those have to be typed
    too. A Stop hook is the only producer that does not.

    Four gates, because a Stop hook that blocks is intrusive by construction:
    the opt-out env var, Claude Code's own re-entry flag, one fire per session,
    and a working tree this session actually changed.
    """
    if os.environ.get("SUPERCLAUDE_INSIGHT_PROMPT", "1").lower() in (
        "0",
        "false",
        "no",
    ):
        return 0
    # Set by Claude Code when a Stop hook already continued this turn. Without
    # this check the block below would answer itself forever.
    if getattr(args, "stop_hook_active", False):
        return 0

    guard = _request_guard_file(getattr(args, "session_id", None))
    if guard.exists():
        return 0
    if not _session_changed_code(getattr(args, "session_id", None)):
        return 0

    try:
        guard.parent.mkdir(parents=True, exist_ok=True)
        guard.write_text(_now_iso(), encoding="utf-8")
    except OSError:
        return 0  # cannot guarantee one-shot, so do not ask at all

    print(json.dumps({"decision": "block", "reason": REQUEST_REASON}))
    return 0


# ---------- main ----------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="insight_writer", description=__doc__.split("\n")[0]
    )
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
    h.add_argument(
        "--source", default="other", help="hook source (clear|compact|other|...)"
    )
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

    # No --cwd: the pending file is anchored on project_root(), so accepting a
    # cwd here would be a flag that silently does nothing.
    pc = sub.add_parser("pending-count")
    pc.set_defaults(fn=cmd_pending_count)

    sb = sub.add_parser("session-baseline")
    sb.add_argument("--session-id", default=os.environ.get("CLAUDE_SESSION_ID"))
    sb.set_defaults(fn=cmd_session_baseline)

    rq = sub.add_parser("request")
    rq.add_argument("--session-id", default=os.environ.get("CLAUDE_SESSION_ID"))
    rq.add_argument("--stop-hook-active", action="store_true")
    rq.set_defaults(fn=cmd_request)

    return p


def main(argv: list[str] | None = None) -> int:
    # Special hook entry points: when invoked from SessionStart/PreCompact/
    # SessionEnd/Stop hooks, the harness pipes JSON to stdin. Parse it to
    # extract session_id / cwd / reason|trigger / stop_hook_active automatically.
    if argv is None:
        argv = sys.argv[1:]

    if argv and argv[0] == "request-from-hook":
        try:
            data = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            data = {}
        argv = ["request", "--session-id", str(data.get("session_id", ""))]
        if data.get("stop_hook_active"):
            argv.append("--stop-hook-active")

    if argv and argv[0] in ("harvest-from-hook", "pending-count-from-hook"):
        try:
            data = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            data = {}
        cwd = str(data.get("cwd", os.getcwd()))
        if argv[0] == "pending-count-from-hook":
            # SessionStart is the only event that runs before the session can
            # change anything, so the baseline is recorded here rather than in a
            # fifteenth hook and a second interpreter spawn.
            cmd_session_baseline(
                argparse.Namespace(session_id=str(data.get("session_id", "")))
            )
            argv = ["pending-count"]
        else:
            source = (
                data.get("reason")  # SessionEnd
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
                cwd,
            ]

    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
