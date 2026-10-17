#!/usr/bin/env python3
"""PostToolUse hook for running prettier on JS/TS files.

Runs prettier on edited files with supported extensions.
Cross-platform compatible (Windows/macOS/Linux).

Checks stop_hook_active to prevent infinite loops (Claude Code best practice).
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from superclaude.utils import project_root

PRETTIER_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}


def _find_prettier() -> str | None:
    """Absolute path of prettier: the project-local install first, then PATH.

    ``shutil.which`` picks ``prettier.cmd`` on Windows (PATHEXT) and the POSIX
    script elsewhere. Spawning the extension-less ``node_modules/.bin/prettier``
    directly fails on Windows with WinError 193 (not a valid Win32 application),
    which used to be swallowed as "prettier not installed". The lookup is
    anchored on the project root because hook CWD is not the project root.
    """
    local_bin = project_root() / "node_modules" / ".bin"
    search = str(local_bin) + os.pathsep + os.environ.get("PATH", "")
    return shutil.which("prettier", path=search)


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

        prettier = _find_prettier()
        if prettier is None:
            return  # prettier not installed — silent skip

        cmd = [prettier, "--write", str(path)]
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
