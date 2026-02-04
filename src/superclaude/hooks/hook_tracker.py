"""Hook Execution Tracker for SuperClaude v2.1.0

Tracks hook executions per session to support `once: true` functionality.
Prevents duplicate execution of hooks marked with once=true within a session.

Session Management:
- Session ID is generated at SessionStart or derived from environment
- Hook executions are logged with timestamps
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
from typing import Literal

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
    hook_type: Literal["PreToolUse", "PostToolUse", "Stop", "SessionStart", "UserPromptSubmit"]
    executed_at: str  # ISO format timestamp
    source: str  # File that defined the hook (skill name or hooks.json)


@dataclass
class SessionData:
    """Session tracking data."""

    session_id: str
    started_at: str
    executions: dict[str, HookExecution] = field(default_factory=dict)


def get_session_id() -> str:
    """Get or generate the current session ID.

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


def _generate_hook_id(
    hook_type: str,
    command: str,
    source: str,
    matcher: str | None = None,
) -> str:
    """Generate a unique ID for a hook.

    Args:
        hook_type: Type of hook (PreToolUse, PostToolUse, etc.)
        command: The hook command
        source: Source file/skill that defined the hook
        matcher: Optional tool matcher pattern

    Returns:
        Unique hook identifier
    """
    raw = f"{hook_type}:{source}:{command}"
    if matcher:
        raw += f":{matcher}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


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


def has_executed_once(
    hook_type: str,
    command: str,
    source: str,
    matcher: str | None = None,
    session_id: str | None = None,
) -> bool:
    """Check if a hook has already been executed in the current session.

    Args:
        hook_type: Type of hook (PreToolUse, PostToolUse, etc.)
        command: The hook command
        source: Source file/skill that defined the hook
        matcher: Optional tool matcher pattern
        session_id: Optional explicit session ID (uses current if not provided)

    Returns:
        True if hook has already been executed, False otherwise
    """
    if session_id is None:
        session_id = get_session_id()

    hook_id = _generate_hook_id(hook_type, command, source, matcher)
    data = _load_tracker_data()

    session_data = data.get(session_id)
    if session_data is None:
        return False

    return hook_id in session_data.executions


def mark_executed(
    hook_type: str,
    command: str,
    source: str,
    matcher: str | None = None,
    session_id: str | None = None,
) -> None:
    """Mark a hook as executed in the current session.

    Args:
        hook_type: Type of hook (PreToolUse, PostToolUse, etc.)
        command: The hook command
        source: Source file/skill that defined the hook
        matcher: Optional tool matcher pattern
        session_id: Optional explicit session ID (uses current if not provided)
    """
    if session_id is None:
        session_id = get_session_id()

    hook_id = _generate_hook_id(hook_type, command, source, matcher)
    data = _load_tracker_data()

    # Get or create session data
    if session_id not in data:
        data[session_id] = SessionData(
            session_id=session_id,
            started_at=datetime.now().isoformat(),
        )

    # Record execution
    data[session_id].executions[hook_id] = HookExecution(
        hook_id=hook_id,
        hook_type=hook_type,
        executed_at=datetime.now().isoformat(),
        source=source,
    )

    _save_tracker_data(data)


def should_execute_hook(
    hook_type: str,
    command: str,
    source: str,
    once: bool = False,
    matcher: str | None = None,
) -> bool:
    """Determine if a hook should be executed.

    Args:
        hook_type: Type of hook
        command: The hook command
        source: Source file/skill
        once: Whether hook is marked as once-per-session
        matcher: Optional tool matcher

    Returns:
        True if hook should be executed, False if it should be skipped
    """
    if not once:
        return True

    return not has_executed_once(hook_type, command, source, matcher)


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


def reset_session() -> str:
    """Reset the current session (start a new one).

    Returns:
        New session ID
    """
    # Remove cached session file
    if SESSION_FILE.exists():
        try:
            SESSION_FILE.unlink()
        except OSError:
            pass  # Best-effort: new session will be generated regardless

    # Clear any environment variable cache
    if "CLAUDE_SESSION_ID" in os.environ:
        del os.environ["CLAUDE_SESSION_ID"]

    # Generate and return new session
    return get_session_id()


def get_session_stats() -> dict:
    """Get statistics about the current session.

    Returns:
        Dictionary with session statistics
    """
    session_id = get_session_id()
    data = _load_tracker_data()

    session_data = data.get(session_id)
    if session_data is None:
        return {
            "session_id": session_id,
            "started_at": None,
            "hooks_executed": 0,
            "hook_types": {},
        }

    # Count by hook type
    hook_types: dict[str, int] = {}
    for execution in session_data.executions.values():
        hook_type = execution.hook_type
        hook_types[hook_type] = hook_types.get(hook_type, 0) + 1

    return {
        "session_id": session_id,
        "started_at": session_data.started_at,
        "hooks_executed": len(session_data.executions),
        "hook_types": hook_types,
    }


# Convenience function for CLI/scripts
def check_and_mark(
    hook_type: str,
    command: str,
    source: str,
    once: bool = False,
    matcher: str | None = None,
) -> bool:
    """Check if hook should execute and mark it if so - optimized single I/O.

    Atomic operation that checks and marks in one call with single load/save.

    Args:
        hook_type: Type of hook
        command: The hook command
        source: Source file/skill
        once: Whether hook is marked as once-per-session
        matcher: Optional tool matcher

    Returns:
        True if hook should execute (and was marked), False otherwise
    """
    if not once:
        return True

    session_id = get_session_id()
    hook_id = _generate_hook_id(hook_type, command, source, matcher)

    # Single load
    data = _load_tracker_data()

    # Check if already executed
    session_data = data.get(session_id)
    if session_data and hook_id in session_data.executions:
        return False

    # Mark as executed
    if session_id not in data:
        data[session_id] = SessionData(
            session_id=session_id,
            started_at=datetime.now().isoformat(),
        )

    data[session_id].executions[hook_id] = HookExecution(
        hook_id=hook_id,
        hook_type=hook_type,
        executed_at=datetime.now().isoformat(),
        source=source,
    )

    # Single save
    _save_tracker_data(data)
    return True
