#!/usr/bin/env python3
"""PreToolUse hook that blocks Read calls on files exceeding the token limit.

Claude Code's Read tool hard-fails at 25,000 tokens (~100KB). This hook
intercepts Read calls, checks file size, and blocks with a helpful message
before the tool wastes a turn on a guaranteed failure.

Threshold: 80KB (20% safety buffer below the 25K token limit).
Bypass: If the Read call already includes a `limit` parameter, it's allowed
        through — the caller is already paginating.

Respects SUPERCLAUDE_SIZE_GUARD=0 env var to disable.
Outputs structured JSON for Claude Code PreToolUse hook protocol.
"""
import json
import os
import sys
from pathlib import Path

# 80KB ≈ 20K tokens — 20% buffer below CC's 25K token hard limit
SIZE_THRESHOLD = 80_000

# Extensions to skip (binary/image files have different Read paths)
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".pdf", ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".webm",
    ".pyc", ".pyo", ".so", ".dylib", ".dll", ".exe",
    ".ipynb",
}


def main() -> None:
    # Respect opt-out env var
    if os.environ.get("SUPERCLAUDE_SIZE_GUARD", "1") == "0":
        print(json.dumps({"decision": "allow"}))
        return

    try:
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data:
            print(json.dumps({"decision": "allow"}))
            return

        data = json.loads(stdin_data)
        tool_input = data.get("tool_input", {})

        file_path = tool_input.get("file_path", "")
        has_limit = tool_input.get("limit") is not None

        # If limit is already set, caller is paginating — allow
        if has_limit:
            print(json.dumps({"decision": "allow"}))
            return

        # Skip binary files
        if file_path:
            ext = Path(file_path).suffix.lower()
            if ext in BINARY_EXTENSIONS:
                print(json.dumps({"decision": "allow"}))
                return

        # Check file size
        if file_path and os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            if size > SIZE_THRESHOLD:
                size_kb = size // 1024
                # Suggest a reasonable limit based on file size
                suggested_limit = 500
                print(json.dumps({
                    "decision": "block",
                    "reason": (
                        f"File is {size_kb}KB ({size:,} bytes) — exceeds safe Read "
                        f"threshold (80KB). Use limit parameter "
                        f"(e.g., limit={suggested_limit}) or use Grep to search "
                        f"for specific content."
                    ),
                }))
                return

        print(json.dumps({"decision": "allow"}))

    except json.JSONDecodeError:
        # Don't block on hook errors — fail open
        print(json.dumps({"decision": "allow"}))
    except OSError:
        print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
