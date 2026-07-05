"""MCP Fallback Hint Tracker for SuperClaude

Tracks per-session fallback hints so each MCP's fallback guidance is shown once.
Uses same session infrastructure as hook_tracker.py.

The hook cannot check actual MCP server availability, so the hint is phrased
conditionally ("if unavailable") rather than asserting the server is down.

Behavior:
- First time an MCP is referenced in a session: Show fallback hint
- Subsequent uses: Silent, no hint

Session identity: callers should pass the `session_id` from the CC hook
stdin JSON (context_loader.py does) so the hint re-arms each CC session;
hook_tracker.get_session_id() is only a non-rotating fallback.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from superclaude.hooks.hook_tracker import _ensure_tracker_dir, get_session_id
from superclaude.utils import atomic_write_json

# Storage for MCP fallback notifications
MCP_FALLBACK_FILE = (
    Path.home() / ".claude" / ".superclaude_hooks" / "mcp_fallbacks.json"
)

# Fallback mapping (see FLAGS.md <mcp> section for flag definitions)
MCP_FALLBACKS: dict[str, str] = {
    "context7": "Tavily/WebSearch",
    "tavily": "WebSearch (native)",
    "sequential": "Native reasoning",
    "serena": "Grep/Glob + Edit (no symbol ops or persistence)",
    "playwright": "DevTools MCP (--devtools) or native WebFetch (install: npx @playwright/mcp@latest)",
    "devtools": "Playwright (install plugin: superclaude mcp --servers chrome-devtools)",
}


def _load_fallback_data() -> dict[str, dict[str, str]]:
    """Load fallback notification data.

    Returns:
        Dict mapping session_id to dict of {mcp_name: notified_at}
    """
    if not MCP_FALLBACK_FILE.exists():
        return {}

    try:
        data: dict[str, dict[str, str]] = json.loads(MCP_FALLBACK_FILE.read_text())
        return data
    except (json.JSONDecodeError, OSError):
        return {}


def _save_fallback_data(data: dict[str, dict[str, str]]) -> None:
    """Save fallback notification data."""
    _ensure_tracker_dir()
    try:
        atomic_write_json(MCP_FALLBACK_FILE, data)
    except OSError:
        pass  # Best-effort: fallback still works without persistence


def should_notify_fallback(
    mcp_name: str, session_id: str | None = None
) -> tuple[bool, str]:
    """Check if fallback notification should be shown.

    Args:
        mcp_name: Name of the MCP server (lowercase)
        session_id: CC session id from the hook stdin JSON. Falls back to
            hook_tracker.get_session_id() (cached, does not rotate per
            session) when not provided.

    Returns:
        Tuple of (should_notify, fallback_tool_name)
    """
    mcp_lower = mcp_name.lower()
    fallback = MCP_FALLBACKS.get(mcp_lower, "Native")

    if session_id is None:
        session_id = get_session_id()
    data = _load_fallback_data()

    session_data = data.get(session_id, {})

    if mcp_lower in session_data:
        # Already notified this session
        return False, fallback

    # First time - mark and return True
    if session_id not in data:
        data[session_id] = {}
    data[session_id][mcp_lower] = datetime.now().isoformat()
    _save_fallback_data(data)

    return True, fallback


def format_fallback_notification(mcp_name: str, fallback: str) -> str:
    """Format the fallback hint message.

    Phrased conditionally — the hook has no way to check whether the MCP
    server is actually connected, so it must not assert unavailability.

    Args:
        mcp_name: Name of the MCP server
        fallback: Fallback tool name

    Returns:
        Formatted hint string
    """
    return f"ℹ️ If {mcp_name} MCP is unavailable, fall back to: {fallback}"


def check_mcp_and_notify(mcp_name: str, session_id: str | None = None) -> str | None:
    """Return the fallback hint on first reference this session.

    Does NOT check actual server availability — only tracks whether the
    hint was already shown this session.

    Args:
        mcp_name: Name of the MCP server
        session_id: CC session id from the hook stdin JSON (see
            should_notify_fallback)

    Returns:
        Hint string if first time, None if already shown
    """
    should_notify, fallback = should_notify_fallback(mcp_name, session_id)

    if should_notify:
        return format_fallback_notification(mcp_name, fallback)
    return None


def get_fallback_for(mcp_name: str) -> str:
    """Get the fallback tool for an MCP server.

    Args:
        mcp_name: Name of the MCP server

    Returns:
        Fallback tool name
    """
    return MCP_FALLBACKS.get(mcp_name.lower(), "Native")
