#!/usr/bin/env python3
"""Context Cache Reset for /clear and /compact Events

SessionStart hook that resets context_loader's dedup cache when the user
runs /clear or /compact. Without this, dynamic contexts (modes, MCP docs)
are never re-injected because the stale cache blocks them.

Registered in hooks.json with matcher: "clear" and "compact".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from superclaude.utils import context_cache_file


def get_cache_file(session_id: str | None = None) -> Path:
    """Get the context_loader cache file for this project and session.

    Omitting the session id yields the project-only name, which is both the
    pre-session-keying filename and the loader's own fallback.
    """
    return context_cache_file(session_id)


def reset_context_cache(session_id: str | None = None) -> bool:
    """Delete this session's dedup cache so contexts re-inject on next prompt.

    Only this session's file and the project-only fallback are removed. A
    concurrent window on the same repository keeps its own cache — clearing one
    session must not force another to re-inject everything it already has.

    Args:
        session_id: Session id from the SessionStart payload, or None

    Returns:
        True if any cache file was removed
    """
    removed = False
    targets = [get_cache_file(session_id)]
    if session_id:
        targets.append(get_cache_file())
    for target in targets:
        if not target.exists():
            continue
        try:
            target.unlink()
            removed = True
        except OSError:
            continue
    return removed


def main() -> None:
    # Read SessionStart hook input from stdin
    try:
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data:
            return

        data = json.loads(stdin_data)
        source = data.get("source", "")
        session_id = data.get("session_id")
    except (json.JSONDecodeError, OSError):
        # If we can't read input, reset cache defensively
        source = "unknown"
        session_id = None

    # 'startup' = fresh session (no conversation history) → LLM hasn't seen prior emits
    # 'clear'   = /clear erased history → same situation
    # 'compact' = summary may drop emit details → safer to re-inject
    # 'resume'  = NOT included: history is restored, prior emits still visible to LLM
    if source in ("clear", "compact", "startup"):
        was_reset = reset_context_cache(session_id)
        if was_reset:
            print(
                f"🔄 Context cache reset ({source}) — dynamic contexts will re-inject"
            )


if __name__ == "__main__":
    main()
    sys.exit(0)
