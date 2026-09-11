"""
Per-clone git exclude management for SuperClaude.

Writes and removes a marker-delimited block of patterns into the per-clone
local exclude file (``.git/info/exclude``) — NOT the team-shared
``.gitignore`` — so SuperClaude's install artifacts are ignored without
polluting team-shared ignore rules. Per-clone is the whole point: every
teammate's own install writes their own block, with no coordination.

CC natively gitignores only ``settings.local.json``; for the rest of the
SuperClaude content (agents/skills/commands/superclaude/etc.) we manage
the exclude file ourselves.

The block is scope-dependent. Local scope excludes everything it installs —
none of it is the team's. Project scope excludes only rebuildable runtime
state: content and the hook registration (``settings.json``,
``hooks/hooks.json``) stay tracked, because sharing them is what the scope is
for, and every hook command is ``superclaude hook <name>`` — no interpreter, no
script path — so each teammate's install writes the same bytes.

The block is generated file-by-file from the shipped source inventory so
team-shared files co-located in the same directories (e.g. a team-authored
``.claude/agents/team-reviewer.md``) are not ignored — only files
SuperClaude actually installs are listed.

Backward-compat: the marker convention matches the previous
``.gitignore``-targeted implementation, so a legacy block found in
``.gitignore`` is migrated automatically (removed from ``.gitignore``)
during install/uninstall.

Worktree support: when ``<root>/.git`` is a file (a worktree pointer), the
block goes to the COMMON git directory's ``info/exclude`` — the one file git
reads for every worktree of the clone. ``.git/worktrees/<name>/info/exclude``
is never read (measured 2026-09-05, git 2.55: a pattern there leaves
``check-ignore`` at exit 1), which is what this module wrote until then. One
file per clone has consequences git's layout dictates: worktrees installed at
the same scope write identical blocks (the patterns are relative), a sibling
worktree installed at a DIFFERENT scope replaces the block — marker-keyed,
last install wins, so a project-scope install in one worktree un-excludes a
local-scope install in another — and a removal from any worktree un-excludes
them all.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from .install_paths import COMPONENTS, SHARED_TARGET_COMPONENTS, shipped_md_names

MARKER_START = "# >>> superclaude >>>"
MARKER_END = "# <<< superclaude <<<"

# Marker text from before the block became scope-aware. Kept so an install that
# predates the rename replaces its block instead of leaving a second one behind.
# A second migration path is this module's established shape, not a new
# exception: _migrate_legacy_gitignore already carries the .gitignore ->
# info/exclude move for the same reason. The alternative — keeping the old text —
# would write "(local scope)" into every project-scope user's exclude file, which
# is a false statement in generated output.
_LEGACY_MARKER_PAIRS = [
    ("# >>> superclaude (local scope) >>>", "# <<< superclaude (local scope) <<<"),
]

_ALL_MARKER_PAIRS = [(MARKER_START, MARKER_END), *_LEGACY_MARKER_PAIRS]


def _has_any_marker(content: str) -> bool:
    """Whether ``content`` carries an SC block under any marker generation."""
    return any(start in content for start, _ in _ALL_MARKER_PAIRS)


# Paths a project-scope install must keep out of the team's history: runtime
# state, rebuildable and written inside the worktree by every install.
# Everything else a project install writes is machine-independent and stays
# tracked — including settings.json and hooks/hooks.json, whose commands are
# `superclaude hook <name>`. (Releases before the console entry baked the
# installing machine's interpreter into both, and listed them here.)
#
# `.claude/agent-memory/` is deliberately absent. A project-scope install creates
# it, so it shows up untracked, but committing reviewed team memory is a
# documented option (docs/research/agent-memory-utilization-ajitta-2026-07-24.md
# calls the PR diff the poisoning trust boundary). Excluding it here would take
# that choice away from the team; a team that does not want it says so in
# .gitignore, which is where team-level decisions belong.
_PROJECT_SCOPE_ENTRIES = [
    ".claude/.superclaude_hooks/",
    ".claude/insights.pending.jsonl",
]


def _collect_entries(scope: str = "local") -> List[str]:
    """Enumerate the paths a scope's exclude block should carry.

    Agents and output styles are listed per-file so team-shared content in
    ``.claude/agents/`` and ``.claude/output-styles/`` keeps working. Commands
    and the superclaude core live in SC-only subdirectories, so directory-level
    ignores are safe there.

    Project scope gets the fixed runtime-state subset instead: its whole
    purpose is that the content — and the hook registration — IS committed.
    """
    if scope == "project":
        return list(_PROJECT_SCOPE_ENTRIES)

    entries: List[str] = []

    # Directories Claude Code shares with the user's own files: list the shipped
    # filenames, never the directory.
    for component in SHARED_TARGET_COMPONENTS:
        target_subdir = COMPONENTS[component][1]
        for name in sorted(shipped_md_names(component)):
            entries.append(f".claude/{target_subdir}/{name}")

    entries.append(".claude/agent-memory-local/")
    entries.append(".claude/agent-memory/")
    # Runtime state and un-promoted markers: rebuildable, framework-owned, and
    # written inside the worktree by every project- or local-scope install.
    entries.append(".claude/.superclaude_hooks/")
    entries.append(".claude/insights.pending.jsonl")
    entries.append(".claude/commands/sc/")
    entries.append(".claude/superclaude/")
    entries.append(".claude/hooks/hooks.json")
    entries.append(".claude/settings.local.json")
    entries.append("CLAUDE.local.md")

    return entries


def _build_block(scope: str = "local") -> str:
    lines = [MARKER_START]
    lines.extend(_collect_entries(scope))
    lines.append(MARKER_END)
    return "\n".join(lines) + "\n"


def _strip_block(content: str) -> Tuple[str, bool]:
    """Return (content without every SC block, whether any was found).

    Both marker generations are stripped, so upgrading across the rename
    replaces the old block rather than appending a second one beside it.

    Terminates because every removal is strictly shrinking: a pair only reports
    a hit when both markers were found, and the marker lines themselves are
    dropped. That is also why the caller needs no "strip failed silently" guard.
    """
    had_any = False
    while True:
        for start_marker, end_marker in _ALL_MARKER_PAIRS:
            stripped, had = _strip_one_block(content, start_marker, end_marker)
            if had:
                content, had_any = stripped, True
                break
        else:
            return content, had_any


def _strip_one_block(
    content: str, start_marker: str, end_marker: str
) -> Tuple[str, bool]:
    """Return (content_without_block, had_block) for one marker pair."""
    start = content.find(start_marker)
    if start == -1:
        return content, False
    end = content.find(end_marker, start)
    if end == -1:
        return content, False
    end_of_line = content.find("\n", end)
    if end_of_line == -1:
        end_of_line = len(content)
    else:
        end_of_line += 1
    trimmed_before = content[:start].rstrip("\n")
    after = content[end_of_line:]
    if trimmed_before and after:
        return trimmed_before + "\n" + after, True
    if trimmed_before:
        return trimmed_before + "\n", True
    return after, True


def _resolve_git_exclude_file(project_root: Path) -> Optional[Path]:
    """Resolve the ``info/exclude`` git actually reads for a project root.

    Returns None for non-git directories or malformed worktree pointers.
    Handles three cases:

    - ``.git/`` is a directory (regular repo) → ``<root>/.git/info/exclude``
    - ``.git`` is a file (``gitdir:`` pointer) → the gitdir's ``commondir``
      file, when present, names the common git directory and the answer is
      ``<commondir>/info/exclude``: git resolves ``info/`` through the common
      dir, so a linked worktree's own ``info/exclude`` is dead. Without a
      ``commondir`` the gitdir is complete on its own (a submodule's
      ``.git/modules/<name>``) and its ``info/exclude`` is the one git reads.
      A ``commondir`` naming a directory that no longer exists → None, like a
      malformed pointer: a stale worktree (its repository moved or deleted)
      must not have a git directory conjured for it by ``mkdir(parents=True)``.
    - neither exists                           → None

    Plain file reads, no ``git`` subprocess — the same two hops as
    ``superclaude.utils.main_worktree_root``, which answers a different
    question (the main worktree's root, not its git directory: a bare
    repository's worktrees have a common dir with no worktree above it).
    """
    git_path = project_root / ".git"
    if git_path.is_dir():
        return git_path / "info" / "exclude"
    if git_path.is_file():
        try:
            content = git_path.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        prefix = "gitdir: "
        if not content.startswith(prefix):
            return None
        git_dir_str = content[len(prefix) :].strip()
        git_dir = Path(git_dir_str)
        if not git_dir.is_absolute():
            git_dir = (project_root / git_dir).resolve()
        if not git_dir.is_dir():
            return None
        try:
            common = (git_dir / "commondir").read_text(encoding="utf-8").strip()
        except OSError:
            common = ""
        if common:
            common_dir = Path(common)
            if not common_dir.is_absolute():
                common_dir = (git_dir / common_dir).resolve()
            if not common_dir.is_dir():
                return None
            git_dir = common_dir
        return git_dir / "info" / "exclude"
    return None


def has_legacy_gitignore_block(project_root: Path) -> bool:
    """Whether a legacy SC block exists in ``<root>/.gitignore``."""
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        return False
    try:
        return _has_any_marker(gitignore.read_text(encoding="utf-8"))
    except OSError:
        return False


def has_exclude_block(project_root: Path) -> bool:
    """Whether an SC block exists in ``<root>/.git/info/exclude``."""
    exclude_file = _resolve_git_exclude_file(project_root)
    if exclude_file is None or not exclude_file.exists():
        return False
    try:
        return _has_any_marker(exclude_file.read_text(encoding="utf-8"))
    except OSError:
        return False


def _migrate_legacy_gitignore(project_root: Path) -> Optional[str]:
    """Remove SC block from legacy ``.gitignore`` if present.

    Returns a status message when migration was performed (or attempted
    and failed), ``None`` when no legacy block was found.
    """
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        return None
    try:
        existing = gitignore.read_text(encoding="utf-8")
    except OSError as e:
        return f"⚠️  Could not read legacy {gitignore}: {e}"
    stripped, had_block = _strip_block(existing)
    if not had_block:
        return None
    try:
        if stripped.strip():
            gitignore.write_text(stripped, encoding="utf-8")
        else:
            gitignore.unlink()
        return f"Migrated legacy SC block out of {gitignore}"
    except OSError as e:
        return f"⚠️  Failed to migrate legacy {gitignore}: {e}"


def add_git_exclude(project_root: Path, scope: str = "local") -> Tuple[bool, str]:
    """Add/refresh the SuperClaude block in ``.git/info/exclude``.

    Idempotent by marker: an existing block is replaced so subsequent
    installs pick up newly shipped agents, and so switching scope in place
    replaces the block rather than stacking a second one.

    Silent skip on non-git directories. Migrates a legacy block from
    ``<root>/.gitignore`` if present.

    Args:
        project_root: The checkout to write the exclude block into
        scope: Install scope deciding which paths the block lists
    """
    exclude_file = _resolve_git_exclude_file(project_root)
    if exclude_file is None:
        return (
            True,
            f"Not a git repository (skipping exclude setup): {project_root}",
        )

    messages: List[str] = []
    legacy_msg = _migrate_legacy_gitignore(project_root)
    if legacy_msg is not None:
        messages.append(legacy_msg)

    block = _build_block(scope)

    try:
        if exclude_file.exists():
            existing = exclude_file.read_text(encoding="utf-8")
            stripped, had_block = _strip_block(existing)
            base = stripped if had_block else existing
            separator = "" if base.endswith("\n") or not base else "\n"
            updated = base + separator + ("\n" if base else "") + block
            action = "refreshed" if had_block else "updated"
        else:
            exclude_file.parent.mkdir(parents=True, exist_ok=True)
            updated = block
            action = "created"
        exclude_file.write_text(updated, encoding="utf-8")
        messages.append(
            f".git/info/exclude {action} with SC {scope} block: {exclude_file}"
        )
        return True, "; ".join(messages)
    except OSError as e:
        messages.append(f"Failed to write {exclude_file}: {e}")
        return False, "; ".join(messages)


def remove_git_exclude(project_root: Path) -> Tuple[bool, str]:
    """Remove the SuperClaude block from ``.git/info/exclude``.

    Also removes a legacy block from ``<root>/.gitignore`` if present.
    The exclude file itself is preserved (only the marker block is
    stripped) — git's default template comments and any user content
    remain intact.
    """
    messages: List[str] = []

    legacy_msg = _migrate_legacy_gitignore(project_root)
    if legacy_msg is not None:
        messages.append(legacy_msg)

    exclude_file = _resolve_git_exclude_file(project_root)
    if exclude_file is None:
        if not messages:
            messages.append(f"Not a git repository: {project_root}")
        return True, "; ".join(messages)

    if not exclude_file.exists():
        if not messages:
            messages.append(
                f".git/info/exclude not found (nothing to remove): {exclude_file}"
            )
        return True, "; ".join(messages)

    try:
        existing = exclude_file.read_text(encoding="utf-8")
        stripped, had_block = _strip_block(existing)
        if not had_block:
            if not messages:
                messages.append(f".git/info/exclude had no SC block: {exclude_file}")
            return True, "; ".join(messages)
        exclude_file.write_text(stripped, encoding="utf-8")
        messages.append(f".git/info/exclude SC block removed: {exclude_file}")
        return True, "; ".join(messages)
    except OSError as e:
        messages.append(f"Failed to update {exclude_file}: {e}")
        return False, "; ".join(messages)


# One `git check-ignore -v` line: `<source>:<linenum>:<pattern>\t<path>`. The
# source is matched greedily so a Windows drive letter (`C:/Users/x/.gitignore`)
# keeps its line number.
_CHECK_IGNORE_LINE_RE = re.compile(
    r"^(?P<source>.*):(?P<line>\d+):(?P<pattern>.*)\t(?P<path>.*)$"
)


def _parse_check_ignore(stdout: str) -> List[Tuple[str, str, str]]:
    """(source, line, path) for every rule that actually hides its path.

    Two kinds of line are dropped. A negation pattern (`!.claude/settings.json`)
    is printed by `-v` as the winning rule, yet it means the path is NOT
    ignored — reporting it would tell the user to delete the whitelist that
    makes the file committable. A rule from an `info/exclude` file is per-clone
    (SuperClaude's own block, or the user's), not a team rule, so it is not what
    this check is about.
    """
    found: List[Tuple[str, str, str]] = []
    for line in stdout.splitlines():
        match = _CHECK_IGNORE_LINE_RE.match(line)
        if not match:
            continue
        if match["pattern"].startswith("!"):
            continue
        if match["source"].replace("\\", "/").endswith("info/exclude"):
            continue
        found.append((match["source"], match["line"], match["path"]))
    return found


def find_team_ignores(
    project_root: Path, paths: List[str]
) -> List[Tuple[str, str, str]]:
    """Team-level ignore rules that hide ``paths`` from the team's history.

    Project scope promises the hook registration is committed, and this module
    stopped excluding it — but a team-level ``.gitignore`` or a global excludes
    file can still hide it, silently: install reports success and nothing ever
    reaches the repository. ``git check-ignore -v`` names the rule that wins.
    Tracked files are never reported (git's own rule), so an already-committed
    registration stays quiet; negation patterns and per-clone ``info/exclude``
    rules are dropped by ``_parse_check_ignore``.

    Returns:
        (source, line, path) per ignored path; empty when nothing is ignored,
        when this is not a git repository, or when git is unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "check-ignore", "-v", "--", *paths],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:  # 1: nothing ignored; 128: not a repository
        return []
    return _parse_check_ignore(result.stdout)
