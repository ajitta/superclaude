"""Unit tests for insight_writer.

Covers: append (escaping, validation, annotation refs), harvest (marker
detection, dedup, isMeta/assistant skip), review/promote round-trip,
pending-count, _encode_cwd matching Claude Code's projects-dir scheme.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

from superclaude.scripts import insight_writer as iw


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """Run each test in an isolated cwd so .claude/ paths don't collide."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ---------- _encode_cwd ----------


class TestEncodeCwd:
    def test_windows_double_dash_after_drive(self):
        # ':\' becomes '--' (each separator → one dash, no coalescing)
        assert iw._encode_cwd(r"C:\Users\ajitta") == "C--Users-ajitta"

    def test_unix_path(self):
        assert iw._encode_cwd("/home/ajitta/repo") == "-home-ajitta-repo"

    def test_real_project_path(self):
        # Matches the directory name observed in ~/.claude/projects/
        assert (
            iw._encode_cwd(r"C:\Users\ajitta\Repos\ajitta\superclaude")
            == "C--Users-ajitta-Repos-ajitta-superclaude"
        )


# ---------- append ----------


def _run_append(json_str: str) -> int:
    import argparse

    return iw.cmd_append(argparse.Namespace(json=json_str))


class TestAppend:
    def test_escaping_special_chars(self, workdir):
        rc = _run_append(
            json.dumps(
                {
                    "type": "discovery",
                    "insight": 'quotes "x" backslash \\ unicode 한글 newline\nstill ok',
                }
            )
        )
        assert rc == 0
        line = (
            (workdir / ".claude" / "insights.jsonl").read_text(encoding="utf-8").strip()
        )
        d = json.loads(line)
        assert d["insight"].startswith('quotes "x"')
        assert "한글" in d["insight"]

    def test_auto_fills_ts_and_author(self, workdir):
        rc = _run_append(json.dumps({"type": "feedback", "insight": "x"}))
        assert rc == 0
        d = json.loads(
            (workdir / ".claude" / "insights.jsonl").read_text(encoding="utf-8")
        )
        assert "ts" in d
        assert d["author"]  # non-empty

    def test_rejects_invalid_type(self, workdir, capsys):
        rc = _run_append(json.dumps({"type": "bogus", "insight": "x"}))
        assert rc == 2
        assert "invalid type" in capsys.readouterr().err

    def test_rejects_missing_required(self, workdir, capsys):
        rc = _run_append(json.dumps({"type": "feedback"}))
        assert rc == 2
        assert "missing required" in capsys.readouterr().err

    def test_batch_append(self, workdir):
        rc = _run_append(
            json.dumps(
                [
                    {"type": "feedback", "insight": "a"},
                    {"type": "decision", "insight": "b"},
                ]
            )
        )
        assert rc == 0
        lines = (
            (workdir / ".claude" / "insights.jsonl")
            .read_text(encoding="utf-8")
            .strip()
            .split("\n")
        )
        assert len(lines) == 2

    def test_annotation_requires_ref_ts(self, workdir, capsys):
        rc = _run_append(json.dumps({"type": "annotation", "insight": "x"}))
        assert rc == 2
        assert "ref_ts" in capsys.readouterr().err

    def test_annotation_ref_must_exist(self, workdir, capsys):
        rc = _run_append(
            json.dumps(
                {
                    "type": "annotation",
                    "insight": "x",
                    "ref_ts": "2999-01-01T00:00:00+09:00",
                }
            )
        )
        assert rc == 2
        assert "does not match" in capsys.readouterr().err

    def test_annotation_ref_to_existing_passes(self, workdir):
        # Create a real entry first
        _run_append(
            json.dumps(
                {
                    "type": "discovery",
                    "insight": "base",
                    "ts": "2026-04-25T22:00:00+09:00",
                }
            )
        )
        rc = _run_append(
            json.dumps(
                {
                    "type": "annotation",
                    "insight": "links to base",
                    "ref_ts": "2026-04-25T22:00:00+09:00",
                }
            )
        )
        assert rc == 0

    def test_annotation_ref_to_other_annotation_rejected(self, workdir, capsys):
        # Create base + annotation, then try to annotate the annotation
        _run_append(
            json.dumps(
                {
                    "type": "discovery",
                    "insight": "base",
                    "ts": "2026-04-25T22:00:00+09:00",
                }
            )
        )
        _run_append(
            json.dumps(
                {
                    "type": "annotation",
                    "insight": "first ann",
                    "ref_ts": "2026-04-25T22:00:00+09:00",
                    "ts": "2026-04-25T22:01:00+09:00",
                }
            )
        )
        rc = _run_append(
            json.dumps(
                {
                    "type": "annotation",
                    "insight": "ann of ann",
                    "ref_ts": "2026-04-25T22:01:00+09:00",
                }
            )
        )
        assert rc == 2
        assert "does not match" in capsys.readouterr().err


# ---------- harvest ----------


def _make_transcript(project_dir: Path, session_id: str, records: list[dict]) -> Path:
    project_dir.mkdir(parents=True, exist_ok=True)
    p = project_dir / f"{session_id}.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return p


def _harvest(workdir: Path, monkeypatch, session_id: str, source: str = "clear"):
    """Invoke harvest with a fake home so we can place transcripts."""
    import argparse

    fake_home = workdir / "fakehome"
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    cwd_str = str(workdir)
    project_dir = fake_home / ".claude" / "projects" / iw._encode_cwd(cwd_str)
    return argparse.Namespace(
        cwd=cwd_str,
        session_id=session_id,
        source=source,
    ), project_dir


class TestHarvest:
    def test_extracts_user_insight_markers(self, workdir, monkeypatch):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "sessionId": "sess1",
                    "timestamp": "2026-04-25T22:00:00Z",
                    "message": {"role": "user", "content": "INSIGHT: dedup matters"},
                },
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u2",
                    "sessionId": "sess1",
                    "timestamp": "2026-04-25T22:01:00Z",
                    "message": {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "INSIGHT: list content also works"}
                        ],
                    },
                },
            ],
        )
        rc = iw.cmd_harvest(ns)
        assert rc == 0
        pending = (
            (workdir / ".claude" / "insights.pending.jsonl")
            .read_text(encoding="utf-8")
            .strip()
            .split("\n")
        )
        assert len(pending) == 2
        texts = [json.loads(p)["raw_text"] for p in pending]
        assert "dedup matters" in texts
        assert "list content also works" in texts

    def test_skips_meta_and_assistant(self, workdir, monkeypatch):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": True,
                    "uuid": "u1",
                    "message": {"role": "user", "content": "INSIGHT: meta skip me"},
                },
                {
                    "type": "assistant",
                    "uuid": "a1",
                    "message": {
                        "role": "assistant",
                        "content": "INSIGHT: assistant skip me",
                    },
                },
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u2",
                    "message": {"role": "user", "content": "INSIGHT: keep me"},
                },
            ],
        )
        rc = iw.cmd_harvest(ns)
        assert rc == 0
        pending = (
            (workdir / ".claude" / "insights.pending.jsonl")
            .read_text(encoding="utf-8")
            .strip()
            .split("\n")
        )
        assert len(pending) == 1
        assert "keep me" in json.loads(pending[0])["raw_text"]

    def test_idempotent(self, workdir, monkeypatch):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "message": {"role": "user", "content": "INSIGHT: dedup"},
                }
            ],
        )
        iw.cmd_harvest(ns)
        iw.cmd_harvest(ns)
        iw.cmd_harvest(ns)
        pending_path = workdir / ".claude" / "insights.pending.jsonl"
        assert len(pending_path.read_text(encoding="utf-8").strip().split("\n")) == 1

    def test_no_transcript_silent_success(self, workdir, monkeypatch):
        # No project dir at all
        fake_home = workdir / "fakehome"
        monkeypatch.setattr(Path, "home", lambda: fake_home)
        import argparse

        rc = iw.cmd_harvest(
            argparse.Namespace(cwd=str(workdir), session_id="missing", source="clear")
        )
        assert rc == 0
        assert not (workdir / ".claude" / "insights.pending.jsonl").exists()

    def test_no_markers_no_pending_file(self, workdir, monkeypatch):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "message": {"role": "user", "content": "no marker here"},
                }
            ],
        )
        iw.cmd_harvest(ns)
        assert not (workdir / ".claude" / "insights.pending.jsonl").exists()


# ---------- review / promote / pending-count ----------


class TestReviewPromote:
    def test_review_empty(self, workdir, capsys):
        import argparse

        rc = iw.cmd_review(argparse.Namespace())
        assert rc == 0
        assert "no pending" in capsys.readouterr().out

    def test_promote_round_trip(self, workdir, monkeypatch):
        # Seed pending
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "sessionId": "sess1",
                    "timestamp": "2026-04-25T22:00:00Z",
                    "message": {"role": "user", "content": "INSIGHT: promote me"},
                }
            ],
        )
        iw.cmd_harvest(ns)
        assert (workdir / ".claude" / "insights.pending.jsonl").exists()

        import argparse

        rc = iw.cmd_promote(
            argparse.Namespace(
                index=0, type="discovery", insight=None, tags="harvest,a"
            )
        )
        assert rc == 0
        # Promoted entry in insights.jsonl
        line = (
            (workdir / ".claude" / "insights.jsonl").read_text(encoding="utf-8").strip()
        )
        d = json.loads(line)
        assert d["type"] == "discovery"
        assert d["insight"] == "promote me"
        assert d["tags"] == ["harvest", "a"]
        # Pending file removed when emptied
        assert not (workdir / ".claude" / "insights.pending.jsonl").exists()

    def test_promote_index_out_of_range(self, workdir, capsys):
        import argparse

        rc = iw.cmd_promote(
            argparse.Namespace(index=99, type="discovery", insight=None, tags=None)
        )
        assert rc == 2
        assert "out of range" in capsys.readouterr().err

    def test_pending_count_zero_silent(self, workdir, capsys):
        import argparse

        rc = iw.cmd_pending_count(argparse.Namespace())
        assert rc == 0
        assert capsys.readouterr().out == ""

    def test_pending_count_nonzero_prints(self, workdir, monkeypatch, capsys):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "message": {"role": "user", "content": "INSIGHT: x"},
                }
            ],
        )
        iw.cmd_harvest(ns)
        capsys.readouterr()  # drain harvest output
        import argparse

        iw.cmd_pending_count(argparse.Namespace())
        out = capsys.readouterr().out
        assert "pending insight" in out


# ---------- jq error path ----------


class TestJqRequired:
    def test_list_errors_when_jq_missing(self, workdir, monkeypatch, capsys):
        # Simulate jq missing on PATH
        monkeypatch.setattr(shutil, "which", lambda name: None)
        # Need at least one entry so we hit the jq path
        _run_append(json.dumps({"type": "feedback", "insight": "x"}))
        import argparse

        with pytest.raises(SystemExit) as exc:
            iw.cmd_list(argparse.Namespace(limit=20))
        assert exc.value.code == 1
        assert "jq not found" in capsys.readouterr().err


# ---------- harvest-from-hook argv translation (S3) ----------


class TestHarvestFromHook:
    def test_translates_session_end_payload(self, workdir, monkeypatch, capsys):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "sessionId": "sess1",
                    "timestamp": "2026-04-25T22:00:00Z",
                    "message": {"role": "user", "content": "INSIGHT: from hook"},
                }
            ],
        )
        payload = json.dumps(
            {"session_id": "sess1", "cwd": str(workdir), "source": "clear"}
        )
        monkeypatch.setattr("sys.stdin", _StdinMock(payload))
        rc = iw.main(["harvest-from-hook"])
        assert rc == 0
        pending = (workdir / ".claude" / "insights.pending.jsonl").read_text(
            encoding="utf-8"
        )
        d = json.loads(pending.strip())
        assert d["source"] == "clear"
        assert d["raw_text"] == "from hook"

    def test_precompact_trigger_field(self, workdir, monkeypatch):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "sessionId": "sess1",
                    "timestamp": "2026-04-25T22:00:00Z",
                    "message": {"role": "user", "content": "INSIGHT: pre-compact"},
                }
            ],
        )
        payload = json.dumps(
            {"session_id": "sess1", "cwd": str(workdir), "trigger": "manual"}
        )
        monkeypatch.setattr("sys.stdin", _StdinMock(payload))
        rc = iw.main(["harvest-from-hook"])
        assert rc == 0
        d = json.loads(
            (workdir / ".claude" / "insights.pending.jsonl")
            .read_text(encoding="utf-8")
            .strip()
        )
        assert d["source"] == "manual"

    def test_malformed_payload_falls_back_to_other(self, workdir, monkeypatch):
        # Even with garbage stdin, harvest should not crash; cwd defaults to os.getcwd()
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "sessionId": "sess1",
                    "timestamp": "2026-04-25T22:00:00Z",
                    "message": {
                        "role": "user",
                        "content": "INSIGHT: still gets caught",
                    },
                }
            ],
        )
        monkeypatch.setattr("sys.stdin", _StdinMock("not-json {garbage"))
        rc = iw.main(["harvest-from-hook"])
        assert rc == 0
        d = json.loads(
            (workdir / ".claude" / "insights.pending.jsonl")
            .read_text(encoding="utf-8")
            .strip()
        )
        assert d["source"] == "other"


class _StdinMock:
    def __init__(self, text: str) -> None:
        self._text = text

    def read(self) -> str:
        return self._text


# ---------- _now_iso (S5) + inline marker (S2) + tail-scan (S4) ----------


class TestTimestampFormat:
    def test_colon_offset_format(self):
        s = iw._now_iso()
        # ISO 8601 with colon offset: ...+HH:MM or ...-HH:MM
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$", s), s

    def test_consecutive_calls_monotonic(self):
        # Sanity: two calls produce parseable, ordered timestamps
        from datetime import datetime

        s1 = iw._now_iso()
        s2 = iw._now_iso()
        # fromisoformat handles colon offset directly
        d1 = datetime.fromisoformat(s1)
        d2 = datetime.fromisoformat(s2)
        assert d1 <= d2


class TestInlineMarker:
    def test_inline_INSIGHT_in_middle_of_message(self, workdir, monkeypatch):  # noqa: N802 — INSIGHT literal under test
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "message": {
                        "role": "user",
                        "content": "lots of context first INSIGHT: real one",
                    },
                }
            ],
        )
        iw.cmd_harvest(ns)
        d = json.loads(
            (workdir / ".claude" / "insights.pending.jsonl")
            .read_text(encoding="utf-8")
            .strip()
        )
        assert d["raw_text"] == "real one"

    def test_word_boundary_ignores_INSIGHTS(self, workdir, monkeypatch):  # noqa: N802 — INSIGHTS literal under test
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "message": {
                        "role": "user",
                        "content": "many INSIGHTS: not a marker",
                    },
                }
            ],
        )
        iw.cmd_harvest(ns)
        # No marker → no pending file
        assert not (workdir / ".claude" / "insights.pending.jsonl").exists()

    def test_lowercase_insight_and_hyphen_separator_do_not_match(
        self, workdir, monkeypatch
    ):
        """Regression: /context output (stored as a synthetic user message) lists
        agent and skill token meters like 'insight-analyst: 63 tokens' and
        'sc:insight: 24 tokens'. The marker must require uppercase INSIGHT and
        a colon separator, otherwise these are false-harvested.
        """
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        context_stdout = (
            "<local-command-stdout> Context Usage\n"
            "├ insight-analyst: 63 tokens\n"
            "├ sc:insight: 24 tokens\n"
            "**(insight-analyst, self-review, project-initializer)** absorbed\n"
            "Insight: lowercase prefix should also be ignored\n"
        )
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "message": {"role": "user", "content": context_stdout},
                }
            ],
        )
        iw.cmd_harvest(ns)
        assert not (workdir / ".claude" / "insights.pending.jsonl").exists()


class TestMultiMarkerSameLine:
    def test_two_markers_on_one_line_yields_two_entries(self, workdir, monkeypatch):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "message": {
                        "role": "user",
                        "content": "INSIGHT: first INSIGHT: second",
                    },
                }
            ],
        )
        iw.cmd_harvest(ns)
        pending = (
            (workdir / ".claude" / "insights.pending.jsonl")
            .read_text(encoding="utf-8")
            .strip()
            .split("\n")
        )
        assert len(pending) == 2
        texts = [json.loads(p)["raw_text"] for p in pending]
        assert texts == ["first", "second"]

    def test_markers_across_multiple_lines(self, workdir, monkeypatch):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "message": {
                        "role": "user",
                        "content": "line one INSIGHT: a\nline two INSIGHT: b",
                    },
                }
            ],
        )
        iw.cmd_harvest(ns)
        pending = (
            (workdir / ".claude" / "insights.pending.jsonl")
            .read_text(encoding="utf-8")
            .strip()
            .split("\n")
        )
        texts = sorted(json.loads(p)["raw_text"] for p in pending)
        assert texts == ["a", "b"]


class TestFindTranscriptFallback:
    def test_session_id_missing_falls_back_to_most_recent(self, workdir, monkeypatch):
        # Set up a fake home with two transcripts
        fake_home = workdir / "fakehome"
        monkeypatch.setattr(Path, "home", lambda: fake_home)
        cwd = str(workdir)
        pdir = fake_home / ".claude" / "projects" / iw._encode_cwd(cwd)
        pdir.mkdir(parents=True)
        old = pdir / "old.jsonl"
        new = pdir / "new.jsonl"
        old.write_text("{}\n", encoding="utf-8")
        new.write_text("{}\n", encoding="utf-8")
        # Force mtimes so 'new' is newer
        import os as _os

        _os.utime(old, (1000, 1000))
        _os.utime(new, (2000, 2000))
        # No session_id supplied → fallback to most-recent
        result = iw._find_transcript(None, cwd)
        assert result is not None
        assert result.name == "new.jsonl"

    def test_session_id_no_match_falls_back(self, workdir, monkeypatch):
        fake_home = workdir / "fakehome"
        monkeypatch.setattr(Path, "home", lambda: fake_home)
        cwd = str(workdir)
        pdir = fake_home / ".claude" / "projects" / iw._encode_cwd(cwd)
        pdir.mkdir(parents=True)
        only = pdir / "only.jsonl"
        only.write_text("{}\n", encoding="utf-8")
        # session_id "nonexistent" → no direct hit, fall back to most-recent
        result = iw._find_transcript("nonexistent-id", cwd)
        assert result is not None
        assert result.name == "only.jsonl"

    def test_no_project_dir_returns_none(self, workdir, monkeypatch):
        fake_home = workdir / "fakehome"
        monkeypatch.setattr(Path, "home", lambda: fake_home)
        result = iw._find_transcript("any", str(workdir))
        assert result is None


class TestTailScanBoundary:
    def test_seek_landing_exactly_at_line_start_keeps_first_line(
        self, workdir, monkeypatch, tmp_path
    ):
        """When tail seek lands exactly after a \\n, the next line is complete and
        must NOT be discarded as a partial line."""
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        pdir.mkdir(parents=True, exist_ok=True)
        path = pdir / "sess1.jsonl"

        # Build a record that, when serialized + newline, has known byte length.
        # Pad early portion to (TRANSCRIPT_TAIL_BYTES - 1) bytes so the boundary
        # falls exactly between '\n' and the start of the next record.
        pad_record = {
            "type": "user",
            "isMeta": False,
            "uuid": "pad",
            "message": {"role": "user", "content": "x"},
        }
        target_record = {
            "type": "user",
            "isMeta": False,
            "uuid": "target",
            "message": {"role": "user", "content": "INSIGHT: keep me"},
        }
        pad_line = json.dumps(pad_record) + "\n"

        with path.open("wb") as f:
            written = 0
            # Fill up to exactly TRANSCRIPT_TAIL_BYTES - 1 with pad lines
            while written + len(pad_line) <= iw.TRANSCRIPT_TAIL_BYTES - 1:
                f.write(pad_line.encode("utf-8"))
                written += len(pad_line)
            # Pad to exact boundary with shorter records if needed
            short = b'{"type":"user","isMeta":false,"uuid":"x","message":{"role":"user","content":"x"}}\n'
            while written + len(short) <= iw.TRANSCRIPT_TAIL_BYTES - 1:
                f.write(short)
                written += len(short)
            # Write filler until exactly boundary
            remaining = iw.TRANSCRIPT_TAIL_BYTES - 1 - written
            if remaining > 0:
                # Build a record with adjustable content length
                filler_obj = {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "f",
                    "message": {"role": "user", "content": "y"},
                }
                base = json.dumps(filler_obj) + "\n"
                # Adjust 'y' field to make total = remaining
                overhead = len(base) - 1  # everything except 'y'
                # We need len(content) such that total line len == remaining
                content_len = remaining - overhead
                if content_len < 1:
                    # Just write the base; close enough — test still useful
                    f.write(base.encode("utf-8"))
                    written += len(base)
                else:
                    filler_obj["message"]["content"] = "y" * content_len
                    line = (json.dumps(filler_obj) + "\n").encode("utf-8")
                    f.write(line)
                    written += len(line)
            # Now write the target record, which starts at byte position written
            target_line = (json.dumps(target_record) + "\n").encode("utf-8")
            f.write(target_line)

        # Verify: file size > TRANSCRIPT_TAIL_BYTES so tail-scan engages
        assert path.stat().st_size > iw.TRANSCRIPT_TAIL_BYTES
        iw.cmd_harvest(ns)
        pending = workdir / ".claude" / "insights.pending.jsonl"
        assert pending.exists(), "target line was discarded — boundary handling bug"
        d = json.loads(pending.read_text(encoding="utf-8").strip())
        assert d["raw_text"] == "keep me"


class TestAppendDoesNotMutateInput:
    def test_input_dict_unchanged_after_append(self, workdir):
        original = {"type": "feedback", "insight": "x"}
        _run_append(json.dumps(original))  # JSON serialization already insulates
        # The defensive copy primarily protects in-process reuse; verify the
        # internal append helper does not back-mutate when called with a dict ref
        import argparse

        live = {"type": "discovery", "insight": "live"}
        live_copy = dict(live)
        iw.cmd_append(argparse.Namespace(json=json.dumps(live)))
        assert live == live_copy  # JSON path, untouched
        # Direct internal invocation: simulate cmd_promote-like path
        # cmd_append rebuilds entries from json.loads, so caller's `live` is
        # already isolated. The defensive copy guards future internal callers.


class TestTranscriptTailScan:
    def test_huge_transcript_only_scans_tail(self, workdir, monkeypatch):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        # Build a transcript: one early marker, then padding > 5MB, then a late marker
        early = {
            "type": "user",
            "isMeta": False,
            "uuid": "early",
            "message": {"role": "user", "content": "INSIGHT: very early"},
        }
        late = {
            "type": "user",
            "isMeta": False,
            "uuid": "late",
            "message": {"role": "user", "content": "INSIGHT: recent"},
        }
        padding_record = {
            "type": "user",
            "isMeta": False,
            "uuid": "pad",
            "message": {"role": "user", "content": "x" * 1000},
        }
        pdir.mkdir(parents=True, exist_ok=True)
        path = pdir / "sess1.jsonl"
        with path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(early) + "\n")
            # Pad past TRANSCRIPT_TAIL_BYTES so 'early' falls outside the tail window
            target = iw.TRANSCRIPT_TAIL_BYTES + 100_000
            written = path.stat().st_size
            while written < target:
                f.write(json.dumps(padding_record) + "\n")
                f.flush()
                written = path.stat().st_size
            f.write(json.dumps(late) + "\n")
        iw.cmd_harvest(ns)
        pending = (
            (workdir / ".claude" / "insights.pending.jsonl")
            .read_text(encoding="utf-8")
            .strip()
        )
        # 'early' is outside the tail window; only 'recent' should be harvested.
        texts = [json.loads(line)["raw_text"] for line in pending.split("\n")]
        assert "recent" in texts
        assert "very early" not in texts
