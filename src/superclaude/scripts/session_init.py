#!/usr/bin/env python3
"""SuperClaude SessionStart initialization script (Python)

Auto-executed when Claude Code session starts.
Cross-platform compatible (Windows/macOS/Linux).

v2.2.0 Features (Claude Code 2.1.20 Integration):
- PR review status indicator display
"""

from __future__ import annotations

import json
import subprocess
import sys


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
        from superclaude.utils import claude_base, detect_scope
    except ImportError:
        return "⚠️ SuperClaude: install status unavailable"

    base = claude_base()
    # A two-way user/project test reported a local install as "project scope".
    # The two share <project>/.claude, so only detect_scope() separates them.
    scope = detect_scope()

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


def main() -> None:
    # The context cache reset belongs to context_reset.py, the other SessionStart
    # hook: it reads the session id off stdin, and this one does not. Calling it
    # from here passed no id, so it deleted the project-only fallback cache that
    # a concurrent session without an id is using.

    # 1. Check PR status (Claude Code 2.1.20+)
    pr_status = get_pr_status()
    if pr_status:
        print(pr_status)

    # 2. What is actually installed
    print(get_install_status())


if __name__ == "__main__":
    main()
    sys.exit(0)
