"""Shared utility functions for superclaude.

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
import sys
import time
from pathlib import Path
from typing import Any

# `hashlib` and `tempfile` are imported inside the two functions that use them.
# Every hook script pays this module's import cost on every tool call, and
# `tempfile` alone is 3.0ms of it — spent even on the read-only PreToolUse paths
# that never write state. Keep new module-level imports out of here for the same
# reason.


def read_hook_stdin() -> str:
    """Raw text Claude Code piped to a hook; "" on a tty or an unreadable stdin."""
    try:
        return sys.stdin.read() if not sys.stdin.isatty() else ""
    except (OSError, ValueError):
        return ""


def read_hook_input() -> dict | None:
    """The JSON object Claude Code piped to a hook, or None.

    None covers every "nothing to act on" case a hook must stay silent for: a
    tty, empty stdin, text that is not JSON, and JSON that is not an object.
    A PreToolUse hook allows by printing nothing, so callers return on None
    rather than printing a decision (see hooks/README.md).
    """
    raw = read_hook_stdin()
    if not raw.strip():
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


# Default for CLAUDE_CONTEXT_MAX_TOKENS: the on-demand injection budget per
# prompt (chars/4 estimate), enforced by scripts/context_loader.py and reported
# by `superclaude context explain`. One constant, not two literals: v4.29.1
# shipped `/sc:analyze --delegate` dropping RULES_DOCS.md because the three
# P1 rule modules reached 8,015 tokens against an 8,000 default and nothing
# tied the number to the content it must hold. 12,000 fits every P1 rule
# module plus the largest routed mode with headroom —
# tests/unit/test_context_loader.py pins that.
DEFAULT_CONTEXT_MAX_TOKENS = 12000


def int_env(name: str, default: int) -> int:
    """Read an integer knob from the environment; a missing or malformed value
    (``8k``, an empty string) yields ``default`` instead of a ValueError. The
    prompt hook reads its budget at import, so a typo in a shell profile would
    otherwise fail every prompt until found."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def atomic_write_text(path: Path, text: str) -> None:
    """Write ``text`` as UTF-8 atomically (temp file + os.replace).

    Prevents data corruption from crashes during write by writing to a
    temporary file first, then atomically replacing the target. The text is
    written byte for byte (no newline translation): the caller decides the
    line ending, so a project-scope settings.json, committed and promised
    identical on every teammate's checkout, is not CRLF on Windows.

    The file keeps its permission mode. ``mkstemp`` creates the temp file
    0600, and replacing the target with it used to leave every settings file
    0600 whatever mode the user had given it (install/upgrade audit, C-21). A
    new file gets what a plain ``open()`` would: 0666 less the umask.

    A symlink stays a symlink: the write goes to the file it points at, with
    the temp file made in that file's directory. Renaming over the link used to
    turn a settings file a dotfiles manager symlinks into a plain file, and the
    repository copy never saw the hooks (06c, Y-1).

    Args:
        path: Target file path
        text: The complete file content
    """
    import stat
    import tempfile

    path = Path(path)
    if path.is_symlink():
        path = Path(os.path.realpath(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except FileNotFoundError:
        umask = os.umask(0)
        os.umask(umask)
        mode = 0o666 & ~umask
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.chmod(tmp_path, mode)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def atomic_write_json(path: Path, data: Any, indent: int | None = 2) -> None:
    """Write JSON data atomically; see ``atomic_write_text`` for the guarantees.

    Args:
        path: Target file path
        data: JSON-serializable data
        indent: JSON indentation level
    """
    atomic_write_text(path, json.dumps(data, indent=indent))


def project_root() -> Path:
    """Project root for hook-relative paths.

    Hook CWD is not guaranteed to be the project root, so $CLAUDE_PROJECT_DIR is
    the anchor whenever Claude Code provides it. See the hooks reference at
    'https://code.claude.com/docs/en/hooks'.

    Returns:
        $CLAUDE_PROJECT_DIR if set, else the current working directory
    """
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())


# Claude Code's own encoder, read out of the installed CLI binary
# (~/.local/bin/claude, 2026-10-15 build): `e.replace(/[^a-zA-Z0-9]/g,"-")`.
_CLAUDE_PROJECTS_DIR_RE = re.compile(r"[^A-Za-z0-9]")


def claude_projects_dir_name(cwd: str) -> str:
    """Folder name Claude Code gives ``cwd`` under ``~/.claude/projects/``.

    Claude Code stores transcripts and auto-memory under
    ``~/.claude/projects/<encoded cwd>/``. The rule — every character outside
    ``[A-Za-z0-9]`` becomes one ``-``, no coalescing, no case folding — was
    derived on 2026-10-18 from two sources, not assumed:

    1. All 98 folder names present in the author's ``~/.claude/projects/``,
       matched back to their real cwds. They show ``:``, ``\\``, ``/``, ``.``
       and ``_`` each becoming one ``-`` (``C:\\Users\\ajitta\\.claude\\...`` →
       ``C--Users-ajitta--claude-...``; mkdtemp suffixes drawn from
       ``[a-z0-9_]`` stored with ``-`` where ``_`` was), letters keeping their
       case (one folder starts ``c--Users-`` from a lowercase drive letter),
       and no hashing or truncation up to the longest observed name (164).
    2. The encoder function in the installed CLI binary, which is literally
       ``replace(/[^a-zA-Z0-9]/g,"-")`` followed by a truncation that only
       applies past 200 characters.

    The two earlier copies in ``memory_staleness`` and ``insight_writer``
    replaced only ``:``, ``\\`` and ``/``, so any project whose path contained
    a dot (``.claude/worktrees/...``, ``.config``) resolved to a folder that
    does not exist: the staleness scan found nothing and never warned, and the
    transcript fallback found no transcript.

    Not replicated: the CLI's >200-character truncation (``slice(0, 200)`` plus
    a base-36 hash of the original path). The hash function was not identified
    in the binary, and no path on this machine reaches that length; a cwd that
    does will resolve to a non-existent folder, as before.

    Args:
        cwd: Absolute session or project path, as Claude Code received it

    Returns:
        The encoded folder name (not a full path)
    """
    return _CLAUDE_PROJECTS_DIR_RE.sub("-", cwd)


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


def user_claude_dir() -> Path:
    """The user ``.claude`` directory Claude Code reads.

    ``$CLAUDE_CONFIG_DIR`` when it is set and non-empty, else ``~/.claude``
    (ADR-0002). Claude Code reads user settings, components, the user
    ``CLAUDE.md``, ``.claude.json`` and ``projects/`` from there (P8 W7), so a
    user-scope install anywhere else is never loaded. Under
    ``CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`` Claude Code removes the variable from
    hook subprocesses, and a hook falls back to ``~/.claude`` (ADR-0002 Q1 a;
    doctor says so).
    """
    value = os.environ.get("CLAUDE_CONFIG_DIR", "").strip()
    if value:
        return Path(value).expanduser().absolute()
    return Path.home() / ".claude"


def claude_json_path() -> Path:
    """Claude Code's ``.claude.json``: inside ``$CLAUDE_CONFIG_DIR`` when set.

    Without the variable it sits beside ``~/.claude``, not in it.
    """
    if os.environ.get("CLAUDE_CONFIG_DIR", "").strip():
        return user_claude_dir() / ".claude.json"
    return Path.home() / ".claude.json"


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
        worktree's when this is a linked worktree carrying one, else the user
        directory (``user_claude_dir``)
    """
    root = project_root() / ".claude"
    if (root / "superclaude").exists():
        return root
    main_root = main_worktree_root(project_root())
    if main_root is not None:
        main_base = main_root / ".claude"
        if (main_base / "superclaude").exists():
            return main_base
    return user_claude_dir()


# Markers identifying a hook registration as superclaude's. Hoisted here from
# install_settings because scope detection needs the same judgement: which
# settings file the *installer* wrote is the only signal that separates local
# from project scope reliably. Every marker is anchored — bare script names like
# "session_init" would misclassify a user's own hook as ours.
SUPERCLAUDE_HOOK_MARKERS = [
    "[superclaude]",
    "{{SCRIPTS_PATH}}",  # legacy: unresolved template form of the scripts path
    "BLOCKED: destructive",  # legacy inline destructive-Bash blocker command
]

# The console-entry form every shipped hook command takes: `superclaude hook
# <name> [subcommand]`. The prefix admits a directory, a Windows suffix and a
# closing quote (`~/.local/bin/superclaude hook x`, `C:/.../superclaude.exe hook
# x`, `"C:/Program Files/.../superclaude.exe" hook x` — a path with a space has
# to be quoted): pinning the absolute path is the user's workaround when Claude
# Code's hook shell has a narrow PATH, and that pinned command is still ours —
# judged otherwise, a non-force install appended every shipped hook beside it.
# Group 1 is the hook name, group 2 whatever follows it.
CONSOLE_HOOK_RE = re.compile(
    r"(?:^|[\s/\\])superclaude(?:\.exe)?[\"']?\s+hook\s+([A-Za-z0-9_]+)(.*)$"
)

# Legacy resolved form (releases before the console entry): a command naming a
# script copy under a superclaude scripts directory (absolute user-scope path
# or $CLAUDE_PROJECT_DIR/.claude/superclaude/scripts; / or \ separators). Kept
# so an upgrade still recognises — and migrates — those registrations.
_SC_SCRIPTS_PATH_RE = re.compile(r"superclaude[/\\]scripts[/\\]")

# Inline commands a release registered with no marker at all: the
# `[experimental]` agent-team echoes of d174e600 → 42218e97, whose entry comment
# lacked the tag. Matched whole, so only these exact commands count as ours and
# uninstall can reach them.
UNMARKED_SC_HOOK_COMMANDS = (
    "echo 'Teammate idle — assign next task'",
    "echo 'Task completed — aggregate results'",
)


def is_legacy_hook_command(command: str) -> bool:
    """Whether a hook command is a pre-console-entry registration.

    An interpreter plus a script copy under a superclaude scripts directory,
    resolved or still templated: these carry the installing machine's paths,
    which is what the console entry removed, so an install rewrites them.
    """
    return "{{SCRIPTS_PATH}}" in command or bool(_SC_SCRIPTS_PATH_RE.search(command))


def is_superclaude_inner_hook(hook: dict) -> bool:
    """Whether one inner hook is superclaude's, judged on its own command.

    The unit that matters for ownership. A settings entry carries one matcher
    and a list of inner hooks, so a user's own command can sit beside a
    superclaude one; judging the whole entry deleted the user's command along
    with ours on `--force` and on uninstall.
    """
    cmd = hook.get("command", "")
    if any(marker in cmd for marker in SUPERCLAUDE_HOOK_MARKERS):
        return True
    if CONSOLE_HOOK_RE.search(cmd) or is_legacy_hook_command(cmd):
        return True
    if cmd.strip() in UNMARKED_SC_HOOK_COMMANDS:
        return True
    return any(
        marker in hook.get("_comment", "") for marker in SUPERCLAUDE_HOOK_MARKERS
    )


def is_superclaude_hook(hook_entry: dict) -> bool:
    """Whether a settings hook entry belongs to superclaude.

    Args:
        hook_entry: A hook entry dict with a "hooks" array

    Returns:
        True if any hook command runs `superclaude hook`, references a legacy
        superclaude scripts path (template or resolved) or carries an anchored
        superclaude marker, or a `_comment` carries the `[superclaude]` tag
    """
    comment = hook_entry.get("_comment", "")
    if any(marker in comment for marker in SUPERCLAUDE_HOOK_MARKERS):
        return True

    return any(is_superclaude_inner_hook(h) for h in hook_entry.get("hooks", []))


def _has_superclaude_hooks(settings_file: Path) -> bool:
    """Whether a settings file carries at least one superclaude hook entry."""
    try:
        settings = json.loads(settings_file.read_text(encoding="utf-8-sig"))
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

    1. A settings file carrying superclaude hooks. Only ``install`` writes
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

    Safety classifiers on Fable 5.x, Opus 5.5, Sonnet 5.5 and Opus 5 end a turn
    with the API's ``stop_reason: "refusal"`` plus ``stop_details.category``
    (``cyber``, ``bio``, ``reasoning_extraction``, ...; the set differs by model:
    Opus 5 has ``reasoning_extraction``; sources disagree on ``bio``). On Opus 5.5 and Sonnet 5.5
    server-side fallback returns a ``reasoning_extraction`` decline instead of
    retrying it (on Sonnet 5.5, server-side fallback retries only ``cyber`` and
    ``frontier_llm``, on Sonnet 5), so a caller that sees that category changes
    the prompt. The CLI's result object carries a
    top-level ``stop_reason`` but no ``stop_details`` (Claude Code 2.1.258
    result schema); the category lives on the assistant message, which only
    stream-json exposes. So callers check the assistant message first and the
    result object second, and never let the result's ``"unknown"`` replace a
    category. A ``subtype`` naming a refusal counts as a fallback. A refusal
    is not ``is_error``: the CLI returns rc=0 with the refusal text in
    ``result``, which is why that text must never pass as a normal answer.

    Shared by the parallel-A/B runner, the auto-improve mutator and the eval
    harness under ``evals/`` (a test pins that the harness imports this one).
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
# the state dir is superclaude's, but deleting by prefix rather than by directory
# means a file put there deliberately later is not collected by surprise.
_PRUNABLE_PREFIXES = (
    "claude_context_",
    "loop_guard_",
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
CURRENT_MCP_SERVERS = frozenset({"context7", "tavily", "playwright", "devtools"})


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
