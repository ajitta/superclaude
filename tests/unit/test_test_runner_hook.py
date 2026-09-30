"""Tests for the PostToolUse test_runner_hook."""

from __future__ import annotations

import io
import json
import shutil
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
        ("output", "reason"),
        [
            ("/p/.venv/bin/python: No module named pytest", "pytest is not installed"),
            ("No module named 'pytest'", "pytest is not installed"),
            ("/bin/sh: 1: uv: not found", "uv is not installed"),
            ("bash: uv: command not found", "uv is not installed"),
            ('npm error Missing script: "test"', "package.json has no test script"),
            ('npm ERR! Missing script: "test"', "package.json has no test script"),
            (
                "make: *** No rule to make target 'test'.  Stop.",
                "the Makefile has no test target",
            ),
            (
                "make: *** No rule to make target `test'.  Stop.",
                "the Makefile has no test target",
            ),
        ],
    )
    def test_detects_missing_runner(self, output, reason):
        assert hook.runner_unavailable(output, 1) == reason

    @pytest.mark.parametrize(
        "output",
        [
            "FAILED tests/test_ops.py::test_add - assert 4 == 5",
            "E   ModuleNotFoundError: No module named 'calc'",
            "E   ModuleNotFoundError: No module named 'pytest_asyncio'",
            "No module named 'pytest_helpers'",
            "make: *** No rule to make target 'test-data.json', needed by 'test'.  Stop.",
            # A real failure whose assertion text quotes the runner message.
            "collected 4 items\n"
            "No module named pytest\n"
            "=========== 1 failed, 3 passed in 0.02s ===========",
            "No module named pytest\n1 failed, 3 passed in 0.02s",
            "",
        ],
    )
    def test_real_failures_are_not_mistaken_for_a_missing_runner(self, output):
        assert hook.runner_unavailable(output, 1) is None

    def test_success_is_never_classified(self):
        assert hook.runner_unavailable("/p/python: No module named pytest", 0) is None

    def test_pytest_exit_5_is_no_tests(self):
        out = "collected 0 items\n\n============ no tests ran in 0.01s ============"
        assert hook.runner_unavailable(out, 5) == "pytest collected no tests"


class TestNpmScriptCheck:
    @pytest.mark.parametrize(
        ("scripts", "expected"),
        [
            (None, False),
            ({}, False),
            ({"test": 'echo "Error: no test specified" && exit 1'}, False),
            ({"test": "jest"}, True),
        ],
    )
    def test_detects_test_script(self, tmp_path, scripts, expected):
        pkg = {"name": "x"} if scripts is None else {"name": "x", "scripts": scripts}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        assert hook._npm_has_test_script(tmp_path / "package.json") is expected

    def test_no_script_means_no_command(self, tmp_path):
        (tmp_path / "package.json").write_text(json.dumps({"name": "x"}))
        (tmp_path / "a.js").write_text("")
        assert hook.detect_test_command(str(tmp_path / "a.js")) is None


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


@pytest.mark.skipif(shutil.which("make") is None, reason="make not installed")
class TestRealMake:
    """End-to-end against the real make binary, not synthetic strings."""

    def _run(self, tmp_path, makefile):
        (tmp_path / "Makefile").write_text(makefile)
        r = subprocess.run(
            ["make", "-C", str(tmp_path), "test"], capture_output=True, text=True
        )
        return hook.runner_unavailable(r.stdout + r.stderr, r.returncode)

    def test_missing_target(self, tmp_path):
        assert (
            self._run(tmp_path, "build:\n\ttrue\n") == "the Makefile has no test target"
        )

    def test_missing_prerequisite_is_a_real_failure(self, tmp_path):
        assert self._run(tmp_path, "test: test-data.json\n\ttrue\n") is None
