"""
Local-scope git exclude management for SuperClaude.

Writes and removes a marker-delimited block of patterns into the per-clone
local exclude file (``.git/info/exclude``) — NOT the team-shared
``.gitignore`` — so SuperClaude's local-scope install artifacts are
ignored without polluting team-shared ignore rules.

CC natively gitignores only ``settings.local.json``; for the rest of the
SuperClaude content (agents/skills/commands/superclaude/etc.) we manage
the exclude file ourselves.

The block is generated file-by-file from the shipped source inventory so
team-shared files co-located in the same directories (e.g. a team-authored
``.claude/agents/team-reviewer.md``) are not ignored — only files
SuperClaude actually installs are listed.

Backward-compat: the marker convention matches the previous
``.gitignore``-targeted implementation, so a legacy block found in
``.gitignore`` is migrated automatically (removed from ``.gitignore``)
during install/uninstall.

Worktree support: when ``<root>/.git`` is a file (a worktree pointer),
the worktree-specific gitdir's ``info/exclude`` is used.
"""

from pathlib import Path
from typing import List, Optional, Tuple

from .install_paths import _get_source_dir

MARKER_START = "# >>> superclaude (local scope) >>>"
MARKER_END = "# <<< superclaude (local scope) <<<"


def _collect_local_entries() -> List[str]:
    """Enumerate SC-installed paths for the local-scope exclude block.

    Agents and skills are listed per-file/per-dir so team-shared content in
    ``.claude/agents/`` and ``.claude/skills/`` keeps working. Commands and
    the superclaude core live in SC-only subdirectories, so directory-level
    ignores are safe there.
    """
    entries: List[str] = []

    agents_src = _get_source_dir("agents")
    if agents_src.exists():
        for f in sorted(agents_src.glob("*.md")):
            if f.stem.upper() != "README":
                entries.append(f".claude/agents/{f.name}")

    skills_src = _get_source_dir("skills")
    if skills_src.exists():
        for d in sorted(skills_src.iterdir()):
            if d.is_dir() and not d.name.startswith(("_", ".")):
                entries.append(f".claude/skills/{d.name}/")

    entries.append(".claude/commands/sc/")
    entries.append(".claude/superclaude/")
    entries.append(".claude/hooks/hooks.json")
    entries.append(".claude/settings.local.json")
    entries.append("CLAUDE.local.md")

    return entries


def _build_block() -> str:
    lines = [MARKER_START]
    lines.extend(_collect_local_entries())
    lines.append(MARKER_END)
    return "\n".join(lines) + "\n"


def _strip_block(content: str) -> Tuple[str, bool]:
    """Return (content_without_block, had_block)."""
    start = content.find(MARKER_START)
    if start == -1:
        return content, False
    end = content.find(MARKER_END, start)
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
    """Resolve ``<git-dir>/info/exclude`` for a project root.

    Returns None for non-git directories or malformed worktree pointers.
    Handles three cases:

    - ``.git/`` is a directory (regular repo) → ``<root>/.git/info/exclude``
    - ``.git`` is a file (worktree pointer)   → parses ``gitdir:`` and uses
      that worktree's ``info/exclude`` (per-worktree by git's design)
    - neither exists                          → None
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
        return git_dir / "info" / "exclude"
    return None


def has_legacy_gitignore_block(project_root: Path) -> bool:
    """Whether a legacy SC block exists in ``<root>/.gitignore``."""
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        return False
    try:
        return MARKER_START in gitignore.read_text(encoding="utf-8")
    except OSError:
        return False


def has_exclude_block(project_root: Path) -> bool:
    """Whether an SC block exists in ``<root>/.git/info/exclude``."""
    exclude_file = _resolve_git_exclude_file(project_root)
    if exclude_file is None or not exclude_file.exists():
        return False
    try:
        return MARKER_START in exclude_file.read_text(encoding="utf-8")
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


def add_local_git_exclude(project_root: Path) -> Tuple[bool, str]:
    """Add/refresh SuperClaude local-scope block in ``.git/info/exclude``.

    Idempotent by marker: an existing block is replaced so subsequent
    installs pick up newly shipped agents or skills.

    Silent skip on non-git directories. Migrates a legacy block from
    ``<root>/.gitignore`` if present.
    """
    exclude_file = _resolve_git_exclude_file(project_root)
    if exclude_file is None:
        return (
            True,
            f"Not a git repository (skipping local-scope exclude setup): {project_root}",
        )

    messages: List[str] = []
    legacy_msg = _migrate_legacy_gitignore(project_root)
    if legacy_msg is not None:
        messages.append(legacy_msg)

    block = _build_block()

    try:
        if exclude_file.exists():
            existing = exclude_file.read_text(encoding="utf-8")
            stripped, had_block = _strip_block(existing)
            if had_block and stripped == existing:
                # Defensive: strip failed silently; fall back to append.
                had_block = False
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
            f".git/info/exclude {action} with SC local block: {exclude_file}"
        )
        return True, "; ".join(messages)
    except OSError as e:
        messages.append(f"Failed to write {exclude_file}: {e}")
        return False, "; ".join(messages)


def remove_local_git_exclude(project_root: Path) -> Tuple[bool, str]:
    """Remove SuperClaude local-scope block from ``.git/info/exclude``.

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
                messages.append(
                    f".git/info/exclude had no SC local block: {exclude_file}"
                )
            return True, "; ".join(messages)
        exclude_file.write_text(stripped, encoding="utf-8")
        messages.append(f".git/info/exclude SC local block removed: {exclude_file}")
        return True, "; ".join(messages)
    except OSError as e:
        messages.append(f"Failed to update {exclude_file}: {e}")
        return False, "; ".join(messages)
