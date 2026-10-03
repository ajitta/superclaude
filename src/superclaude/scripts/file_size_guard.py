#!/usr/bin/env python3
"""PreToolUse hook that blocks Read calls on large files to prevent token explosion.

Proactive token conservation: blocks full-file reads above 30KB, pushing the
model toward Serena symbolic tools, Grep, or paginated Read instead.

Threshold: 30KB (token conservation, not CC hard limit).
Bypass: limit parameter, pages parameter (PDF), binary extensions, files
        under 30KB.

Respects SUPERCLAUDE_SIZE_GUARD=0 env var to disable.
Outputs structured JSON for Claude Code PreToolUse hook protocol.
"""

import json
import os
import sys
from pathlib import Path

# 30KB — proactive token conservation threshold
SIZE_THRESHOLD = 30_000

# Extensions to skip (binary/image files have different Read paths)
BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".webp",
    ".svg",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".7z",
    ".rar",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".mp3",
    ".mp4",
    ".wav",
    ".avi",
    ".mov",
    ".webm",
    ".pyc",
    ".pyo",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".ipynb",
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


def _block_reason(tool_input: dict) -> str | None:
    """Why this Read should be blocked, or None to let it through."""
    # If limit or pages is set, caller is paginating — allow
    if tool_input.get("limit") is not None or tool_input.get("pages") is not None:
        return None
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return None
    ext = Path(file_path).suffix.lower()
    # Binary files have different Read paths
    if ext in BINARY_EXTENSIONS or not os.path.isfile(file_path):
        return None
    size = os.path.getsize(file_path)
    return _block_message(size, ext) if size >= SIZE_THRESHOLD else None


def main() -> None:
    reason = None
    # Respect opt-out env var
    if os.environ.get("SUPERCLAUDE_SIZE_GUARD", "1") != "0":
        try:
            stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
            if stdin_data:
                reason = _block_reason(json.loads(stdin_data).get("tool_input", {}))
        except (json.JSONDecodeError, OSError):
            pass  # Don't block on hook errors — fail open

    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))
    else:
        print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
