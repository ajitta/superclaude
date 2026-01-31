#!/usr/bin/env python3
"""SuperClaude SessionStart initialization script (Python)

Auto-executed when Claude Code session starts.
Cross-platform compatible (Windows/macOS/Linux).

v2.1.0 Features:
- Hook session tracking initialization
- Old session cleanup (>24h)

v2.2.0 Features (Claude Code 2.1.20 Integration):
- PR review status indicator display
- Multi-directory CLAUDE.md awareness
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


def get_pr_status() -> str:
    """
    Get PR review status for current branch.

    Integrates with Claude Code 2.1.20's PR status indicator feature.

    Returns:
        Formatted PR status string with colored indicator
    """
    try:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if branch_result.returncode != 0:
            return ""

        current_branch = branch_result.stdout.strip()
        if not current_branch or current_branch in ("main", "master"):
            return ""

        # Check PR status via gh CLI
        pr_result = subprocess.run(
            ["gh", "pr", "view", "--json", "state,reviewDecision,isDraft,url"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if pr_result.returncode != 0:
            return ""

        import json

        pr_data = json.loads(pr_result.stdout)

        # Determine status and indicator
        if pr_data.get("isDraft"):
            indicator = "⚪"  # Gray for draft
            status = "draft"
        else:
            review_decision = pr_data.get("reviewDecision", "")
            if review_decision == "APPROVED":
                indicator = "🟢"  # Green for approved
                status = "approved"
            elif review_decision == "CHANGES_REQUESTED":
                indicator = "🔴"  # Red for changes requested
                status = "changes requested"
            else:
                indicator = "🟡"  # Yellow for pending
                status = "pending review"

        url = pr_data.get("url", "")
        if url:
            return f"{indicator} PR: {status} ({url})"
        return f"{indicator} PR: {status}"

    except FileNotFoundError:
        # gh CLI not installed
        return ""
    except Exception:
        return ""


def get_additional_dirs_status() -> str:
    """
    Check for additional CLAUDE.md directories (monorepo support).

    Returns:
        Status string if additional directories are detected
    """
    import os
    from pathlib import Path

    if os.environ.get("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "0") != "1":
        return ""

    cwd = Path.cwd()
    additional_count = 0

    for pattern in ["packages/*", "apps/*", "libs/*", "services/*"]:
        for subdir in cwd.glob(pattern):
            if subdir.is_dir() and (subdir / "CLAUDE.md").exists():
                additional_count += 1

    if additional_count > 0:
        return f"📁 Multi-dir: {additional_count} additional CLAUDE.md found"
    return ""


def main():
    # 0. Initialize hook tracker (cleanup old sessions)
    init_hook_tracker()

    # 1. Check git status
    print(get_git_status())

    # 2. Check PR status (Claude Code 2.1.20+)
    pr_status = get_pr_status()
    if pr_status:
        print(pr_status)

    # 3. Check for additional directories (monorepo)
    additional_dirs = get_additional_dirs_status()
    if additional_dirs:
        print(additional_dirs)

    # 4. Remind token budget
    print("💡 Use /context to confirm token budget.")

    # 5. Report core services
    print()
    print("🛠️ Core Services Available:")
    print("  ✅ Confidence Check (pre-implementation validation)")
    print("  ✅ Deep Research (web/MCP integration)")
    print("  ✅ Repository Index (token-efficient exploration)")
    print("  ✅ PR Status Check (Claude Code 2.1.20+)")
    print("  ✅ Task Auto-Cleanup (stale task removal)")
    print()
    print("SC Agent ready — awaiting task assignment.")


if __name__ == "__main__":
    main()
    sys.exit(0)
