#!/usr/bin/env python3
"""SuperClaude SessionStart initialization script (Python)
Auto-executed when Claude Code session starts
Cross-platform compatible (Windows/macOS/Linux)
"""
import subprocess
import sys


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
