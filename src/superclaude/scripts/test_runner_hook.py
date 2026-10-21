#!/usr/bin/env python3
"""PostToolUse hook for running tests after code edits (async).

Detects project test runner (npm test / pytest / make test) and runs it.
Cross-platform compatible (Windows/macOS/Linux).

Only runs when a source code file is edited (not configs, docs, etc.).
Respects SUPERCLAUDE_AUTO_TEST=0 env var to disable.
Outputs structured JSON systemMessage so Claude can react to results.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from superclaude.utils import read_hook_input, run_shell

# Below the hook's `timeout` in hooks.json (120 s): Claude Code's timer starts
# with the hook, before this one, so an equal value lets Claude Code cut the
# hook off first and run_shell's tree kill never runs
# (test_test_runner_hook.py checks the gap).
TEST_TIMEOUT_SECONDS = 110

# File extensions that should trigger test runs
SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".rb",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
}

# Directories to skip (edits in these don't trigger tests)
SKIP_DIRS = {"node_modules", "__pycache__", ".venv", "dist", "build", ".git"}

# Authoring-rule dispatch: .md edits under these dirs run targeted structure tests
AUTHORING_TEST_MAP = {
    "agents": "tests/unit/test_agent_structure.py",
    "commands": "tests/unit/test_command_structure.py",
    "modes": "tests/unit/test_mode_structure.py",
}


def detect_authoring_test(file_path: str) -> tuple[str, Path] | None:
    """If a superclaude .md authoring file was edited, return (pytest cmd, cwd)."""
    path = Path(file_path)
    if path.suffix.lower() != ".md":
        return None
    parts = path.parts
    if "superclaude" not in parts:
        return None
    for segment, test_file in AUTHORING_TEST_MAP.items():
        if segment in parts:
            for parent in path.resolve().parents:
                if (parent / "pyproject.toml").exists():
                    return (
                        f"uv run python -m pytest {test_file} --tb=short -q",
                        parent,
                    )
            return None
    return None


# Output lines meaning "the runner itself could not start", as opposed to a
# test that ran and failed. Each pattern must match a whole line, so a test
# assertion that merely quotes the text, a missing pytest plugin
# ("No module named 'pytest_asyncio'") or a missing prerequisite of the test
# target ("... needed by 'test'") still count as real failures.
_RUNNER_UNAVAILABLE = (
    (
        re.compile(r"^(?:\S+: )?No module named '?pytest'?\s*$", re.M),
        "pytest is not installed",
    ),
    (
        re.compile(
            r"^(?:\S*sh: (?:(?:line )?\d+: )?)?uv: (?:command )?not found\s*$", re.M
        ),
        "uv is not installed",
    ),
    (
        re.compile(r'^npm (?:ERR!|error) Missing script: "test"\s*$', re.M),
        "package.json has no test script",
    ),
    (
        re.compile(
            r"^make(?:\[\d+\])?: \*\*\* No rule to make target [`']test'\.\s+Stop\.\s*$",
            re.M,
        ),
        "the Makefile has no test target",
    ),
)

# A pytest session summary or collection line means tests ran, whatever else
# the output contains.
_PYTEST_SESSION = re.compile(
    r"^collected \d+ items?|^=+ .*\bin [\d.]+s\b.*=+$|^\d+ (?:passed|failed|errors?)\b",
    re.M,
)

# pytest's own exit code for "no tests were collected".
_PYTEST_NO_TESTS = 5

# The default test script `npm init` writes: it always fails and tests nothing.
_NPM_PLACEHOLDER = "no test specified"


def runner_unavailable(output: str, returncode: int) -> str | None:
    """Return why the test runner could not start, or None if tests ran.

    A project whose pyproject.toml does not declare pytest makes
    `uv run python -m pytest` exit non-zero before any test runs. Reporting
    that as "Tests FAILED" sends the model to debug correct code. Only a
    non-zero exit with no pytest session in the output qualifies.
    """
    if returncode == 0:
        return None
    if returncode == _PYTEST_NO_TESTS and "no tests ran" in output:
        return "pytest collected no tests"
    if _PYTEST_SESSION.search(output):
        return None
    for pattern, reason in _RUNNER_UNAVAILABLE:
        if pattern.search(output):
            return reason
    return None


def _npm_has_test_script(package_json: Path) -> bool:
    """True when package.json defines a real `test` script."""
    try:
        scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts")
    except (OSError, ValueError, AttributeError):
        return True  # unreadable: let npm report it
    script = (scripts or {}).get("test", "") if isinstance(scripts, dict) else ""
    return bool(script.strip()) and _NPM_PLACEHOLDER not in script


def detect_test_command(file_path: str) -> tuple[str, Path] | None:
    """Detect the test command and the project directory to run it in.

    The directory is the one whose marker file was found, so a sub-project
    in a monorepo runs its own suite rather than whatever lives at the
    hook's CWD.
    """
    path = Path(file_path).resolve()

    # Walk up to find project root indicators
    for parent in [path.parent, *path.parents]:
        if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
            if (parent / "Makefile").exists():
                return "make test", parent
            return "uv run python -m pytest --tb=short -q", parent

        if (parent / "package.json").exists():
            # `npm test --silent` prints nothing when the script is missing,
            # so check the script before running rather than parse its output.
            if not _npm_has_test_script(parent / "package.json"):
                return None
            return "npm test --silent", parent

        if (parent / "Makefile").exists():
            return "make test", parent

        # Stop at git root
        if (parent / ".git").exists():
            break

    return None


def should_run(file_path: str) -> bool:
    """Check if this file edit should trigger a test run."""
    if not file_path:
        return False

    path = Path(file_path)

    if path.suffix.lower() not in SOURCE_EXTENSIONS:
        return False

    parts = path.parts
    if any(part in SKIP_DIRS for part in parts):
        return False

    return True


def main() -> None:
    # Respect opt-out env var
    if os.environ.get("SUPERCLAUDE_AUTO_TEST", "1") == "0":
        return

    data = read_hook_input()
    if data is None:
        return

    try:
        file_path = data.get("tool_input", {}).get("file_path", "")

        detected = detect_authoring_test(file_path)
        if detected is None:
            if not should_run(file_path):
                return
            detected = detect_test_command(file_path)
        if not detected:
            return
        test_cmd, cwd = detected

        result = run_shell(test_cmd, timeout=TEST_TIMEOUT_SECONDS, cwd=cwd)

        file_name = Path(file_path).name

        combined = result.stdout + result.stderr
        reason = runner_unavailable(combined, result.returncode)

        if reason:
            msg = json.dumps(
                {
                    "systemMessage": (
                        f"Tests not run after editing {file_name} ({test_cmd}): "
                        f"{reason}. This says nothing about the edit; run the "
                        "project's own test command to check it."
                    )
                }
            )
            print(msg)
        elif result.returncode != 0:
            # Last 15 lines of failure output for context
            lines = combined.strip().splitlines()
            tail = "\n".join(lines[-15:])
            msg = json.dumps(
                {
                    "systemMessage": f"Tests FAILED after editing {file_name} ({test_cmd}):\n{tail}"
                }
            )
            print(msg)
        else:
            msg = json.dumps(
                {"systemMessage": f"Tests passed after editing {file_name}"}
            )
            print(msg)

    except subprocess.TimeoutExpired:
        print(f"test hook: timeout after {TEST_TIMEOUT_SECONDS}s", file=sys.stderr)
    except OSError as e:
        print(f"test hook: OS error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
