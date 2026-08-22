"""Shared utility functions for SuperClaude.

Runtime paths resolve here and nowhere else. Two classes, opposite lifetimes:

- Ephemeral machine state (context caches, trackers, circuit-breaker counters)
  lives under ``hook_state_dir()`` so ``superclaude uninstall`` removes it with
  the rest of the scope.
- Durable project data the user owns (``insights.jsonl``) lives under
  ``project_root() / ".claude"`` so uninstall preserves it.

``os.getcwd()``, ``Path.cwd()`` and CWD-relative literals are bugs in hook and
script code — hook CWD is not guaranteed to be the project root. See
`.claude/rules/gotchas/hooks.md`.
"""

import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any


def atomic_write_json(path: Path, data: Any, indent: int = 2) -> None:
    """Write JSON data atomically using temp file + os.replace.

    Prevents data corruption from crashes during write by writing to
    a temporary file first, then atomically replacing the target.

    Args:
        path: Target file path
        data: JSON-serializable data
        indent: JSON indentation level
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=indent)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def get_skill_directories() -> list[Path]:
    """Get all skill directories to scan.

    Project-local skills are found via project_root(), not the CWD: a hook
    running from a subdirectory used to see only user-scope skills, so the
    installed-skill count under-reported project and local scope installs.

    Returns:
        List of skill base directories (global, project-local)
    """
    return [
        Path.home() / ".claude" / "skills",
        project_root() / ".claude" / "skills",
    ]


def project_root() -> Path:
    """Project root for hook-relative paths.

    Hook CWD is not guaranteed to be the project root, so $CLAUDE_PROJECT_DIR is
    the anchor whenever Claude Code provides it. See the hooks reference at
    'https://code.claude.com/docs/en/hooks'.

    Returns:
        $CLAUDE_PROJECT_DIR if set, else the current working directory
    """
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())


def claude_base() -> Path:
    """Resolve the .claude directory of the install whose hooks are running.

    Project and local scope keep framework content under
    ``<project>/.claude/superclaude``, so its presence identifies the active
    scope. User scope is the fallback.

    Returns:
        Project-local .claude when a scoped install is present, else ~/.claude
    """
    root = project_root() / ".claude"
    if (root / "superclaude").exists():
        return root
    return Path.home() / ".claude"


def hook_state_dir() -> Path:
    """Runtime state directory for hook scripts, scoped to the active install.

    Keeping state under the install's own .claude means a local-scope install
    leaves no footprint in ~/.claude, and ``superclaude uninstall`` can remove it
    with the rest of the scope.

    Returns:
        <claude_base>/.superclaude_hooks
    """
    return claude_base() / ".superclaude_hooks"


# How long unused runtime state is kept. Everything under hook_state_dir() is a
# rebuildable cache, so the only cost of collecting one too early is that the
# next prompt re-injects a context or re-arms a hint.
STATE_MAX_AGE_DAYS = 7

# Filenames the sweep owns. Anything else sharing the directory is left alone —
# the state dir is SuperClaude's, but deleting by prefix rather than by directory
# means a file put there deliberately later is not collected by surprise.
_PRUNABLE_PREFIXES = (
    "claude_context_",
    "loop_guard_",
    "hook_tracker",
    "current_session",
    "insight_prompt_",
    "insight_baseline_",
)

# The fallback ledger is pruned entry by entry, not deleted: one live session's
# entry has to survive a sweep triggered by another.
FALLBACK_LEDGER_NAME = "mcp_fallbacks.json"

# MCP servers still in the roster. Hints for anything else are dead weight —
# a real ledger still carried `magic` and `morphllm` months after both were
# dropped. Kept here rather than imported from superclaude.hooks.mcp_fallback so
# this module stays dependency-free, and asserted equal by the test suite.
CURRENT_MCP_SERVERS = frozenset(
    {"context7", "tavily", "sequential", "serena", "playwright", "devtools"}
)


def prune_hook_state(max_age_days: float = STATE_MAX_AGE_DAYS) -> int:
    """Delete rebuildable state files nothing has touched in max_age_days.

    loop_guard already prunes entries *inside* its file; nothing pruned the files
    themselves, so one accumulated per project key and per test run — 50 of them
    in a real user-scope directory, the oldest naming a project that no longer
    exists.

    Args:
        max_age_days: Age past which an untouched state file is collected

    Returns:
        Number of files removed
    """
    directory = hook_state_dir()
    cutoff = time.time() - max_age_days * 86400
    removed = 0
    try:
        entries = list(directory.iterdir())
    except OSError:
        return 0

    for path in entries:
        if path.name == FALLBACK_LEDGER_NAME:
            continue
        if not path.name.startswith(_PRUNABLE_PREFIXES):
            continue
        try:
            if not path.is_file() or path.stat().st_mtime >= cutoff:
                continue
            path.unlink()
            removed += 1
        except OSError:
            continue
    return removed


def prune_fallback_ledger(
    session_id: str | None = None, max_age_days: float = STATE_MAX_AGE_DAYS
) -> bool:
    """Drop dead sessions and retired servers from the MCP fallback ledger.

    The ledger gains one entry per session and shed none, so it grew for the life
    of the install while carrying keys from an id scheme retired months earlier.

    Pruned by age rather than by "anything but the current session": a sweep in
    one window must not delete the ledger entry of another window that is still
    open, which would re-show every hint that session had already seen — the same
    starvation the context cache had.

    Args:
        session_id: Session to keep regardless of its age, if any
        max_age_days: Age past which a session's entry is dropped

    Returns:
        True if the ledger was rewritten
    """
    path = hook_state_dir() / FALLBACK_LEDGER_NAME
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(data, dict):
        return False

    cutoff = time.time() - max_age_days * 86400
    pruned: dict[str, dict[str, str]] = {}
    for key, hints in data.items():
        if not isinstance(hints, dict):
            continue
        live = {
            server: stamp
            for server, stamp in hints.items()
            if server in CURRENT_MCP_SERVERS
        }
        if not live:
            continue
        if key == session_id:
            pruned[key] = live
            continue
        if _newest_stamp(live) >= cutoff:
            pruned[key] = live

    if pruned == data:
        return False
    try:
        atomic_write_json(path, pruned)
    except OSError:
        return False
    return True


def _newest_stamp(hints: dict[str, str]) -> float:
    """Most recent ISO timestamp in a ledger entry, as epoch seconds (0 if none)."""
    from datetime import datetime

    newest = 0.0
    for stamp in hints.values():
        try:
            newest = max(newest, datetime.fromisoformat(stamp).timestamp())
        except (TypeError, ValueError):
            continue
    return newest


def session_slug(session_id: str | None) -> str | None:
    """Filename-safe form of a Claude Code session id, or None if unusable.

    Session ids arrive on hook stdin, so they are stripped to characters that
    cannot escape the state directory before being used as a path component.

    Args:
        session_id: Raw session id from hook stdin, or None

    Returns:
        Sanitised slug, or None when nothing usable remains
    """
    if not session_id:
        return None
    slug = re.sub(r"[^A-Za-z0-9_-]", "", session_id)[:64]
    return slug or None


def context_cache_file(session_id: str | None = None) -> Path:
    """Path to context_loader's dedup cache for one (project, session).

    Two Claude Code windows open on one repository are two sessions. Keying this
    file on the project alone let whichever session triggered a context first
    mark it loaded for both, starving the second of every context it should have
    received. Callers holding no session id get the project-only name, which is
    also the filename used before session keying.

    Args:
        session_id: Raw session id from hook stdin, or None

    Returns:
        <hook_state_dir>/claude_context_<project_key>[_<session>].txt
    """
    slug = session_slug(session_id)
    suffix = f"_{slug}" if slug else ""
    return hook_state_dir() / f"claude_context_{project_key()}{suffix}.txt"


def project_key() -> str:
    """Stable short id for the active project, for per-project state filenames.

    User-scope installs share one ``hook_state_dir()`` across every project, so
    state that is not session-keyed needs this in its filename to stop two
    projects contaminating each other. Anchored on ``project_root()`` rather
    than the CWD so a hook firing from a subdirectory resolves the same id.

    Returns:
        First 8 hex chars of the MD5 of the project root path
    """
    # usedforsecurity=False: this is a filename discriminator, not a digest, and
    # bare md5() raises under a FIPS-enforcing Python build.
    return hashlib.md5(str(project_root()).encode(), usedforsecurity=False).hexdigest()[
        :8
    ]
