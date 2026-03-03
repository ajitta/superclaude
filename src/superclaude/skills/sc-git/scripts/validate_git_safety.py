#!/usr/bin/env python3
"""sc:git PreToolUse safety validation.

Reads tool_input from stdin (JSON), checks git command safety.
Exit 0 = allow, Exit 2 = block.
"""

import json
import re
import sys


def main():
    try:
        tool_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    # BLOCK: force push to main/master
    # Covers: --force, -f, --force-with-lease, and +ref refspec syntax
    is_push = re.search(r"git\s+push\b", command)
    targets_protected = re.search(r"\b(main|master)\b", command) if is_push else None
    has_force = re.search(r"git\s+push\s+.*?(--force\b|\s-f\b)", command) if is_push else None
    has_refspec_force = re.search(r"\+\s*(main|master)\b", command) if is_push else None

    if is_push and targets_protected and (has_force or has_refspec_force):
        print("BLOCKED: Force push to main/master is not allowed. "
              "Create a feature branch and open a PR instead.", file=sys.stderr)
        sys.exit(2)

    # WARN: destructive operations (allow but inform)
    warn_patterns = [
        (r"git\s+push\s+.*--force-with-lease", "git push --force-with-lease can overwrite remote commits"),
        (r"git\s+reset\s+--hard", "git reset --hard will discard uncommitted changes"),
        (r"git\s+clean\s+-f", "git clean -f will permanently delete untracked files"),
        (r"git\s+checkout\s+--\s+\.", "git checkout -- . will discard all unstaged changes"),
        (r"git\s+branch\s+-D", "git branch -D will force-delete the branch"),
        (r"git\s+rebase(?!\s+-i)", "git rebase can rewrite history — ensure you understand the implications"),
    ]

    for pattern, message in warn_patterns:
        if re.search(pattern, command):
            print(f"WARNING: {message}", file=sys.stderr)
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
