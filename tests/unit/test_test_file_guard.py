"""Tests for test_file_guard.py — the test-file lock hook.

Contract:
- ``check`` (PreToolUse on Edit|Write, the hooks.json registration; bare argv
  means the same): no marker -> approve; marker + test-file path -> block with
  a reason that names ``superclaude hook test_file_guard unlock``; marker +
  non-test path -> approve; SUPERCLAUDE_TEST_LOCK=0 -> approve.
- ``lock`` / ``unlock`` / ``status``: plain stdout. The marker is
  <claude_base>/.superclaude_hooks/test_file_lock_<project_key>, so a
  user-scope install locks one project at a time and uninstall removes it.
- Failure modes (bad stdin, empty stdin, no file_path) fail open (approve).
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from superclaude.scripts.test_file_guard import is_test_file

GUARD_SCRIPT = (
    Path(__file__).parent.parent.parent
    / "src"
    / "superclaude"
    / "scripts"
    / "test_file_guard.py"
)

UNLOCK_COMMAND = "superclaude hook test_file_guard unlock"


def run_guard(
    args: list[str],
    project_dir: Path,
    stdin: str = "",
    env_override: dict | None = None,
) -> subprocess.CompletedProcess:
    """Invoke test_file_guard.py with a subcommand; CLAUDE_PROJECT_DIR pinned."""
    env = os.environ.copy()
    env.pop("SUPERCLAUDE_TEST_LOCK", None)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    if env_override:
        env.update(env_override)
    return subprocess.run(
        [sys.executable, str(GUARD_SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
    )


def check(file_path: str, project_dir: Path, env_override: dict | None = None) -> dict:
    """Run the PreToolUse path and return the parsed decision."""
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": file_path}})
    result = run_guard(["check"], project_dir, stdin=payload, env_override=env_override)
    assert result.returncode == 0, f"guard crashed: {result.stderr}"
    return json.loads(result.stdout.strip())


def marker_file(project_dir: Path) -> Path:
    """Resolve the marker the same way superclaude.utils does.

    Mirrors hook_state_dir() / f"test_file_lock_{project_key()}" without
    importing the resolvers, which read CLAUDE_PROJECT_DIR from the *test*
    process rather than the guard subprocess.
    """
    key = hashlib.md5(str(project_dir).encode()).hexdigest()[:8]
    return project_dir / ".claude" / ".superclaude_hooks" / f"test_file_lock_{key}"


@pytest.fixture
def project_dir(tmp_path):
    # The superclaude/ marker makes claude_base() resolve to this tmp project
    # instead of falling back to the real ~/.claude, keeping tests hermetic.
    (tmp_path / ".claude" / "superclaude").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def locked_project(project_dir):
    marker = marker_file(project_dir)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()
    return project_dir


TEST_PATHS = [
    "tests/unit/test_guard.py",
    "src/pkg/__tests__/guard.js",
    "src/pkg/guard_test.py",
    "src/pkg/guard.test.ts",
    "src/pkg/guard.spec.js",
    "tests/fixtures/data.json",
    "C:\\repo\\tests\\unit\\test_guard.py",
    "Tests/Unit/FooTests.cs",
]
NON_TEST_PATHS = [
    "src/pkg/guard.py",
    "README.md",
    "src/pkg/contest_results.py",
    "src/latest/report.md",
    "docs/testing.md",
]


class TestIsTestFile:
    @pytest.mark.parametrize("path", TEST_PATHS)
    def test_test_paths(self, path):
        assert is_test_file(path)

    @pytest.mark.parametrize("path", [*NON_TEST_PATHS, ""])
    def test_non_test_paths(self, path):
        assert not is_test_file(path)


class TestCheck:
    def test_no_marker_approves(self, project_dir):
        assert check("tests/unit/test_guard.py", project_dir)["decision"] == "approve"

    @pytest.mark.parametrize("path", TEST_PATHS)
    def test_marker_blocks_test_file(self, locked_project, path):
        result = check(path, locked_project)
        assert result["decision"] == "block"
        assert UNLOCK_COMMAND in result["reason"]
        assert path in result["reason"]

    def test_block_reason_says_why(self, locked_project):
        reason = check("tests/unit/test_guard.py", locked_project)["reason"]
        assert "proof" in reason
        assert "weaken" in reason

    @pytest.mark.parametrize("path", NON_TEST_PATHS)
    def test_marker_approves_non_test_file(self, locked_project, path):
        assert check(path, locked_project)["decision"] == "approve"

    def test_bare_argv_is_check(self, locked_project):
        payload = json.dumps({"tool_input": {"file_path": "tests/unit/test_guard.py"}})
        result = run_guard([], locked_project, stdin=payload)
        assert json.loads(result.stdout.strip())["decision"] == "block"

    def test_env_opt_out_approves(self, locked_project):
        result = check(
            "tests/unit/test_guard.py",
            locked_project,
            env_override={"SUPERCLAUDE_TEST_LOCK": "0"},
        )
        assert result["decision"] == "approve"

    def test_invalid_json_fails_open(self, locked_project):
        result = run_guard(["check"], locked_project, stdin="not json")
        assert json.loads(result.stdout.strip()) == {"decision": "approve"}

    def test_empty_stdin_approves(self, locked_project):
        result = run_guard(["check"], locked_project, stdin="")
        assert json.loads(result.stdout.strip()) == {"decision": "approve"}

    def test_missing_file_path_approves(self, locked_project):
        payload = json.dumps({"tool_input": {}})
        result = run_guard(["check"], locked_project, stdin=payload)
        assert json.loads(result.stdout.strip()) == {"decision": "approve"}


class TestSubcommands:
    def test_lock_creates_marker_under_hook_state_dir(self, project_dir):
        result = run_guard(["lock"], project_dir)
        assert result.returncode == 0, result.stderr
        assert result.stdout.startswith("locked")
        assert UNLOCK_COMMAND in result.stdout
        assert marker_file(project_dir).is_file()

    def test_status_reports_both_states(self, project_dir):
        assert run_guard(["status"], project_dir).stdout.startswith("unlocked")
        run_guard(["lock"], project_dir)
        assert run_guard(["status"], project_dir).stdout.startswith("locked")

    def test_unlock_removes_marker_and_is_idempotent(self, project_dir):
        run_guard(["lock"], project_dir)
        first = run_guard(["unlock"], project_dir)
        assert first.returncode == 0
        assert first.stdout.startswith("unlocked")
        assert not marker_file(project_dir).exists()
        second = run_guard(["unlock"], project_dir)
        assert second.returncode == 0
        assert second.stdout.startswith("unlocked")

    def test_lock_check_unlock_round_trip(self, project_dir):
        path = "tests/unit/test_guard.py"
        run_guard(["lock"], project_dir)
        assert check(path, project_dir)["decision"] == "block"
        run_guard(["unlock"], project_dir)
        assert check(path, project_dir)["decision"] == "approve"

    def test_unknown_subcommand_exits_1_with_usage(self, project_dir):
        result = run_guard(["bogus"], project_dir)
        assert result.returncode == 1
        assert result.stdout == ""
        assert "usage:" in result.stderr
        assert "bogus" in result.stderr

    def test_help_lists_subcommands(self, project_dir):
        result = run_guard(["--help"], project_dir)
        assert result.returncode == 0
        for sub in ("check", "lock", "unlock", "status"):
            assert sub in result.stdout


REAL_HOME_STATE = Path(os.path.expanduser("~")) / ".claude" / ".superclaude_hooks"
_REAL_HOME_LOCKS_BEFORE = (
    set(REAL_HOME_STATE.glob("test_file_lock_*")) if REAL_HOME_STATE.exists() else set()
)


class TestAnchor:
    def test_lock_from_subdir_without_env_matches_hook(self, project_dir):
        """`lock` from the Bash tool has no CLAUDE_PROJECT_DIR; its marker must
        still be the one `check` (run by Claude Code with the env set) reads."""
        (project_dir / ".git").mkdir()
        sub = project_dir / "src"
        sub.mkdir()
        env = os.environ.copy()
        env.pop("CLAUDE_PROJECT_DIR", None)
        env.pop("SUPERCLAUDE_TEST_LOCK", None)
        result = subprocess.run(
            [sys.executable, str(GUARD_SCRIPT), "lock"],
            cwd=sub,
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, result.stderr
        assert marker_file(project_dir).is_file(), result.stdout
        assert check("tests/unit/test_guard.py", project_dir)["decision"] == "block"


class TestNoLeak:
    def test_no_marker_leaked_into_real_home(self):
        """Mirrors test_loop_guard.py: a fixture regression must not leave a
        lock in the developer's real ~/.claude (the fallback anchor)."""
        after = (
            set(REAL_HOME_STATE.glob("test_file_lock_*"))
            if REAL_HOME_STATE.exists()
            else set()
        )
        assert after == _REAL_HOME_LOCKS_BEFORE
