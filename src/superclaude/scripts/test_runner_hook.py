#!/usr/bin/env python3
"""PostToolUse hook for running tests after code edits.
Detects project test runner (npm test / pytest / make test) and runs it.
Cross-platform compatible (Windows/macOS/Linux).

Only runs when a source code file is edited (not configs, docs, etc.).
Respects SUPERCLAUDE_AUTO_TEST=0 env var to disable.
"""
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

# File extensions that should trigger test runs
SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".go", ".rs", ".java", ".kt", ".rb",
    ".c", ".cpp", ".h", ".hpp", ".cs",
}

# Directories to skip (edits in these don't trigger tests)
SKIP_DIRS = {"node_modules", "__pycache__", ".venv", "dist", "build", ".git"}


def detect_test_command(file_path: str) -> str | None:
    """Detect the appropriate test command based on project files."""
    path = Path(file_path).resolve()

    # Walk up to find project root indicators
    for parent in [path.parent, *path.parents]:
        if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
            if (parent / "Makefile").exists():
                return f"make -C {shlex.quote(str(parent))} test"
            return "uv run pytest --tb=short -q"

        if (parent / "package.json").exists():
            return "npm test --silent"

        if (parent / "Makefile").exists():
            return f"make -C {shlex.quote(str(parent))} test"

        # Stop at git root
        if (parent / ".git").exists():
            break

    return None


def should_run(file_path: str) -> bool:
    """Check if this file edit should trigger a test run."""
    if not file_path:
        return False

    path = Path(file_path)

    # Check extension
    if path.suffix.lower() not in SOURCE_EXTENSIONS:
        return False

    # Check if in a skip directory
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
        file_path = data.get("tool_input", {}).get("file_path", "")

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

        if result.returncode != 0:
            # Output failure info so Claude Code can see it
            print(f"test hook: FAIL ({test_cmd})", file=sys.stderr)
            # Show last 20 lines of output for context
            lines = (result.stdout + result.stderr).strip().splitlines()
            for line in lines[-20:]:
                print(f"  {line}", file=sys.stderr)
        else:
            print("test hook: PASS", file=sys.stderr)

    except json.JSONDecodeError:
        print("test hook: skipped (invalid JSON input)", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("test hook: skipped (timeout after 120s)", file=sys.stderr)
    except OSError as e:
        print(f"test hook: skipped (OS error: {e})", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
