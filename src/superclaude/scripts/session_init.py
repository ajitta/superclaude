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

import json
import subprocess
import sys
from pathlib import Path


def get_install_status() -> str:
    """One line describing the install that is actually present.

    Replaces five checkmarks printed unconditionally on every startup, naming
    capabilities nothing had checked. The framework was absent from user scope
    for months while that block reported it ready; a count read off disk is the
    line that would have said so on the first day.

    Returns:
        A single status line, never empty
    """
    try:
        from superclaude.utils import claude_base
    except ImportError:
        return "⚠️ SuperClaude: install status unavailable"

    base = claude_base()
    scope = "user" if base == Path.home() / ".claude" else "project"

    def _count(*parts: str) -> int:
        directory = base.joinpath(*parts)
        try:
            return sum(1 for f in directory.glob("*.md") if f.stem.upper() != "README")
        except OSError:
            return 0

    commands = _count("commands", "sc")
    agents = _count("agents")

    if not commands:
        return (
            f"⚠️ SuperClaude: no commands installed at {scope} scope "
            f"({base}) — run `superclaude install`"
        )

    agent_word = "agent" if agents == 1 else "agents"
    return f"🛠️ SuperClaude: {commands} commands, {agents} {agent_word} ({scope} scope)"


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
            print(f"🧹 Cleaned {cleaned} old hook session(s)", file=sys.stderr)

        # Get/create current session
        session_id = get_session_id()
        return session_id
    except ImportError:
        return None


def get_git_status() -> str:
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
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError):
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
    except (
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
        OSError,
        json.JSONDecodeError,
        KeyError,
    ):
        return ""


def get_additional_dirs_status() -> str:
    """
    Check for additional CLAUDE.md directories (monorepo support).

    Returns:
        Status string if additional directories are detected
    """
    import os

    from superclaude.utils import project_root

    if os.environ.get("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "0") != "1":
        return ""

    # project_root(), not Path.cwd(): a hook firing from a subdirectory would
    # otherwise scan the wrong tree and under-report the workspace count.
    root = project_root()
    additional_count = 0

    for pattern in ["packages/*", "apps/*", "libs/*", "services/*"]:
        for subdir in root.glob(pattern):
            if subdir.is_dir() and (subdir / "CLAUDE.md").exists():
                additional_count += 1

    if additional_count > 0:
        return f"📁 Multi-dir: {additional_count} additional CLAUDE.md found"
    return ""


def main() -> None:
    # The context cache reset belongs to context_reset.py, the other SessionStart
    # hook: it reads the session id off stdin, and this one does not. Calling it
    # from here passed no id, so it deleted the project-only fallback cache that
    # a concurrent session without an id is using.

    # 1. Initialize hook tracker (cleanup old sessions)
    init_hook_tracker()

    # 2. Check git status
    print(get_git_status())

    # 3. Check PR status (Claude Code 2.1.20+)
    pr_status = get_pr_status()
    if pr_status:
        print(pr_status)

    # 4. Check for additional directories (monorepo)
    additional_dirs = get_additional_dirs_status()
    if additional_dirs:
        print(additional_dirs)

    # 5. Remind token budget
    print("💡 Use /context to confirm token budget.")

    # 6. What is actually installed
    print(get_install_status())


if __name__ == "__main__":
    main()
    sys.exit(0)
