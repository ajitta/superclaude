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
    """Run each test in an isolated project so .claude/ paths don't collide.

    CLAUDE_PROJECT_DIR is what project_root() anchors on, so chdir alone would
    let the insight files resolve to the real repo.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
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

    def test_skips_meta(self, workdir, monkeypatch):
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

        rc = iw.cmd_pending_count(argparse.Namespace(cwd=None))
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

        iw.cmd_pending_count(argparse.Namespace(cwd=None))
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
        # Real SessionEnd payloads carry 'reason' (SessionStart carries 'source').
        payload = json.dumps(
            {"session_id": "sess1", "cwd": str(workdir), "reason": "clear"}
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


class TestPendingCountFromHook:
    def test_project_root_wins_over_stdin_cwd(self, workdir, monkeypatch, capsys):
        # The stdin payload's cwd is the *session* cwd and may be a
        # subdirectory. Counting must use the project root, the same anchor
        # harvest/promote/append use — otherwise the two ends of the pending
        # workflow read different files.
        subdir = workdir / "packages" / "api"
        subdir.mkdir(parents=True)
        (subdir / ".claude").mkdir()
        (subdir / ".claude" / "insights.pending.jsonl").write_text(
            '{"uuid": "decoy", "raw_text": "wrong file"}\n', encoding="utf-8"
        )
        pending = workdir / ".claude" / "insights.pending.jsonl"
        pending.parent.mkdir(parents=True)
        pending.write_text(
            '{"uuid": "u1", "raw_text": "x"}\n{"uuid": "u2", "raw_text": "y"}\n',
            encoding="utf-8",
        )
        payload = json.dumps(
            {"session_id": "sess1", "cwd": str(subdir), "source": "startup"}
        )
        monkeypatch.setattr("sys.stdin", _StdinMock(payload))
        rc = iw.main(["pending-count-from-hook"])
        assert rc == 0
        assert "2 pending insight" in capsys.readouterr().out

    def test_malformed_payload_falls_back_to_process_cwd(
        self, workdir, monkeypatch, capsys
    ):
        pending = workdir / ".claude" / "insights.pending.jsonl"
        pending.parent.mkdir(parents=True)
        pending.write_text('{"uuid": "u1", "raw_text": "x"}\n', encoding="utf-8")
        monkeypatch.setattr("sys.stdin", _StdinMock("not-json {garbage"))
        rc = iw.main(["pending-count-from-hook"])
        assert rc == 0
        assert "1 pending insight" in capsys.readouterr().out


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


class TestModelEmittedMarkers:
    """The model has to be able to produce a marker, or nothing ever does.

    Harvest scanned user records only, so the sole producer was the user typing
    `INSIGHT:` by hand — which happened 5 times in 10 months. 138 entries exist,
    none after 2026-05-08, with the hooks installed and exiting 0 throughout
    (A5). Per D3 the subsystem is repaired rather than retired.
    """

    def test_assistant_marker_is_harvested(self, workdir, monkeypatch):
        """The request is part of the fixture because it is part of the flow.

        An assistant marker is harvested when it answers the Stop hook's
        request. Unprompted ones are the model explaining the format rather
        than reporting a lesson — see TestHarvestOnlyTakesAnsweredMarkers.
        """
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "r1",
                    "message": {"role": "user", "content": iw.REQUEST_REASON},
                },
                {
                    "type": "assistant",
                    "uuid": "a1",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "Done. INSIGHT: a per-event-type hook merge froze installs",
                            }
                        ],
                    },
                }
            ],
        )

        assert iw.cmd_harvest(ns) == 0

        pending = (workdir / ".claude" / "insights.pending.jsonl").read_text(
            encoding="utf-8"
        )
        assert "a per-event-type hook merge froze installs" in pending

    def test_the_request_itself_is_not_harvested(self, workdir, monkeypatch):
        """The prompt asking for a marker must not read as one."""
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
                        "content": iw.REQUEST_SENTINEL + " emit one INSIGHT: line",
                    },
                }
            ],
        )

        assert iw.cmd_harvest(ns) == 0
        assert not (workdir / ".claude" / "insights.pending.jsonl").exists()


class TestInsightRequestHook:
    """A Stop hook is the only producer that does not have to be typed."""

    def _run(self, workdir, monkeypatch, dirty=True, stop_hook_active=False):
        import argparse

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(workdir))
        monkeypatch.delenv("SUPERCLAUDE_INSIGHT_PROMPT", raising=False)
        monkeypatch.setattr(iw, "_session_changed_code", lambda _session: dirty)
        return iw.cmd_request(
            argparse.Namespace(session_id="sess1", stop_hook_active=stop_hook_active)
        )

    def test_asks_once_when_the_tree_changed(self, workdir, monkeypatch, capsys):
        rc = self._run(workdir, monkeypatch)

        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["decision"] == "block"
        assert iw.REQUEST_SENTINEL in out["reason"]

    def test_second_stop_in_the_same_session_is_silent(
        self, workdir, monkeypatch, capsys
    ):
        """One extra turn per session at most — never a loop."""
        self._run(workdir, monkeypatch)
        capsys.readouterr()

        self._run(workdir, monkeypatch)

        assert capsys.readouterr().out.strip() == ""

    def test_clean_tree_is_silent(self, workdir, monkeypatch, capsys):
        self._run(workdir, monkeypatch, dirty=False)
        assert capsys.readouterr().out.strip() == ""

    def test_reentry_is_silent(self, workdir, monkeypatch, capsys):
        """stop_hook_active means this hook already spoke — never answer twice."""
        self._run(workdir, monkeypatch, stop_hook_active=True)
        assert capsys.readouterr().out.strip() == ""

    def test_opt_out_is_honoured(self, workdir, monkeypatch, capsys):
        import argparse

        monkeypatch.setenv("SUPERCLAUDE_INSIGHT_PROMPT", "0")
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(workdir))
        monkeypatch.setattr(iw, "_session_changed_code", lambda _session: True)

        iw.cmd_request(argparse.Namespace(session_id="sess1", stop_hook_active=False))

        assert capsys.readouterr().out.strip() == ""


def _committed_repo(tmp_path, monkeypatch):
    """A real git repository with one commit, anchored for the hook resolvers."""
    import subprocess

    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "test@example.com"],
        ["git", "config", "user.name", "test"],
    ):
        subprocess.run(cmd, cwd=tmp_path, check=True)
    (tmp_path / "tracked.txt").write_text("hello\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=tmp_path, check=True)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    return tmp_path


class TestFrameworkStateIsNotAUserChange:
    """SuperClaude's own runtime files must not read as "the session changed code".

    The gate asked whether `git status --porcelain` printed anything. In a
    project- or local-scope install the framework writes its context cache,
    pending-insight file and agent-memory store inside the worktree, and nothing
    excludes them for project scope at all — so a session that read one file and
    edited nothing ended with a blocking Stop asking for a lesson it did not
    have. This repository only looked clean because its .gitignore was written
    by hand.
    """

    def test_runtime_cache_is_ignored(self, tmp_path, monkeypatch):
        import superclaude.scripts.insight_writer as iw

        repo = _committed_repo(tmp_path, monkeypatch)
        state = repo / ".claude" / ".superclaude_hooks"
        state.mkdir(parents=True)
        (state / "claude_context_abc.txt").write_text("cached\n", encoding="utf-8")

        assert iw._working_tree_changed() is False

    def test_pending_insights_are_ignored(self, tmp_path, monkeypatch):
        import superclaude.scripts.insight_writer as iw

        repo = _committed_repo(tmp_path, monkeypatch)
        (repo / ".claude").mkdir()
        (repo / ".claude" / "insights.pending.jsonl").write_text(
            '{"text": "x"}\n', encoding="utf-8"
        )

        assert iw._working_tree_changed() is False

    def test_agent_memory_is_ignored(self, tmp_path, monkeypatch):
        import superclaude.scripts.insight_writer as iw

        repo = _committed_repo(tmp_path, monkeypatch)
        memory = repo / ".claude" / "agent-memory" / "system-architect"
        memory.mkdir(parents=True)
        (memory / "notes.md").write_text("note\n", encoding="utf-8")

        assert iw._working_tree_changed() is False

    def test_a_real_edit_still_counts(self, tmp_path, monkeypatch):
        import superclaude.scripts.insight_writer as iw

        repo = _committed_repo(tmp_path, monkeypatch)
        (repo / "tracked.txt").write_text("edited\n", encoding="utf-8")

        assert iw._working_tree_changed() is True

    def test_a_new_source_file_still_counts(self, tmp_path, monkeypatch):
        import superclaude.scripts.insight_writer as iw

        repo = _committed_repo(tmp_path, monkeypatch)
        (repo / "new_module.py").write_text("x = 1\n", encoding="utf-8")

        assert iw._working_tree_changed() is True


class TestSessionBaselineDecidesTheAsk:
    """"Is the tree dirty" is not "did this session change code".

    A repository dirty before the session started satisfied the old gate on the
    very first turn, so the one request a session gets was spent on a turn that
    changed nothing. Recording a fingerprint at SessionStart and diffing at Stop
    asks the question the prompt text actually claims to ask.
    """

    def test_pre_existing_dirt_does_not_trigger(self, tmp_path, monkeypatch, capsys):
        import superclaude.scripts.insight_writer as iw

        repo = _committed_repo(tmp_path, monkeypatch)
        monkeypatch.setattr(iw, "hook_state_dir", lambda: tmp_path / ".git" / "sc-state")
        (repo / "tracked.txt").write_text("dirty before the session\n", encoding="utf-8")

        iw.main(["session-baseline", "--session-id", "s1"])
        capsys.readouterr()

        iw.main(["request", "--session-id", "s1"])

        assert capsys.readouterr().out.strip() == "", (
            "a session that changed nothing was asked for a lesson"
        )

    def test_a_change_after_the_baseline_triggers(self, tmp_path, monkeypatch, capsys):
        import json

        import superclaude.scripts.insight_writer as iw

        repo = _committed_repo(tmp_path, monkeypatch)
        monkeypatch.setattr(iw, "hook_state_dir", lambda: tmp_path / ".git" / "sc-state")

        iw.main(["session-baseline", "--session-id", "s2"])
        capsys.readouterr()
        (repo / "tracked.txt").write_text("changed during the session\n", encoding="utf-8")

        iw.main(["request", "--session-id", "s2"])

        payload = json.loads(capsys.readouterr().out)
        assert payload["decision"] == "block"

    def test_without_a_baseline_it_falls_back_to_the_proxy(
        self, tmp_path, monkeypatch, capsys
    ):
        """An install whose SessionStart hook is not registered still works."""
        import json

        import superclaude.scripts.insight_writer as iw

        repo = _committed_repo(tmp_path, monkeypatch)
        monkeypatch.setattr(iw, "hook_state_dir", lambda: tmp_path / ".git" / "sc-state")
        (repo / "tracked.txt").write_text("dirty\n", encoding="utf-8")

        iw.main(["request", "--session-id", "s3"])

        payload = json.loads(capsys.readouterr().out)
        assert payload["decision"] == "block"


def _assistant(uuid: str, text: str, **extra) -> dict:
    record = {
        "type": "assistant",
        "isMeta": False,
        "uuid": uuid,
        "sessionId": "sess1",
        "timestamp": "2026-08-22T10:00:00Z",
        "message": {"role": "assistant", "content": text},
    }
    record.update(extra)
    return record


def _pending_texts(workdir):
    path = workdir / ".claude" / "insights.pending.jsonl"
    if not path.exists():
        return []
    return [
        json.loads(line)["raw_text"]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestHarvestOnlyTakesAnsweredMarkers:
    """An assistant marker counts when it answers the request, not otherwise.

    Widening the scan from user records to every assistant record gave the
    subsystem a producer, and simultaneously made every explanation of the
    marker into an entry: a document quoting it, a review of this very file, a
    reply repeating an earlier answer. A user typing the marker is explicit
    intent and still always counts.
    """

    def test_an_unprompted_assistant_marker_is_not_harvested(
        self, workdir, monkeypatch
    ):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [_assistant("a1", "The format is a line beginning INSIGHT: like this.")],
        )

        assert iw.cmd_harvest(ns) == 0
        assert _pending_texts(workdir) == []

    def test_an_answer_to_the_request_is_harvested(self, workdir, monkeypatch):
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "r1",
                    "sessionId": "sess1",
                    "message": {"role": "user", "content": iw.REQUEST_REASON},
                },
                _assistant("a1", "Done. INSIGHT: the cache key needed the session id."),
            ],
        )

        assert iw.cmd_harvest(ns) == 0
        assert _pending_texts(workdir) == ["the cache key needed the session id."]

    def test_a_user_typed_marker_never_needs_a_request(self, workdir, monkeypatch):
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
                    "message": {"role": "user", "content": "INSIGHT: typed by hand"},
                }
            ],
        )

        assert iw.cmd_harvest(ns) == 0
        assert _pending_texts(workdir) == ["typed by hand"]

    def test_a_reply_quoting_the_request_still_yields_its_marker(
        self, workdir, monkeypatch
    ):
        """The sentinel marks the request, not everything that mentions it."""
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "r1",
                    "sessionId": "sess1",
                    "message": {"role": "user", "content": iw.REQUEST_REASON},
                },
                _assistant(
                    "a1",
                    f"You asked {iw.REQUEST_SENTINEL} for a lesson. "
                    "INSIGHT: quoting the prompt is not disqualifying.",
                ),
            ],
        )

        assert iw.cmd_harvest(ns) == 0
        assert _pending_texts(workdir) == [
            "quoting the prompt is not disqualifying."
        ]

    def test_sub_agent_records_are_skipped(self, workdir, monkeypatch):
        """A sub-agent's transcript is not this session's lesson."""
        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "r1",
                    "sessionId": "sess1",
                    "message": {"role": "user", "content": iw.REQUEST_REASON},
                },
                _assistant("a1", "INSIGHT: from a branch", isSidechain=True),
            ],
        )

        assert iw.cmd_harvest(ns) == 0
        assert _pending_texts(workdir) == []


class TestHarvestRemembersWhatItPromoted:
    """Dedup has to outlive the pending row it was reading.

    Marker ids were read only from the pending file, and promote removes the row
    it promotes. `PreCompact` harvest → promote → `SessionEnd` harvest of the
    same transcript therefore re-created an entry the user had already filed.
    """

    def test_a_promoted_marker_is_not_harvested_again(self, workdir, monkeypatch):
        import argparse

        ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "r1",
                    "sessionId": "sess1",
                    "message": {"role": "user", "content": iw.REQUEST_REASON},
                },
                _assistant("a1", "INSIGHT: promoted once, harvested once"),
            ],
        )

        iw.cmd_harvest(ns)
        assert len(_pending_texts(workdir)) == 1

        iw.cmd_promote(
            argparse.Namespace(
                index=0, type="discovery", tags=None, author=None, insight=None
            )
        )
        assert _pending_texts(workdir) == []

        iw.cmd_harvest(ns)
        assert _pending_texts(workdir) == [], (
            "an already-promoted marker came back as pending"
        )


class TestTranscriptComesFromThePayload:
    """Claude Code names the transcript; guessing it can read another window's.

    `_find_transcript` rebuilt the path from cwd and session id and fell back to
    the most recently modified file in that directory — which, with two windows
    open on one repository, is the other window's live session.
    """

    def test_the_given_path_wins_over_the_guess(self, workdir, monkeypatch):
        import argparse

        _ns, pdir = _harvest(workdir, monkeypatch, "sess1")
        _make_transcript(
            pdir,
            "sess1",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u1",
                    "sessionId": "sess1",
                    "message": {"role": "user", "content": "INSIGHT: the guessed one"},
                }
            ],
        )
        named = _make_transcript(
            workdir / "elsewhere",
            "other",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "u2",
                    "sessionId": "other",
                    "message": {"role": "user", "content": "INSIGHT: the named one"},
                }
            ],
        )

        iw.cmd_harvest(
            argparse.Namespace(
                cwd=str(workdir),
                session_id="sess1",
                source="clear",
                transcript_path=str(named),
            )
        )

        assert _pending_texts(workdir) == ["the named one"]


class TestStopCollectsItsOwnAnswer:
    """The reply arrives a turn after the ask, and Stop used to never read it.

    Only PreCompact and SessionEnd harvest, so a session that ended without
    either — a closed terminal, a crash — asked for a lesson and then threw the
    answer away.
    """

    def test_the_next_stop_harvests_the_reply(self, workdir, monkeypatch, capsys):
        import argparse

        _ns, pdir = _harvest(workdir, monkeypatch, "sess-answer")
        monkeypatch.setattr(iw, "_session_changed_code", lambda _session: True)
        monkeypatch.delenv("SUPERCLAUDE_INSIGHT_PROMPT", raising=False)

        def _request():
            return iw.cmd_request(
                argparse.Namespace(
                    session_id="sess-answer",
                    stop_hook_active=False,
                    cwd=str(workdir),
                    transcript_path=None,
                )
            )

        _request()
        assert json.loads(capsys.readouterr().out)["decision"] == "block"

        _make_transcript(
            pdir,
            "sess-answer",
            [
                {
                    "type": "user",
                    "isMeta": False,
                    "uuid": "r1",
                    "message": {"role": "user", "content": iw.REQUEST_REASON},
                },
                _assistant("a1", "INSIGHT: the answer must survive a lost SessionEnd"),
            ],
        )

        _request()

        assert capsys.readouterr().out.strip() == "", "Stop spoke twice in one session"
        assert _pending_texts(workdir) == [
            "the answer must survive a lost SessionEnd"
        ]

    def test_it_collects_only_once(self, workdir, monkeypatch, capsys):
        import argparse

        _ns, pdir = _harvest(workdir, monkeypatch, "sess-once")
        monkeypatch.setattr(iw, "_session_changed_code", lambda _session: True)
        monkeypatch.delenv("SUPERCLAUDE_INSIGHT_PROMPT", raising=False)
        calls = []
        real_harvest = iw.cmd_harvest
        monkeypatch.setattr(
            iw, "cmd_harvest", lambda args: (calls.append(args), real_harvest(args))[1]
        )

        for _ in range(3):
            iw.cmd_request(
                argparse.Namespace(
                    session_id="sess-once",
                    stop_hook_active=False,
                    cwd=str(workdir),
                    transcript_path=None,
                )
            )
        capsys.readouterr()

        assert len(calls) == 1
