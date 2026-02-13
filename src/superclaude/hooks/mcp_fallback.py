"""MCP Fallback Notification Tracker for SuperClaude

Tracks MCP fallback notifications per session to support first-notification-only behavior.
Uses same session infrastructure as hook_tracker.py.

Behavior:
- First time an MCP fallback is used in a session: Show notification
- Subsequent uses: Silent fallback, no notification
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from superclaude.hooks.hook_tracker import _ensure_tracker_dir, get_session_id
from superclaude.utils import atomic_write_json

# Storage for MCP fallback notifications
MCP_FALLBACK_FILE = Path.home() / ".claude" / ".superclaude_hooks" / "mcp_fallbacks.json"

# Fallback mapping (see FLAGS.md <mcp> section for flag definitions)
MCP_FALLBACKS: dict[str, str] = {
    "context7": "Tavily/WebSearch",
    "tavily": "WebSearch (native)",
    "sequential": "Native reasoning",
    "serena": "Native search",
    "morphllm": "Edit (native)",
    "magic": "Write (native)",
    "playwright": "--chrome (native)",
    "devtools": "Playwright",
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


def should_notify_fallback(mcp_name: str) -> tuple[bool, str]:
    """Check if fallback notification should be shown.

    Args:
        mcp_name: Name of the MCP server (lowercase)

    Returns:
        Tuple of (should_notify, fallback_tool_name)
    """
    mcp_lower = mcp_name.lower()
    fallback = MCP_FALLBACKS.get(mcp_lower, "Native")

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
    """Format the fallback notification message.

    Args:
        mcp_name: Name of the MCP server
        fallback: Fallback tool name

    Returns:
        Formatted notification string
    """
    return f"⚠️ {mcp_name} unavailable → using {fallback}"


def check_mcp_and_notify(mcp_name: str) -> str | None:
    """Check MCP availability and return notification if needed.

    Args:
        mcp_name: Name of the MCP server

    Returns:
        Notification string if first time, None if already notified
    """
    should_notify, fallback = should_notify_fallback(mcp_name)

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


def cleanup_old_fallback_sessions(ttl_seconds: int = 24 * 60 * 60) -> int:
    """Clean up old session data.

    Args:
        ttl_seconds: Time-to-live in seconds

    Returns:
        Number of sessions cleaned
    """
    import time

    data = _load_fallback_data()
    if not data:
        return 0

    now = time.time()
    cutoff = now - ttl_seconds
    cleaned = 0

    sessions_to_remove = []
    for session_id, mcp_data in data.items():
        # Use the latest MCP timestamp to determine session age
        latest_ts = None
        invalid = False
        for timestamp in mcp_data.values():
            try:
                ts = datetime.fromisoformat(timestamp).timestamp()
                if latest_ts is None or ts > latest_ts:
                    latest_ts = ts
            except (ValueError, AttributeError):
                invalid = True
        if invalid and latest_ts is None:
            # All timestamps invalid — remove session
            sessions_to_remove.append(session_id)
            cleaned += 1
        elif latest_ts is not None and latest_ts < cutoff:
            sessions_to_remove.append(session_id)
            cleaned += 1

    for session_id in sessions_to_remove:
        del data[session_id]

    if cleaned > 0:
        _save_fallback_data(data)

    return cleaned
