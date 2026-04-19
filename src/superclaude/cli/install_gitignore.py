"""
.gitignore management for SuperClaude local scope.

Writes and removes a marker-delimited block of gitignore entries for
SuperClaude-installed content when installing with --scope local. CC natively
gitignores only settings.local.json; for agents/skills/commands/superclaude
dirs we must manage .gitignore ourselves.

The block is generated file-by-file from the shipped source inventory so
team-shared files co-located in the same directories (e.g. a team-authored
`.claude/agents/team-reviewer.md`) are not ignored. Only files SuperClaude
actually installs are listed.
"""

from pathlib import Path
from typing import List, Tuple

from .install_paths import _get_source_dir

MARKER_START = "# >>> superclaude (local scope) >>>"
MARKER_END = "# <<< superclaude (local scope) <<<"


def _collect_local_entries() -> List[str]:
    """Enumerate SC-installed paths for the local-scope gitignore block.

    Agents and skills are listed per-file/per-dir so team-shared content in
    `.claude/agents/` and `.claude/skills/` keeps working. Commands and the
    superclaude core live in SC-only subdirectories, so directory-level
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


def add_local_gitignore(project_root: Path) -> Tuple[bool, str]:
    """Add/refresh SuperClaude local-scope block in project .gitignore.

    Idempotent by marker: an existing block is replaced so `install --force`
    / `update` pick up newly shipped agents or skills.
    """
    gitignore = project_root / ".gitignore"
    block = _build_block()

    if gitignore.exists():
        existing = gitignore.read_text(encoding="utf-8")
        stripped, had_block = _strip_block(existing)
        if had_block and stripped == existing:
            # Defensive: strip failed silently; fall back to append.
            had_block = False
        base = stripped if had_block else existing
        separator = "" if base.endswith("\n") or not base else "\n"
        updated = base + separator + ("\n" if base else "") + block
        action = "refreshed" if had_block else "updated"
    else:
        updated = block
        action = "created"

    try:
        gitignore.write_text(updated, encoding="utf-8")
        return True, f".gitignore {action} with SC local block: {gitignore}"
    except OSError as e:
        return False, f"Failed to write {gitignore}: {e}"


def remove_local_gitignore(project_root: Path) -> Tuple[bool, str]:
    """Remove SuperClaude local-scope block from project .gitignore."""
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        return True, f".gitignore not found (nothing to remove): {gitignore}"

    existing = gitignore.read_text(encoding="utf-8")
    stripped, had_block = _strip_block(existing)
    if not had_block:
        return True, f".gitignore had no SC local block: {gitignore}"

    try:
        if stripped.strip():
            gitignore.write_text(stripped, encoding="utf-8")
        else:
            gitignore.unlink()
        return True, f".gitignore SC local block removed: {gitignore}"
    except OSError as e:
        return False, f"Failed to update {gitignore}: {e}"
