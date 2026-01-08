#!/usr/bin/env python3
"""SuperClaude SessionStart initialization script (Python)

Auto-executed when Claude Code session starts.
Cross-platform compatible (Windows/macOS/Linux).

v2.1.0 Features:
- Hook session tracking initialization
- Old session cleanup (>24h)
"""

from __future__ import annotations

import subprocess
import sys


def init_hook_tracker() -> str | None:
    """Initialize hook tracker and cleanup old sessions.

    Returns:
        Session ID or None if tracker unavailable
    """
    try:
        from superclaude.hooks.hook_tracker import (
            cleanup_old_sessions,
            get_session_id,
        )

        # Cleanup old sessions (>24h)
        cleaned = cleanup_old_sessions()
        if cleaned > 0:
            print(f"🧹 Cleaned {cleaned} old hook session(s)")

        # Get/create current session
        session_id = get_session_id()
        return session_id
    except ImportError:
        return None


def get_git_status():
    """Check git status and return formatted string."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            status = result.stdout.strip()
            if not status:
                return "📊 Git: clean"
            count = len([line for line in status.split("\n") if line])
            return f"📊 Git: {count} files"
        return "📊 Git: not a repo"
    except Exception:
        return "📊 Git: not a repo"


def main():
    # 0. Initialize hook tracker (cleanup old sessions)
    init_hook_tracker()

    # 1. Check git status
    print(get_git_status())

    # 2. Remind token budget
    print("💡 Use /context to confirm token budget.")

    # 3. Report core services
    print()
    print("🛠️ Core Services Available:")
    print("  ✅ Confidence Check (pre-implementation validation)")
    print("  ✅ Deep Research (web/MCP integration)")
    print("  ✅ Repository Index (token-efficient exploration)")
    print()
    print("SC Agent ready — awaiting task assignment.")


if __name__ == "__main__":
    main()
    sys.exit(0)
