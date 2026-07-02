#!/usr/bin/env python3
"""PreToolUse hook that blocks irreversibly destructive shell commands.

Python reimplementation of the former inline ``jq | head | grep`` shell guard
(``hooks.json`` Bash matcher), which silently **failed open** on any platform
missing jq/grep/head — notably the project's primary stock-Windows + fresh-venv
test baseline (``CLAUDE.md``). This version depends only on the Python stdlib —
the same runtime the other safety hooks already require — so it cannot fail open
because an external tool is absent.

Blocks:
  - ``rm -rf /``    — wipe filesystem root
  - ``rm -rf /*``   — wipe everything under root
  - force-push to ``main``/``master`` — via ``--force`` OR the ``-f`` shorthand,
    with the force flag and the branch name in either order (the original regex
    only caught ``--force`` appearing *before* the branch name; 2026-07-02
    live-test found ``git push -f origin main`` sailed through)

``--force-with-lease`` (safe force-push) is allowed by construction: the
``--force`` branch requires the following character to NOT be a hyphen, and
the ``-f`` branch requires a standalone token (not the ``-f`` inside
``--force-with-lease``).

Respects ``SUPERCLAUDE_DESTRUCTIVE_GUARD=0`` to disable.
Outputs structured JSON for the Claude Code PreToolUse hook protocol, matching
``file_size_guard.py`` ({"decision": "approve" | "block", "reason": ...}).
"""
import json
import os
import re
import sys

# rm patterns mirror the original hooks.json shell regex verbatim.
# Force-push pattern (widened 2026-07-02): lookaheads accept the force flag
# (--force, not --force-with-lease; or standalone -f) and main/master in ANY
# argument order — the original `--force ... main` ordering missed both
# `git push -f origin main` and `git push origin main --force`.
_DESTRUCTIVE = re.compile(
    r"rm\s+-rf\s+/\s*$"
    r"|rm\s+-rf\s+/\*"
    r"|git\s+push\b(?=.*(?:--force(?!-)|(?<!\S)-f\b))(?=.*\b(?:main|master)\b)"
)

_BLOCK_REASON = "BLOCKED: destructive command detected (--force-with-lease is allowed)"


def is_destructive(command: str) -> bool:
    """Return True if the command matches a known irreversible-destruction pattern."""
    if not command:
        return False
    return _DESTRUCTIVE.search(command) is not None


def main() -> None:
    # Respect opt-out env var
    if os.environ.get("SUPERCLAUDE_DESTRUCTIVE_GUARD", "1") == "0":
        print(json.dumps({"decision": "approve"}))
        return

    try:
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data:
            print(json.dumps({"decision": "approve"}))
            return

        data = json.loads(stdin_data)
        command = data.get("tool_input", {}).get("command", "")

        if is_destructive(command):
            print(json.dumps({"decision": "block", "reason": _BLOCK_REASON}))
            return

        print(json.dumps({"decision": "approve"}))

    except json.JSONDecodeError:
        # Malformed hook input — fail open (consistent with file_size_guard/loop_guard)
        print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
