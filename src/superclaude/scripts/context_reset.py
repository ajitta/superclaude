#!/usr/bin/env python3
"""Context Cache Reset for /clear and /compact Events

SessionStart hook that resets context_loader's dedup cache when the user
runs /clear or /compact. Without this, dynamic contexts (modes, MCP docs)
are never re-injected because the stale cache blocks them.

Registered in hooks.json with matcher: "clear" and "compact".
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

CACHE_DIR = Path.home() / ".claude" / ".superclaude_hooks"


def get_cache_file() -> Path:
    """Get the context_loader cache file for the current working directory."""
    session_id = hashlib.md5(os.getcwd().encode()).hexdigest()[:8]
    return CACHE_DIR / f"claude_context_{session_id}.txt"


def reset_context_cache() -> bool:
    """Delete the context_loader dedup cache so contexts re-inject on next prompt.

    Returns:
        True if cache was reset, False if no cache existed
    """
    cache_file = get_cache_file()
    if cache_file.exists():
        try:
            cache_file.unlink()
            return True
        except OSError:
            return False
    return False


def main() -> None:
    # Read SessionStart hook input from stdin
    try:
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data:
            return

        data = json.loads(stdin_data)
        source = data.get("source", "")
    except (json.JSONDecodeError, OSError):
        # If we can't read input, reset cache defensively
        source = "unknown"

    if source in ("clear", "compact"):
        was_reset = reset_context_cache()
        if was_reset:
            print(f"🔄 Context cache reset ({source}) — dynamic contexts will re-inject")


if __name__ == "__main__":
    main()
    sys.exit(0)
