#!/usr/bin/env python3
"""PreToolUse hook that locks test files while a fix is in progress.

``/sc:troubleshoot --fix`` writes a failing test, commits it, then applies the
fix. Between those two points the test is the proof that the bug is gone, and
an edit to it — a widened assertion, a skip marker, a deleted case — makes the
fix look done without it being so. A rule line cannot hold that under auto mode, where a fix task edits whatever
stands in its way; a hook on the Edit and Write tools can. A shell edit of a
test file (sed, ``git checkout --``, rm) is outside this lock.

Subcommands (argv, forwarded by ``superclaude hook test_file_guard <sub>``):
  - ``check`` (hooks.json, PreToolUse on Edit|Write; bare argv means the same):
    block when the lock marker exists and ``tool_input.file_path`` is a test
    file, approve otherwise.
  - ``lock`` / ``unlock`` / ``status``: run by hand from the command flow,
    plain stdout.

A test file is any path under a ``tests/`` or ``__tests__/`` directory, or a
basename matching ``test_*.py``, ``*_test.py``, ``*.test.*`` or ``*.spec.*``
(directory names case-insensitive). The rule is path-shaped, not
project-scoped, and names Python and JS conventions only.

The marker is <claude_base>/.superclaude_hooks/test_file_lock_<project_key>:
under ``hook_state_dir()`` so ``superclaude uninstall`` removes it, keyed by
project so a user-scope install locks one project at a time. Fail-open on any
error. Opt out with SUPERCLAUDE_TEST_LOCK=0.

Output matches ``file_size_guard.py`` / ``destructive_guard.py``:
{"decision": "approve"} or {"decision": "block", "reason": ...}.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path, PurePosixPath

from superclaude.utils import hook_state_dir, project_key

_TEST_DIRS = {"tests", "__tests__"}
_UNLOCK = "superclaude hook test_file_guard unlock"
_SUBCOMMANDS = ("check", "lock", "unlock", "status")
_ANCHORS = (".git", os.path.join(".claude", "superclaude"))


def _anchor_project_root() -> None:
    """Pin CLAUDE_PROJECT_DIR for the by-hand subcommands.

    Claude Code sets it for the hook; the Bash tool does not, and project_root()
    then falls back to the CWD, so ``lock`` run from a subdirectory would write a
    marker ``check`` never reads. Walk up to the nearest ``.git`` or
    ``.claude/superclaude`` and pin that, the same anchor the hook resolves.
    """
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return
    here = Path.cwd()
    for candidate in (here, *here.parents):
        if any((candidate / a).exists() for a in _ANCHORS):
            os.environ["CLAUDE_PROJECT_DIR"] = str(candidate)
            return


def _marker() -> Path:
    return hook_state_dir() / f"test_file_lock_{project_key()}"


def is_test_file(file_path: str) -> bool:
    """True for a path the lock protects (see the module docstring)."""
    if not file_path:
        return False
    parts = PurePosixPath(file_path.replace("\\", "/")).parts
    if any(part.lower() in _TEST_DIRS for part in parts[:-1]):
        return True
    name = parts[-1].lower()
    if name.startswith("test_") and name.endswith(".py"):
        return True
    if name.endswith("_test.py"):
        return True
    return ".test." in name or ".spec." in name


def _block_reason(file_path: str) -> str:
    return (
        f"BLOCKED: test files are locked while a fix is in progress — {file_path} "
        "is a test file. The failing test is the proof that the bug is gone, and "
        "a fix task must not weaken the check that proves it (no widened "
        "assertion, skip marker or deleted case). Fix the code under test "
        f"instead. If the test itself is wrong, say so and run `{_UNLOCK}` first."
    )


def _approve() -> None:
    print(json.dumps({"decision": "approve"}))


def _block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))


def _check() -> int:
    try:
        if os.environ.get("SUPERCLAUDE_TEST_LOCK", "1") == "0":
            _approve()
            return 0
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data.strip():
            _approve()
            return 0
        tool_input = json.loads(stdin_data).get("tool_input") or {}
        file_path = str(tool_input.get("file_path") or "")
        if is_test_file(file_path) and _marker().is_file():
            _block(_block_reason(file_path))
            return 0
    except Exception:
        pass  # Fail open — never break the user's flow on a hook error
    _approve()
    return 0


def _lock() -> int:
    marker = _marker()
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()
    print(f"locked: test files are read-only until `{_UNLOCK}` ({marker})")
    return 0


def _unlock() -> int:
    marker = _marker()
    marker.unlink(missing_ok=True)
    print(f"unlocked: test files are editable again ({marker})")
    return 0


def _status() -> int:
    marker = _marker()
    state = "locked" if marker.is_file() else "unlocked"
    print(f"{state} ({marker})")
    return 0


def _usage(prog: str) -> str:
    return (
        f"usage: {prog} [{'|'.join(_SUBCOMMANDS)}]\n\n"
        "check   PreToolUse hook (hooks.json): block Edit/Write on a test file "
        "while locked\n"
        "lock    lock this project's test files (/sc:troubleshoot --fix, once "
        "the failing test is committed)\n"
        "unlock  release the lock (after the fix is verified, or when the test "
        "itself is wrong)\n"
        "status  print locked/unlocked and the marker path\n"
    )


def main(argv: list[str] | None = None, prog: str = "test_file_guard") -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] in ("-h", "--help"):
        sys.stdout.write(_usage(prog))
        return 0
    sub = argv[0] if argv else "check"
    _anchor_project_root()
    if sub not in _SUBCOMMANDS or len(argv) > 1:
        # 1, not 2: an unknown word here is a typo, and exit 2 on PreToolUse
        # would block the tool call (why: cli/hook_dispatch.py docstring).
        sys.stderr.write(
            f"{prog}: unknown subcommand {' '.join(argv)!r}\n\n{_usage(prog)}"
        )
        return 1
    if sub == "check":
        return _check()
    try:
        return {"lock": _lock, "unlock": _unlock, "status": _status}[sub]()
    except OSError as exc:
        sys.stderr.write(f"{prog} {sub}: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
