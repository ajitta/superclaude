#!/usr/bin/env python3
"""PostToolUse hook for running prettier on JS/TS files (Python)
Runs prettier on edited files with supported extensions
Cross-platform compatible (Windows/macOS/Linux)
"""
import json
import subprocess
import sys
from pathlib import Path


def main():
    # Read tool input from stdin (JSON from Claude Code)
    try:
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data:
            return

        data = json.loads(stdin_data)
        file_path = data.get("tool_input", {}).get("file_path", "")

        if not file_path:
            return

        # Check if file has JS/TS extension
        path = Path(file_path)
        if path.suffix.lower() in (".ts", ".tsx", ".js", ".jsx"):
            # Run prettier
            subprocess.run(
                ["npx", "prettier", "--write", str(path)],
                capture_output=True,
                timeout=30,
            )
    except (json.JSONDecodeError, subprocess.TimeoutExpired, Exception):
        # Silently ignore errors
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
