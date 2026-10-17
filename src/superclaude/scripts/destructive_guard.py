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

Warns (roadmap 0-3 warn-tier, shipped 2026-07-03 after the eval matrix
recorded a live ``git clean -fd`` execution that only a hook could catch):
  - ``git reset --hard``  — discards working tree + index
  - ``git clean -f*`` / ``--force`` — deletes untracked files
  - ``git branch -D`` / ``--delete --force`` — drops unmerged branch
These are legitimate often enough that a hard block is wrong; they emit
``hookSpecificOutput.permissionDecision: "ask"`` (verified supported on
CC 2.1.198) so interactive sessions get a confirm prompt with the reason,
and headless ``-p`` sessions resolve ask -> deny. Known limitation shared
with the deny tier: patterns match anywhere in the command string, so a
quoted mention (e.g. in a commit message) can trigger a spurious confirm —
cost is one prompt, never a lost command.

Respects ``SUPERCLAUDE_DESTRUCTIVE_GUARD=0`` to disable (both tiers).
Deny tier outputs legacy PreToolUse JSON ({"decision": "block", "reason": ...});
warn tier outputs the ``hookSpecificOutput`` schema (the only shape that carries
"ask"). A command that matches neither tier gets **no output**: the official
hooks reference maps the legacy ``"approve"`` to ``permissionDecision:
"allow"``, which skips Claude Code's own permission prompt, so printing it on
every ordinary command would turn the prompt off for all of Bash. Silence
leaves the decision to the normal permission flow.
"""

import json
import os
import re

from superclaude.utils import read_hook_input

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

# Warn tier: reversible-but-risky. `git clean` needs a standalone -f cluster
# (-f/-fd/-xfd) or --force, AND no dry-run flag — with both, git runs the
# preview, and the 2026-07-03 live probe showed `-fdxn` dry-run is the model's
# natural first move (gating it just adds a pointless prompt). Known limit:
# the dry-run lookahead scans the whole command string, so a chained
# `git clean -fd && git clean -n` escapes the warn — regex-on-string tradeoff,
# prose/deny tiers still apply. `git branch` needs capital -D (lowercase -d is
# the merged-only safe delete) or the --delete --force long form either order.
_WARN = re.compile(
    r"git\s+reset\b.*--hard\b"
    r"|git\s+clean\b(?!.*(?:(?<!\S)-[A-Za-z]*n[A-Za-z]*\b|--dry-run\b))"
    r"(?=.*(?:(?<!\S)-[A-Za-z]*f[A-Za-z]*\b|--force\b))"
    r"|git\s+branch\b(?=.*(?:(?<!\S)-D\b|--delete\b.*--force\b|--force\b.*--delete\b))"
)

_BLOCK_REASON = "BLOCKED: destructive command detected (--force-with-lease is allowed)"

_WARN_REASON = (
    "CONFIRM: reversible-but-risky command (git reset --hard / clean -f / "
    "branch -D class) — it discards work that is recoverable only until it runs. "
    "Safer alternatives: git stash, a backup branch, or `git clean -n` dry-run. "
    "Proceed only with explicit user confirmation."
)


def is_destructive(command: str) -> bool:
    """Return True if the command matches a known irreversible-destruction pattern."""
    if not command:
        return False
    return _DESTRUCTIVE.search(command) is not None


def is_warn(command: str) -> bool:
    """Return True if the command is reversible-but-risky (warn tier, ask first)."""
    if not command:
        return False
    return _WARN.search(command) is not None


def main() -> None:
    # Respect opt-out env var. Disabled, empty-stdin, allowed and malformed
    # paths all print nothing — see the module docstring.
    if os.environ.get("SUPERCLAUDE_DESTRUCTIVE_GUARD", "1") == "0":
        return

    data = read_hook_input()
    if data is None:
        return
    command = data.get("tool_input", {}).get("command", "")

    if is_destructive(command):
        print(json.dumps({"decision": "block", "reason": _BLOCK_REASON}))
        return

    if is_warn(command):
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "ask",
                        "permissionDecisionReason": _WARN_REASON,
                    }
                }
            )
        )


if __name__ == "__main__":
    main()
