"""Hook Session Tracker for SuperClaude

Provides the fallback session identity used by mcp_fallback.py's
once-per-session hints, plus cleanup of stale session logs.

Note: once-per-session hook *execution* gating is handled natively by
Claude Code (`"once": true` in hooks.json), not by this module. Callers
running inside a hook should prefer the `session_id` field from the hook
stdin JSON (see context_loader.py) over get_session_id().

Session Management:
- Session ID is generated on first use or derived from environment
- Old sessions are automatically cleaned up (>24h by default)
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from superclaude.utils import atomic_write_json

# Default session TTL: 24 hours (configurable via SUPERCLAUDE_SESSION_TTL env var)
SESSION_TTL_SECONDS = int(os.environ.get("SUPERCLAUDE_SESSION_TTL", 24 * 60 * 60))

# Storage location for hook execution tracking
HOOK_TRACKER_DIR = Path.home() / ".claude" / ".superclaude_hooks"
HOOK_TRACKER_FILE = HOOK_TRACKER_DIR / "hook_executions.json"
SESSION_FILE = HOOK_TRACKER_DIR / "current_session.txt"


@dataclass
class HookExecution:
    """Record of a single hook execution."""

    hook_id: str
    hook_type: (
        str  # One of PreToolUse, PostToolUse, Stop, SessionStart, UserPromptSubmit
    )
    executed_at: str  # ISO format timestamp
    source: str  # File that defined the hook (skill name or hooks.json)


@dataclass
class SessionData:
    """Session tracking data."""

    session_id: str
    started_at: str
    executions: dict[str, HookExecution] = field(default_factory=dict)


def get_session_id() -> str:
    """Get or generate a fallback session ID.

    Callers running inside a Claude Code hook should prefer the `session_id`
    field from the hook stdin JSON — it identifies the real CC session. This
    function is the fallback when that id is unavailable; the cached id
    persists across CC sessions (it does not rotate per session).

    Session ID sources (in priority order):
    1. CLAUDE_SESSION_ID environment variable (if set by Claude Code)
    2. Cached session ID from SESSION_FILE
    3. Newly generated session ID based on timestamp + process info

    Returns:
        Session ID string
    """
    # Try environment variable first
    env_session = os.environ.get("CLAUDE_SESSION_ID")
    if env_session:
        return env_session

    # Try cached session file
    if SESSION_FILE.exists():
        try:
            cached = SESSION_FILE.read_text().strip()
            if cached:
                return cached
        except OSError:
            pass  # Best-effort: proceed to generate new session

    # Generate new session ID
    timestamp = datetime.now().isoformat()
    pid = os.getpid()
    ppid = os.getppid()
    raw = f"{timestamp}-{pid}-{ppid}"
    session_id = hashlib.sha256(raw.encode()).hexdigest()[:16]

    # Cache the session ID
    _ensure_tracker_dir()
    try:
        SESSION_FILE.write_text(session_id)
    except OSError:
        pass  # Best-effort: session still usable without cache

    return session_id


def _ensure_tracker_dir() -> None:
    """Ensure the tracker directory exists."""
    HOOK_TRACKER_DIR.mkdir(parents=True, exist_ok=True)


def _load_tracker_data() -> dict[str, SessionData]:
    """Load tracker data from file.

    Returns:
        Dictionary mapping session_id to SessionData
    """
    if not HOOK_TRACKER_FILE.exists():
        return {}

    try:
        data = json.loads(HOOK_TRACKER_FILE.read_text())
        result = {}
        for session_id, session_dict in data.items():
            executions = {}
            for hook_id, exec_dict in session_dict.get("executions", {}).items():
                executions[hook_id] = HookExecution(**exec_dict)
            result[session_id] = SessionData(
                session_id=session_dict["session_id"],
                started_at=session_dict["started_at"],
                executions=executions,
            )
        return result
    except (json.JSONDecodeError, OSError, KeyError, TypeError):
        return {}


def _save_tracker_data(data: dict[str, SessionData]) -> None:
    """Save tracker data to file.

    Args:
        data: Dictionary mapping session_id to SessionData
    """
    _ensure_tracker_dir()

    # Convert to JSON-serializable format
    json_data = {}
    for session_id, session_data in data.items():
        json_data[session_id] = {
            "session_id": session_data.session_id,
            "started_at": session_data.started_at,
            "executions": {
                hook_id: asdict(execution)
                for hook_id, execution in session_data.executions.items()
            },
        }

    try:
        atomic_write_json(HOOK_TRACKER_FILE, json_data)
    except OSError:
        pass  # Silently fail if we can't write


def cleanup_old_sessions(ttl_seconds: int = SESSION_TTL_SECONDS) -> int:
    """Clean up sessions older than TTL.

    Args:
        ttl_seconds: Time-to-live in seconds (default: 24 hours)

    Returns:
        Number of sessions cleaned up
    """
    data = _load_tracker_data()
    if not data:
        return 0

    now = time.time()
    cutoff = now - ttl_seconds
    cleaned = 0

    sessions_to_remove = []
    for session_id, session_data in data.items():
        try:
            started = datetime.fromisoformat(session_data.started_at)
            if started.timestamp() < cutoff:
                sessions_to_remove.append(session_id)
                cleaned += 1
        except (ValueError, AttributeError):
            # Invalid timestamp, remove it
            sessions_to_remove.append(session_id)
            cleaned += 1

    for session_id in sessions_to_remove:
        del data[session_id]

    if cleaned > 0:
        _save_tracker_data(data)

    return cleaned
