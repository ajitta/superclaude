"""Tests for the PostToolUse test_runner_hook."""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from superclaude.scripts import test_runner_hook as hook


def _feed_stdin(monkeypatch, file_path):
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": file_path}})
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    monkeypatch.setenv("SUPERCLAUDE_AUTO_TEST", "1")


def _run_main(monkeypatch, capsys, file_path, completed):
    _feed_stdin(monkeypatch, file_path)
    monkeypatch.setattr(
        hook, "detect_test_command", lambda p: ("uv run python -m pytest", Path("."))
    )
    monkeypatch.setattr(hook, "run_shell", lambda *a, **k: completed)
    hook.main()
    out = capsys.readouterr().out.strip()
    return json.loads(out)["systemMessage"] if out else ""


def _capture_run(monkeypatch):
    """Replace run_shell; return the list of (cmd, kwargs) it received."""
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return _completed(0)

    monkeypatch.setattr(hook, "run_shell", fake_run)
    return calls


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


class TestCommandRunsInDetectedProject:
    """Finding 8: the command must run in the directory whose marker was found,
    not in the hook's own CWD (a monorepo root may have no test script)."""

    def test_npm_subproject(self, monkeypatch, capsys, tmp_path):
        (tmp_path / "package.json").write_text(json.dumps({"name": "root"}))
        api = tmp_path / "packages" / "api"
        (api / "src").mkdir(parents=True)
        (api / "package.json").write_text(
            json.dumps({"name": "api", "scripts": {"test": "jest"}})
        )
        edited = api / "src" / "x.ts"
        edited.write_text("")
        calls = _capture_run(monkeypatch)
        _feed_stdin(monkeypatch, str(edited))

        hook.main()

        assert len(calls) == 1
        cmd, kwargs = calls[0]
        assert cmd == "npm test --silent"
        assert Path(kwargs["cwd"]).resolve() == api.resolve()

    def test_python_subproject(self, monkeypatch, capsys, tmp_path):
        (tmp_path / ".git").mkdir()
        svc = tmp_path / "services" / "worker"
        (svc / "pkg").mkdir(parents=True)
        (svc / "pyproject.toml").write_text("[project]\nname = 'worker'\n")
        edited = svc / "pkg" / "ops.py"
        edited.write_text("")
        calls = _capture_run(monkeypatch)
        _feed_stdin(monkeypatch, str(edited))

        hook.main()

        assert len(calls) == 1
        cmd, kwargs = calls[0]
        assert cmd.startswith("uv run python -m pytest")
        assert Path(kwargs["cwd"]).resolve() == svc.resolve()

    def test_make_subproject(self, monkeypatch, capsys, tmp_path):
        lib = tmp_path / "lib"
        lib.mkdir()
        (lib / "Makefile").write_text("test:\n\ttrue\n")
        edited = lib / "a.c"
        edited.write_text("")
        calls = _capture_run(monkeypatch)
        _feed_stdin(monkeypatch, str(edited))

        hook.main()

        assert len(calls) == 1
        cmd, kwargs = calls[0]
        assert cmd == "make test"
        assert Path(kwargs["cwd"]).resolve() == lib.resolve()

    def test_authoring_test_runs_at_pyproject_root(self, tmp_path):
        root = tmp_path / "superclaude"
        (root / "agents").mkdir(parents=True)
        (root / "pyproject.toml").write_text("")
        edited = root / "agents" / "x.md"
        edited.write_text("")

        result = hook.detect_authoring_test(str(edited))

        assert result is not None
        cmd, cwd = result
        assert cmd == (
            "uv run python -m pytest tests/unit/test_agent_structure.py --tb=short -q"
        )
        assert Path(cwd).resolve() == root.resolve()


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


def test_own_timeout_is_below_the_hooks_json_timeout() -> None:
    # Claude Code's hook timer starts before run_shell's; with equal values
    # Claude Code always cuts the hook off first and the tree kill never runs.
    import superclaude

    hooks = json.loads(
        (Path(superclaude.__file__).parent / "hooks" / "hooks.json").read_text(
            encoding="utf-8"
        )
    )
    timeouts = [
        h["timeout"]
        for groups in hooks["hooks"].values()
        for group in groups
        for h in group.get("hooks", [])
        if h.get("command", "").endswith("test_runner_hook")
    ]
    assert timeouts, "hooks.json registers no test_runner_hook"
    for t in timeouts:
        assert hook.TEST_TIMEOUT_SECONDS + 5 <= t, (hook.TEST_TIMEOUT_SECONDS, t)
