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


PR_STATUS_TTL_SECONDS = 600


def _pr_cache_path():
    """Cache file for the rendered PR status line, one entry per branch.

    Ephemeral, regenerable state, so it lives under ``hook_state_dir()`` where
    ``superclaude uninstall`` reaches it. Keyed by ``project_key()`` because a
    user-scope install shares one state directory across every project.
    """
    from superclaude.utils import hook_state_dir, project_key

    return hook_state_dir() / f"pr_status_{project_key()}.json"


def _read_pr_cache(branch: str) -> str | None:
    """Return the cached line for this branch, or None if absent or stale."""
    import time

    try:
        path = _pr_cache_path()
        if not path.is_file():
            return None
        entry = json.loads(path.read_text(encoding="utf-8")).get(branch)
        if not isinstance(entry, dict):
            return None
        ts = entry.get("ts")
        if not isinstance(ts, (int, float)):
            return None
        if time.time() - ts > PR_STATUS_TTL_SECONDS:
            return None
        line = entry.get("line")
        return line if isinstance(line, str) else None
    except (OSError, json.JSONDecodeError, AttributeError, ImportError):
        return None


def _write_pr_cache(branch: str, line: str) -> None:
    """Store the rendered line for this branch. Fail-open on any error."""
    import time

    try:
        from superclaude.utils import atomic_write_json

        path = _pr_cache_path()
        data = {}
        if path.is_file():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data = loaded
            except (OSError, json.JSONDecodeError):
                data = {}
        data[branch] = {"ts": time.time(), "line": line}
        atomic_write_json(path, data)
    except (OSError, ImportError, TypeError):
        pass


def get_pr_status() -> str:
    """
    Get PR review status for current branch.

    Integrates with Claude Code 2.1.20's PR status indicator feature.

    The ``gh pr view`` call is a network round-trip to GitHub measured at 552ms,
    paid on every session start on a feature branch — the single largest hook
    cost in the framework. The rendered line is cached per branch for
    PR_STATUS_TTL_SECONDS so most session starts skip the network entirely. The
    empty result is cached too: a branch with no PR would otherwise pay the full
    round-trip every time to learn nothing.

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

        cached = _read_pr_cache(current_branch)
        if cached is not None:
            return cached

        # Check PR status via gh CLI
        pr_result = subprocess.run(
            ["gh", "pr", "view", "--json", "state,reviewDecision,isDraft,url"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if pr_result.returncode != 0:
            _write_pr_cache(current_branch, "")
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
        line = (
            f"{indicator} PR: {status} ({url})" if url else f"{indicator} PR: {status}"
        )
        _write_pr_cache(current_branch, line)
        return line

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
