"""Unit tests for the SuperClaude safety hooks.

Covers the previously-untested safety surface flagged by the 2026-06-05 audit
(MP-TESTCOV / docs/analysis/superclaude-audit-vs-superpowers-ajitta-2026-06-05.md):

  - I1: the destructive-command guard (``destructive_guard.py``), reimplemented
    in Python so it no longer fails open when jq/grep/head are absent.
  - I2: ``loop_guard._save_state`` atomic write (temp file + ``os.replace``).

The scripts are standalone hook entry points (invoked as ``python <script>.py``),
so they are loaded by file path rather than as a package.
"""
from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "src" / "superclaude" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


destructive_guard = _load("destructive_guard")
loop_guard = _load("loop_guard")


class TestDestructiveGuard:
    """I1 — destructive-command blocker (Python rewrite of the shell guard)."""

    @pytest.mark.parametrize(
        "cmd",
        [
            "rm -rf /",
            "rm -rf /  ",
            "rm -rf /*",
            "sudo rm -rf /*",
            "git push --force origin main",
            "git push --force origin master",
        ],
    )
    def test_blocks_destructive(self, cmd):
        assert destructive_guard.is_destructive(cmd) is True

    @pytest.mark.parametrize(
        "cmd",
        [
            "",
            "rm -rf /tmp/build",
            "rm -rf ./dist",
            "git push --force-with-lease origin main",  # safe force-push allowed
            "git push origin main",  # no force
            "git push --force origin feature",  # force but not main/master
            "ls -la",
            "git commit -m 'rm -rf cleanup notes'",
        ],
    )
    def test_allows_safe(self, cmd):
        assert destructive_guard.is_destructive(cmd) is False

    def test_main_blocks_via_stdin(self, monkeypatch, capsys):
        payload = json.dumps({"tool_input": {"command": "rm -rf /"}})
        monkeypatch.setattr("sys.stdin", io.StringIO(payload))
        destructive_guard.main()
        out = json.loads(capsys.readouterr().out)
        assert out["decision"] == "block"
        assert "destructive" in out["reason"]

    def test_main_approves_via_stdin(self, monkeypatch, capsys):
        payload = json.dumps({"tool_input": {"command": "git push origin main"}})
        monkeypatch.setattr("sys.stdin", io.StringIO(payload))
        destructive_guard.main()
        out = json.loads(capsys.readouterr().out)
        assert out["decision"] == "approve"

    def test_main_opt_out(self, monkeypatch, capsys):
        monkeypatch.setenv("SUPERCLAUDE_DESTRUCTIVE_GUARD", "0")
        monkeypatch.setattr(
            "sys.stdin", io.StringIO(json.dumps({"tool_input": {"command": "rm -rf /"}}))
        )
        destructive_guard.main()
        out = json.loads(capsys.readouterr().out)
        assert out["decision"] == "approve"  # disabled -> never blocks

    def test_main_malformed_fails_open(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.stdin", io.StringIO("{ not json"))
        destructive_guard.main()
        out = json.loads(capsys.readouterr().out)
        assert out["decision"] == "approve"


class TestLoopGuardAtomicWrite:
    """I2 — atomic state write stops torn-file corruption under concurrent fan-out."""

    def test_save_load_roundtrip(self, tmp_path):
        p = tmp_path / ".claude" / "loop_guard_state.json"
        state = {"entries": [{"signature": "Bash::x", "ts": 123.0, "kind": "error"}]}
        loop_guard._save_state(p, state)
        assert loop_guard._load_state(p) == state

    def test_no_temp_file_left_behind(self, tmp_path):
        p = tmp_path / "state.json"
        loop_guard._save_state(p, {"entries": []})
        leftovers = list(p.parent.glob(".loop_guard_*"))
        assert leftovers == []

    def test_rewrite_replaces_atomically(self, tmp_path):
        p = tmp_path / "state.json"
        loop_guard._save_state(p, {"entries": [{"signature": "a", "ts": 1.0, "kind": "error"}]})
        loop_guard._save_state(p, {"entries": [{"signature": "b", "ts": 2.0, "kind": "error"}]})
        assert loop_guard._load_state(p)["entries"][0]["signature"] == "b"

    def test_written_file_is_always_valid_json(self, tmp_path):
        p = tmp_path / "state.json"
        loop_guard._save_state(p, {"entries": []})
        # A complete, parseable JSON object is always on disk (never a torn write)
        assert json.loads(p.read_text(encoding="utf-8")) == {"entries": []}

    def test_load_corrupt_fails_open(self, tmp_path):
        p = tmp_path / "state.json"
        p.write_text("{ broken json", encoding="utf-8")
        assert loop_guard._load_state(p) == {"entries": []}
