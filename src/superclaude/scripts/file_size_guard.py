#!/usr/bin/env python3
"""PreToolUse hook that blocks Read calls on large files to prevent token explosion.

Proactive token conservation: blocks full-file reads above 30KB, pushing the
model toward Serena symbolic tools, ast-grep, Grep, or paginated Read instead.

Threshold: 30KB (token conservation, not CC hard limit).
Bypass: limit parameter, pages parameter (PDF), binary extensions,
        small files (<5KB), config extensions (<30KB).

Respects SUPERCLAUDE_SIZE_GUARD=0 env var to disable.
Outputs structured JSON for Claude Code PreToolUse hook protocol.
"""
import json
import os
import sys
from pathlib import Path

# 30KB — proactive token conservation threshold
SIZE_THRESHOLD = 30_000

# Small files exempt unconditionally
SMALL_FILE_THRESHOLD = 5_000

# Extensions to skip (binary/image files have different Read paths)
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".pdf", ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".webm",
    ".pyc", ".pyo", ".so", ".dylib", ".dll", ".exe",
    ".ipynb",
}

# Config extensions — exempt below SIZE_THRESHOLD
CONFIG_EXTENSIONS = {
    ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".env",
}

# Code/JSON extensions for context-aware block messages
JSON_EXTENSIONS = {".json", ".jsonl", ".ndjson"}


def _block_message(size: int, ext: str) -> str:
    """Generate context-aware block message based on file extension."""
    size_kb = size // 1024
    if ext in JSON_EXTENSIONS:
        return (
            f"File is {size_kb}KB ({size:,} bytes) — exceeds safe Read threshold "
            f"(30KB). Use jq to query specific fields (e.g., jq '.key' file{ext}) "
            f"or Read with limit parameter (e.g., limit=500)."
        )
    return (
        f"File is {size_kb}KB ({size:,} bytes) — exceeds safe Read threshold "
        f"(30KB). Use limit parameter (e.g., limit=500) or Grep to search "
        f"for specific content."
    )


def main() -> None:
    # Respect opt-out env var
    if os.environ.get("SUPERCLAUDE_SIZE_GUARD", "1") == "0":
        print(json.dumps({"decision": "approve"}))
        return

    try:
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data:
            print(json.dumps({"decision": "approve"}))
            return

        data = json.loads(stdin_data)
        tool_input = data.get("tool_input", {})

        file_path = tool_input.get("file_path", "")
        has_limit = tool_input.get("limit") is not None
        has_pages = tool_input.get("pages") is not None

        # If limit or pages is set, caller is paginating — allow
        if has_limit or has_pages:
            print(json.dumps({"decision": "approve"}))
            return

        if not file_path:
            print(json.dumps({"decision": "approve"}))
            return

        ext = Path(file_path).suffix.lower()

        # Skip binary files
        if ext in BINARY_EXTENSIONS:
            print(json.dumps({"decision": "approve"}))
            return

        # Check file size
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)

            # Small files exempt unconditionally
            if size < SMALL_FILE_THRESHOLD:
                print(json.dumps({"decision": "approve"}))
                return

            # Config extensions exempt below threshold
            if ext in CONFIG_EXTENSIONS and size < SIZE_THRESHOLD:
                print(json.dumps({"decision": "approve"}))
                return

            # Block files above threshold
            if size >= SIZE_THRESHOLD:
                print(json.dumps({
                    "decision": "block",
                    "reason": _block_message(size, ext),
                }))
                return

        print(json.dumps({"decision": "approve"}))

    except json.JSONDecodeError:
        # Don't block on hook errors — fail open
        print(json.dumps({"decision": "approve"}))
    except OSError:
        print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
