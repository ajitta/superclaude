"""MCP Fallback Hint Tracker for SuperClaude

Tracks per-session fallback hints so each MCP's fallback guidance is shown once.

The hook cannot check actual MCP server availability, so the hint is phrased
conditionally ("if unavailable") rather than asserting the server is down.

Behavior:
- First time an MCP is referenced in a session: Show fallback hint
- Subsequent uses: Silent, no hint

Session identity: callers should pass the `session_id` from the CC hook
stdin JSON (context_loader.py does) so the hint re-arms each CC session;
callers without one share the session "default".
"""

from __future__ import annotations

import json
from datetime import datetime

from superclaude.utils import atomic_write_json, hook_state_dir

# Storage for MCP fallback notifications (scoped to the active install)
MCP_FALLBACK_FILE = hook_state_dir() / "mcp_fallbacks.json"

# Fallback mapping (see FLAGS.md <mcp> section for flag definitions)
MCP_FALLBACKS: dict[str, str] = {
    "context7": "Tavily/WebSearch",
    "tavily": "Tavily Agent Skills (tvly CLI), then native WebSearch",
    "serena": "Grep/Glob + Edit (no symbol ops or persistence)",
    "playwright": "playwright-cli skill if installed, else DevTools MCP (--devtools) or native WebFetch (install either: mcp/README.md 'Playwright — CLI or MCP')",
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
    try:
        atomic_write_json(MCP_FALLBACK_FILE, data)
    except OSError:
        pass  # Best-effort: fallback still works without persistence


def check_mcp_and_notify(mcp_name: str, session_id: str | None = None) -> str | None:
    """Return the fallback hint on first reference this session.

    Does NOT check actual server availability — only tracks whether the
    hint was already shown this session. The hint is phrased conditionally:
    the hook has no way to check whether the MCP server is actually
    connected, so it must not assert unavailability.

    Args:
        mcp_name: Name of the MCP server
        session_id: CC session id from the hook stdin JSON; callers without
            one share the session "default"

    Returns:
        Hint string if first time, None if already shown
    """
    mcp_lower = mcp_name.lower()
    data = _load_fallback_data()
    seen = data.setdefault(session_id or "default", {})
    if mcp_lower in seen:
        return None

    seen[mcp_lower] = datetime.now().isoformat()
    _save_fallback_data(data)
    fallback = MCP_FALLBACKS.get(mcp_lower, "Native")
    return f"ℹ️ If {mcp_name} MCP is unavailable, fall back to: {fallback}"
