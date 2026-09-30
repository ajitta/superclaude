"""Tests for the PostToolUse test_runner_hook."""

from __future__ import annotations

import io
import json
import subprocess
import sys

import pytest

from superclaude.scripts import test_runner_hook as hook


def _run_main(monkeypatch, capsys, file_path, completed):
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": file_path}})
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    monkeypatch.setenv("SUPERCLAUDE_AUTO_TEST", "1")
    monkeypatch.setattr(
        hook, "detect_test_command", lambda p: "uv run python -m pytest"
    )
    monkeypatch.setattr(hook.subprocess, "run", lambda *a, **k: completed)
    hook.main()
    out = capsys.readouterr().out.strip()
    return json.loads(out)["systemMessage"] if out else ""


def _completed(rc, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        args="x", returncode=rc, stdout=stdout, stderr=stderr
    )


class TestRunnerUnavailable:
    @pytest.mark.parametrize(
        "output",
        [
            "/p/.venv/bin/python: No module named pytest",
            "ModuleNotFoundError: No module named 'pytest'",
            'npm error Missing script: "test"',
            "make: *** No rule to make target 'test'.  Stop.",
        ],
    )
    def test_detects_missing_runner(self, output):
        assert hook.runner_unavailable(output) is not None

    @pytest.mark.parametrize(
        "output",
        [
            "FAILED tests/test_ops.py::test_add - assert 4 == 5",
            "E   ModuleNotFoundError: No module named 'calc'",
            "",
        ],
    )
    def test_real_failures_are_not_mistaken_for_a_missing_runner(self, output):
        assert hook.runner_unavailable(output) is None


class TestMainMessages:
    def test_missing_pytest_reports_not_run_instead_of_failed(
        self, monkeypatch, capsys, tmp_path
    ):
        msg = _run_main(
            monkeypatch,
            capsys,
            str(tmp_path / "ops.py"),
            _completed(1, stderr="/p/.venv/bin/python: No module named pytest"),
        )

        assert "FAILED" not in msg
        assert "not run" in msg
        assert "pytest" in msg

    def test_real_failure_still_reports_failed(self, monkeypatch, capsys, tmp_path):
        msg = _run_main(
            monkeypatch,
            capsys,
            str(tmp_path / "ops.py"),
            _completed(1, stdout="FAILED tests/test_ops.py::test_add - assert 4 == 5"),
        )

        assert msg.startswith("Tests FAILED")

    def test_pass_reports_passed(self, monkeypatch, capsys, tmp_path):
        msg = _run_main(monkeypatch, capsys, str(tmp_path / "ops.py"), _completed(0))

        assert msg.startswith("Tests passed")
