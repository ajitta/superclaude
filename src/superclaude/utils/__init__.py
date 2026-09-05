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

import json
import os
import re
import time
from pathlib import Path
from typing import Any

# `hashlib` and `tempfile` are imported inside the two functions that use them.
# Every hook script pays this module's import cost on every tool call, and
# `tempfile` alone is 3.0ms of it — spent even on the read-only PreToolUse paths
# that never write state. Keep new module-level imports out of here for the same
# reason.


def atomic_write_json(path: Path, data: Any, indent: int = 2) -> None:
    """Write JSON data atomically using temp file + os.replace.

    Prevents data corruption from crashes during write by writing to
    a temporary file first, then atomically replacing the target.

    Args:
        path: Target file path
        data: JSON-serializable data
        indent: JSON indentation level
    """
    import tempfile

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


def main_worktree_root(root: Path) -> Path | None:
    """Main worktree of ``root``, when ``root`` is a linked git worktree.

    A linked worktree's ``.git`` is a file holding ``gitdir: <path>``; that
    gitdir holds a ``commondir`` file pointing at the main worktree's git
    directory, whose parent is the main worktree itself. Both hops are plain
    file reads — no ``git`` subprocess, because this sits in the startup path
    of every hook.

    ``commondir`` may be absolute, so the answer can point anywhere on disk —
    linked worktrees legitimately live far from their repository, which is why
    the result is not constrained to the project tree. The caller gates on an
    install actually existing there, and ``claude_base()`` already trusts
    project-local content, so this widens WHERE that trust may point rather than
    what is trusted. Deliberate, and the reason a bare ``.git`` pointer alone is
    never enough.

    Returns:
        The main worktree's root, or None for a plain checkout, a
        non-repository, or a malformed pointer chain
    """
    pointer = root / ".git"
    try:
        if not pointer.is_file():
            return None
        text = pointer.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    prefix = "gitdir:"
    if not text.startswith(prefix):
        return None
    git_dir = Path(text[len(prefix) :].strip())
    if not git_dir.is_absolute():
        git_dir = (root / git_dir).resolve()
    try:
        common = (git_dir / "commondir").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not common:
        return None
    common_dir = Path(common)
    if not common_dir.is_absolute():
        common_dir = (git_dir / common_dir).resolve()
    return common_dir.parent


def claude_base() -> Path:
    """Resolve the .claude directory of the install whose hooks are running.

    Project and local scope keep framework content under
    ``<project>/.claude/superclaude``, so its presence identifies the active
    scope. A linked git worktree is checked against its main worktree before
    user scope: Claude Code reads the settings file that registered these hooks
    from the MAIN worktree while setting $CLAUDE_PROJECT_DIR to the linked one,
    so the two anchors disagree there and the install lives at the main root.
    Falling straight to ~/.claude instead is silent — content and hook state
    resolve to a directory that usually holds no install at all.

    ``project_root()`` deliberately keeps pointing at the linked worktree: code
    and content follow the install, per-project data follows the session.

    Returns:
        Project-local .claude when a scoped install is present, the main
        worktree's when this is a linked worktree carrying one, else ~/.claude
    """
    root = project_root() / ".claude"
    if (root / "superclaude").exists():
        return root
    main_root = main_worktree_root(project_root())
    if main_root is not None:
        main_base = main_root / ".claude"
        if (main_base / "superclaude").exists():
            return main_base
    return Path.home() / ".claude"


# Markers identifying a hook registration as SuperClaude's. Hoisted here from
# install_settings because scope detection needs the same judgement: which
# settings file the *installer* wrote is the only signal that separates local
# from project scope reliably. Every marker is anchored — bare script names like
# "session_init" would misclassify a user's own hook as ours.
SUPERCLAUDE_HOOK_MARKERS = [
    "[superclaude]",
    "{{SCRIPTS_PATH}}",  # unresolved template form of the scripts path
    "BLOCKED: destructive",  # legacy inline destructive-Bash blocker command
]

# Resolved {{SCRIPTS_PATH}} form: a command referencing a script under a
# superclaude scripts directory (absolute user-scope path or
# $CLAUDE_PROJECT_DIR/.claude/superclaude/scripts; / or \ separators).
_SC_SCRIPTS_PATH_RE = re.compile(r"superclaude[/\\]scripts[/\\]")


def is_superclaude_hook(hook_entry: dict) -> bool:
    """Whether a settings hook entry belongs to SuperClaude.

    Args:
        hook_entry: A hook entry dict with a "hooks" array

    Returns:
        True if any hook command references a SuperClaude scripts path
        (template or resolved) or carries an anchored SuperClaude marker, or a
        `_comment` carries the `[superclaude]` tag
    """
    comment = hook_entry.get("_comment", "")
    if any(marker in comment for marker in SUPERCLAUDE_HOOK_MARKERS):
        return True

    for hook in hook_entry.get("hooks", []):
        cmd = hook.get("command", "")
        if any(marker in cmd for marker in SUPERCLAUDE_HOOK_MARKERS):
            return True
        if _SC_SCRIPTS_PATH_RE.search(cmd):
            return True
        inner_comment = hook.get("_comment", "")
        if any(marker in inner_comment for marker in SUPERCLAUDE_HOOK_MARKERS):
            return True
    return False


def _has_superclaude_hooks(settings_file: Path) -> bool:
    """Whether a settings file carries at least one SuperClaude hook entry."""
    try:
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    if not isinstance(settings, dict):
        return False
    hooks = settings.get("hooks", {})
    if not isinstance(hooks, dict):
        return False
    return any(
        is_superclaude_hook(entry)
        for array in hooks.values()
        if isinstance(array, list)
        for entry in array
        if isinstance(entry, dict)
    )


def detect_scope(root: Path | None = None) -> str:
    """Name the install scope rooted at ``root``.

    Project and local scope install the same content to ``<root>/.claude``, so
    naming one means reading evidence. The signals are ranked by **who wrote
    them**, strongest first, because the two earlier orderings each got a real
    case wrong by trusting a weak signal:

    1. A settings file carrying SuperClaude hooks. Only ``install`` writes
       these, and only local scope uses ``settings.local.json`` — the one
       signal that cannot be produced by hand.
    2. ``$HOME`` itself. ``~/.claude/CLAUDE.md`` carries the same import line a
       *project* install writes, so without this rung a user-scope install was
       named "project".
    3. The CLAUDE.md import lines. Hand-writable — this repo's own CLAUDE.md
       tells developers to author ``CLAUDE.local.md`` by hand — so a personal
       one used to mask a team's project-scope install and send doctor to the
       wrong settings file. Consulted only when no hooks are registered at all
       (``install --keep-settings``, or a user who removed them).

    Args:
        root: Directory to resolve from; defaults to ``project_root()``. The CLI
            passes an explicit root so ``superclaude`` behaves the same whether
            or not it runs inside a Claude Code session.

    Returns:
        "user", "project", or "local"
    """
    root = root or project_root()
    base = root / ".claude"
    if not (base / "superclaude").exists():
        return "user"

    at_home = same_dir(root, Path.home())

    # 1. Installer-written evidence.
    if _has_superclaude_hooks(base / settings_filename("local")):
        return "local"
    if _has_superclaude_hooks(base / settings_filename("user")):
        return "user" if at_home else "project"

    # 2. A .claude directly under $HOME is user scope unless local hooks said
    #    otherwise above.
    if at_home:
        return "user"

    # 3. Hand-writable evidence, weakest last.
    if _file_contains(root / "CLAUDE.local.md", "@.claude/superclaude/CLAUDE_SC.md"):
        return "local"
    if _file_contains(base / "CLAUDE.md", "@superclaude/CLAUDE_SC.md"):
        return "project"
    if (base / settings_filename("local")).exists():
        return "local"
    return "project"


def detect_refusal(payload: Any) -> str | None:
    """Return the refusal category when a ``claude -p`` payload records a
    model refusal, else None.

    Claude Fable 5.x safety classifiers end a turn with the API's
    ``stop_reason: "refusal"`` plus ``stop_details.category`` (``cyber``,
    ``bio``, ``reasoning_extraction``, ...). The CLI's result object carries a
    top-level ``stop_reason`` but no ``stop_details`` (Claude Code 2.1.258
    result schema); the category lives on the assistant message, which only
    stream-json exposes. So callers check the assistant message first and the
    result object second, and never let the result's ``"unknown"`` replace a
    category. A ``subtype`` naming a refusal counts as a fallback. A refusal
    is not ``is_error``: the CLI returns rc=0 with the refusal text in
    ``result``, which is why that text must never pass as a normal answer.

    Shared by the parallel-A/B runner and the auto-improve mutator; the eval
    harness under ``evals/`` keeps a copy pinned to this one by a test.
    """
    if not isinstance(payload, dict):
        return None
    refused = payload.get("stop_reason") == "refusal" or "refusal" in str(
        payload.get("subtype") or ""
    )
    if not refused:
        return None
    details = payload.get("stop_details") or {}
    category = details.get("category") if isinstance(details, dict) else None
    return str(category) if category else "unknown"


def same_dir(left: Path, right: Path) -> bool:
    """True when both paths name the same directory, symlinks resolved.

    Public because ``install_paths.find_install_root`` needs the same comparison
    to stop its walk-up at $HOME, and a second copy there would reintroduce the
    duplication ``settings_filename`` exists to prevent.

    Args:
        left: First path
        right: Second path

    Returns:
        True when both resolve to the same directory
    """
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return left == right


def _file_contains(path: Path, needle: str) -> bool:
    """True when ``path`` is readable and contains ``needle``."""
    try:
        return needle in path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False


def settings_filename(scope: str) -> str:
    """Name of the settings file a scope's hooks are merged into.

    Local scope keeps its hooks in settings.local.json, which Claude Code
    gitignores; user and project scope share settings.json. Single answer
    location: the same conditional was inlined at four call sites across
    install_settings and install_inventory, which is four places to miss when a
    scope's settings target changes.

    Args:
        scope: "user", "project", or "local"

    Returns:
        "settings.local.json" for local scope, else "settings.json"
    """
    return "settings.local.json" if scope == "local" else "settings.json"


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
    "hook_executions",  # hook_tracker.py's file; the sweep named the module
    "current_session",
    "insight_prompt_",
    "insight_baseline_",
    "insight_answered_",
)

# The fallback ledger is pruned entry by entry, not deleted: one live session's
# entry has to survive a sweep triggered by another.
FALLBACK_LEDGER_NAME = "mcp_fallbacks.json"

# MCP servers still in the roster. Hints for anything else are dead weight —
# a real ledger still carried `magic` and `morphllm` months after both were
# dropped. Kept here rather than imported from superclaude.hooks.mcp_fallback so
# this module stays dependency-free, and asserted equal by the test suite.
CURRENT_MCP_SERVERS = frozenset(
    {"context7", "tavily", "serena", "playwright", "devtools"}
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
    import hashlib

    # usedforsecurity=False: this is a filename discriminator, not a digest, and
    # bare md5() raises under a FIPS-enforcing Python build.
    return hashlib.md5(str(project_root()).encode(), usedforsecurity=False).hexdigest()[
        :8
    ]
