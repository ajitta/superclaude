"""
.gitignore management for SuperClaude local scope.

Writes and removes a marker-delimited block of gitignore entries for
SuperClaude-installed content when installing with --scope local. CC natively
gitignores only settings.local.json; for agents/skills/commands/superclaude
dirs we must manage .gitignore ourselves.
"""

from pathlib import Path
from typing import Tuple

MARKER_START = "# >>> superclaude (local scope) >>>"
MARKER_END = "# <<< superclaude (local scope) <<<"

LOCAL_GITIGNORE_ENTRIES = [
    ".claude/agents/",
    ".claude/skills/",
    ".claude/commands/",
    ".claude/superclaude/",
    ".claude/hooks/",
    ".claude/settings.local.json",
    "CLAUDE.local.md",
]


def _build_block() -> str:
    lines = [MARKER_START]
    lines.extend(LOCAL_GITIGNORE_ENTRIES)
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
    return (trimmed_before or after), True


def add_local_gitignore(project_root: Path) -> Tuple[bool, str]:
    """Add SuperClaude local-scope block to project .gitignore (idempotent)."""
    gitignore = project_root / ".gitignore"
    block = _build_block()

    if gitignore.exists():
        existing = gitignore.read_text(encoding="utf-8")
        if MARKER_START in existing:
            return True, f".gitignore already has SC local block: {gitignore}"
        separator = "" if existing.endswith("\n") or not existing else "\n"
        updated = existing + separator + "\n" + block
    else:
        updated = block

    try:
        gitignore.write_text(updated, encoding="utf-8")
        return True, f".gitignore updated with SC local block: {gitignore}"
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
