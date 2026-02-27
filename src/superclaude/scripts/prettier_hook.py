#!/usr/bin/env python3
"""PostToolUse hook for running prettier on JS/TS files.

Runs prettier on edited files with supported extensions.
Cross-platform compatible (Windows/macOS/Linux).

Checks stop_hook_active to prevent infinite loops (Claude Code best practice).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

PRETTIER_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}


def _find_prettier() -> list[str]:
    """Find prettier binary — prefer local install over npx."""
    # Check node_modules/.bin first (fastest)
    local = Path("node_modules/.bin/prettier")
    if local.exists():
        return [str(local)]

    # Check global prettier
    if shutil.which("prettier"):
        return ["prettier"]

    # Fallback to npx (slower, but always available)
    return ["npx", "prettier"]


def main() -> None:
    try:
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data:
            return

        data = json.loads(stdin_data)

        # Prevent infinite loops when Claude is stopping
        if data.get("stop_hook_active"):
            return

        file_path = data.get("tool_input", {}).get("file_path", "")
        if not file_path:
            return

        path = Path(file_path)
        if path.suffix.lower() not in PRETTIER_EXTENSIONS:
            return

        cmd = _find_prettier() + ["--write", str(path)]
        result = subprocess.run(cmd, capture_output=True, timeout=30)

        if result.returncode == 0:
            # Structured output so Claude knows formatting occurred
            msg = json.dumps({"systemMessage": f"Formatted {path.name} with prettier"})
            print(msg)

    except json.JSONDecodeError:
        pass
    except subprocess.TimeoutExpired:
        print("prettier hook: timeout", file=sys.stderr)
    except OSError:
        pass  # prettier not installed — silent skip


if __name__ == "__main__":
    main()
    sys.exit(0)
