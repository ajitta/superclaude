#!/usr/bin/env python3
"""PostToolUse hook for running tests after code edits (async).

Detects project test runner (npm test / pytest / make test) and runs it.
Cross-platform compatible (Windows/macOS/Linux).

Only runs when a source code file is edited (not configs, docs, etc.).
Respects SUPERCLAUDE_AUTO_TEST=0 env var to disable.
Checks stop_hook_active to prevent infinite loops (Claude Code best practice).
Outputs structured JSON systemMessage so Claude can react to results.
"""

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

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


def _quote_path(path) -> str:
    """Quote a path for shell=True subprocess. shlex.quote produces POSIX
    single-quotes that Windows shells (cmd.exe, MSYS make) don't interpret —
    they reach make/pytest as literal characters and break path parsing on
    drive-letter colons."""
    return f'"{path}"' if os.name == "nt" else shlex.quote(str(path))


def detect_authoring_test(file_path: str) -> str | None:
    """If a SuperClaude .md authoring file was edited, return targeted pytest cmd."""
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
                    return f"uv run python -m pytest {_quote_path(parent / test_file)} --tb=short -q"
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


def detect_test_command(file_path: str) -> str | None:
    """Detect the appropriate test command based on project files."""
    path = Path(file_path).resolve()

    # Walk up to find project root indicators
    for parent in [path.parent, *path.parents]:
        if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
            if (parent / "Makefile").exists():
                return f"make -C {_quote_path(parent)} test"
            return "uv run python -m pytest --tb=short -q"

        if (parent / "package.json").exists():
            # `npm test --silent` prints nothing when the script is missing,
            # so check the script before running rather than parse its output.
            if not _npm_has_test_script(parent / "package.json"):
                return None
            return "npm test --silent"

        if (parent / "Makefile").exists():
            return f"make -C {_quote_path(parent)} test"

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

    try:
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data:
            return

        data = json.loads(stdin_data)

        # Prevent infinite loops when Claude is stopping
        if data.get("stop_hook_active"):
            return

        file_path = data.get("tool_input", {}).get("file_path", "")

        test_cmd = detect_authoring_test(file_path)
        if test_cmd is None:
            if not should_run(file_path):
                return
            test_cmd = detect_test_command(file_path)
        if not test_cmd:
            return

        result = subprocess.run(
            test_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )

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

    except json.JSONDecodeError:
        print("test hook: invalid JSON input", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("test hook: timeout after 120s", file=sys.stderr)
    except OSError as e:
        print(f"test hook: OS error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
