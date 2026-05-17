"""
Settings, Hooks & CLAUDE.md Management for SuperClaude Installation

Handles settings.json merge/unmerge, hook identification, and CLAUDE.md import management.
This is a leaf dependency with no internal imports.
"""

import json
import re
from pathlib import Path
from typing import List, Tuple

from superclaude.utils import atomic_write_json

# Import line to add to CLAUDE.md
CLAUDE_SC_IMPORT = "@superclaude/CLAUDE_SC.md"

# Markers to identify SuperClaude hooks (for merge/replace logic).
# Match is substring-based against `_comment` and `command` fields.
# `superclaude` catches `[superclaude] ...` _comment prefixes (incl. serena-recommended hooks).
SUPERCLAUDE_HOOK_MARKERS = [
    "superclaude",
    "session_init",
    "prettier_hook",
    "test_runner_hook",
    "file_size_guard",
    "BLOCKED: destructive",
]


def _load_settings(settings_file: Path) -> dict:
    """
    Load settings.json file, returning empty dict if not exists or invalid.

    Args:
        settings_file: Path to settings.json

    Returns:
        Dict with settings content, or {} if file doesn't exist/is invalid
    """
    if not settings_file.exists():
        return {}

    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_settings(settings_file: Path, settings: dict) -> Tuple[bool, str]:
    """
    Save settings dict to settings.json file.

    Args:
        settings_file: Path to settings.json
        settings: Settings dict to save

    Returns:
        Tuple of (success, message)
    """
    try:
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(settings_file, settings)
        return True, f"Settings saved to {settings_file}"
    except IOError as e:
        return False, f"Failed to save settings: {e}"


def _hook_entry_signature(hook_entry: dict) -> tuple:
    """Return a hashable signature for a hook entry.

    Two entries with the same matcher and the same set of inner hook commands
    (type, command, timeout) are treated as duplicates regardless of any
    surrounding metadata (`_comment`, etc.).
    """
    matcher = hook_entry.get("matcher", "")
    inner = tuple(sorted(
        (h.get("type", ""), h.get("command", ""), h.get("timeout"))
        for h in hook_entry.get("hooks", [])
    ))
    return (matcher, inner)


def _dedup_hook_array(hooks: List[dict]) -> List[dict]:
    """Remove duplicate hook entries, preserving first occurrence.

    Idempotent: running on an already-clean array is a no-op. Used both to
    clean accumulated duplicates from prior installs (e.g., third-party
    installers re-adding identical entries without checking) and to keep
    merged arrays clean.
    """
    seen = set()
    deduped = []
    for entry in hooks:
        sig = _hook_entry_signature(entry)
        if sig in seen:
            continue
        seen.add(sig)
        deduped.append(entry)
    return deduped


def _is_superclaude_hook(hook_entry: dict) -> bool:
    """
    Check if a hook entry belongs to SuperClaude.

    Args:
        hook_entry: A hook entry dict with "hooks" array

    Returns:
        True if any hook command contains SuperClaude markers,
        or the entry's _comment references experimental agent teams
    """
    # Check _comment field on the hook entry itself
    comment = hook_entry.get("_comment", "")
    if any(marker in comment for marker in SUPERCLAUDE_HOOK_MARKERS):
        return True

    for hook in hook_entry.get("hooks", []):
        cmd = hook.get("command", "")
        if any(marker in cmd for marker in SUPERCLAUDE_HOOK_MARKERS):
            return True
        # Also check _comment on inner hook objects (e.g. test_runner_hook)
        inner_comment = hook.get("_comment", "")
        if any(marker in inner_comment for marker in SUPERCLAUDE_HOOK_MARKERS):
            return True
    return False


def _merge_hook_arrays(
    existing: List[dict],
    new_hooks: List[dict],
    force: bool = False
) -> List[dict]:
    """
    Merge two hook arrays, preserving user hooks.

    Args:
        existing: Existing hooks array from settings.json
        new_hooks: New SuperClaude hooks to add
        force: If True, replace existing SuperClaude hooks

    Returns:
        Merged hooks array
    """
    # Separate user hooks from SuperClaude hooks
    user_hooks = [h for h in existing if not _is_superclaude_hook(h)]
    existing_sc_hooks = [h for h in existing if _is_superclaude_hook(h)]

    if force or not existing_sc_hooks:
        # Replace SuperClaude hooks or add new ones
        return user_hooks + new_hooks
    else:
        # Keep existing SuperClaude hooks (skip new ones)
        return existing


def merge_hooks_to_settings(
    base_path: Path,
    hooks_config: dict,
    scope: str,
    force: bool = False
) -> Tuple[bool, str]:
    """
    Merge hooks.json content into settings.json.

    This function merges SuperClaude hooks into the settings.json file,
    preserving any existing user hooks.

    Args:
        base_path: Installation base path (.claude directory)
        hooks_config: Transformed hooks config (paths already substituted)
        scope: Installation scope ("user", "project", or "target")
        force: Replace existing SuperClaude hooks if True

    Returns:
        Tuple of (success, message)

    Scope behavior:
        - user: Merges to ~/.claude/settings.json (absolute paths)
        - project: Merges to ./.claude/settings.json (team-shared)
        - local: Merges to ./.claude/settings.local.json (CC auto-gitignores)
        - target: Merges to {target}/.claude/settings.json (absolute paths)
    """
    settings_filename = "settings.local.json" if scope == "local" else "settings.json"
    settings_file = base_path / settings_filename
    new_hooks = hooks_config.get("hooks", {})

    if not new_hooks:
        return True, "No hooks to merge"

    # Load existing settings
    settings = _load_settings(settings_file)

    # Initialize hooks section if not exists
    if "hooks" not in settings:
        settings["hooks"] = {}

    existing_hooks = settings["hooks"]
    merged_any = False
    skipped_any = False

    # Merge each hook type (SessionStart, PostToolUse, etc.)
    for hook_type, new_hook_array in new_hooks.items():
        existing_array = existing_hooks.get(hook_type, [])

        # Dedup existing entries first. Third-party installers (e.g., Serena)
        # may re-add identical entries on each install without checking; running
        # `make sync-user` N times accumulates N copies of unmarked hooks.
        # Deduping on every merge is idempotent and bounds growth.
        existing_array = _dedup_hook_array(existing_array)

        # Check if SuperClaude hooks already exist
        has_sc_hooks = any(_is_superclaude_hook(h) for h in existing_array)

        if has_sc_hooks and not force:
            existing_hooks[hook_type] = existing_array
            skipped_any = True
            continue

        merged_array = _merge_hook_arrays(existing_array, new_hook_array, force)
        merged_array = _dedup_hook_array(merged_array)
        existing_hooks[hook_type] = merged_array
        merged_any = True

    settings["hooks"] = existing_hooks

    # Save updated settings
    success, save_msg = _save_settings(settings_file, settings)

    if not success:
        return False, save_msg

    if skipped_any and not merged_any:
        return True, f"Hooks already exist in {settings_file} (use --force to update)"
    elif skipped_any:
        return True, f"Some hooks merged to {settings_file}, some skipped (existing)"
    else:
        return True, f"Hooks merged to {settings_file}"


def uninstall_hooks_from_settings(base_path: Path, scope: str = "user") -> Tuple[bool, str]:
    """
    Remove SuperClaude hooks from settings.json (or settings.local.json for local scope),
    preserving user hooks.

    Args:
        base_path: Installation base path (.claude directory)
        scope: Installation scope

    Returns:
        Tuple of (success, message)
    """
    settings_filename = "settings.local.json" if scope == "local" else "settings.json"
    settings_file = base_path / settings_filename

    if not settings_file.exists():
        return True, f"No {settings_filename} found (nothing to clean)"

    settings = _load_settings(settings_file)

    if "hooks" not in settings or not settings["hooks"]:
        return True, f"No hooks in {settings_filename}"

    existing_hooks = settings["hooks"]
    cleaned_any = False

    # Remove SuperClaude hooks from each hook type
    for hook_type, hook_array in list(existing_hooks.items()):
        # Keep only user hooks
        user_hooks = [h for h in hook_array if not _is_superclaude_hook(h)]

        if len(user_hooks) < len(hook_array):
            cleaned_any = True

        if user_hooks:
            existing_hooks[hook_type] = user_hooks
        else:
            # Remove empty hook type
            del existing_hooks[hook_type]

    # If no hooks remain, remove hooks section entirely
    if not existing_hooks:
        del settings["hooks"]

    # For local/project scope: if the settings file is now empty (only SC content), delete it.
    # User scope is excluded — global settings.json is likely to hold user config independent of SC.
    if scope in ("local", "project") and not settings:
        try:
            settings_file.unlink()
            return True, f"SuperClaude hooks removed and empty {settings_filename} deleted"
        except OSError as e:
            return False, f"Failed to delete empty {settings_file}: {e}"

    # Save updated settings
    success, save_msg = _save_settings(settings_file, settings)

    if not success:
        return False, save_msg

    if cleaned_any:
        return True, f"SuperClaude hooks removed from {settings_file}"
    else:
        return True, f"No SuperClaude hooks found in {settings_filename}"


def _claude_md_target(base_path: Path, scope: str) -> Tuple[Path, str]:
    """
    Resolve the CLAUDE.md target file and the import line for a scope.

    - user/project: base_path/CLAUDE.md with `@superclaude/CLAUDE_SC.md` (import
      resolves relative to CLAUDE.md's directory)
    - local: project_root/CLAUDE.local.md with `@.claude/superclaude/CLAUDE_SC.md`
      (CLAUDE.local.md lives at project root per CC docs; must walk into .claude/)
    """
    if scope == "local":
        project_root = base_path.parent
        return project_root / "CLAUDE.local.md", "@.claude/superclaude/CLAUDE_SC.md"
    return base_path / "CLAUDE.md", CLAUDE_SC_IMPORT


def check_claude_md_import(base_path: Path = None, scope: str = "user") -> Tuple[bool, str]:
    """
    Check if CLAUDE.md (or CLAUDE.local.md for local scope) has the CLAUDE_SC.md import.

    Args:
        base_path: Base installation path
        scope: Installation scope

    Returns:
        Tuple of (has_import: bool, status_message: str)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    claude_md, import_line = _claude_md_target(base_path, scope)
    target_label = claude_md.name

    if not claude_md.exists():
        return False, f"{target_label} not found"

    content = claude_md.read_text(encoding="utf-8")

    # Check for import pattern (with or without leading @, cross-platform paths)
    escaped = re.escape(import_line)
    patterns = [
        escaped,
        escaped.replace("/", r"\\"),  # Windows backslash variant
    ]

    for pattern in patterns:
        if re.search(pattern, content):
            return True, f"{target_label} already imports CLAUDE_SC.md"

    return False, f"{target_label} does not import CLAUDE_SC.md"


def update_claude_md_import(
    base_path: Path = None, force: bool = False, scope: str = "user"
) -> Tuple[bool, str]:
    """
    Add CLAUDE_SC.md import to CLAUDE.md (or CLAUDE.local.md for local scope) if not present.

    Args:
        base_path: Base installation path
        force: Force update even if import exists
        scope: Installation scope

    Returns:
        Tuple of (success: bool, message: str)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    claude_md, import_line = _claude_md_target(base_path, scope)
    target_label = claude_md.name

    # Check if already has import
    has_import, status = check_claude_md_import(base_path, scope)

    if has_import and not force:
        return True, status

    # Create or update CLAUDE.md / CLAUDE.local.md
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")

        # If force, replace any existing superclaude imports
        if force:
            content = re.sub(r"@\.claude/superclaude/[^\n]+\n?", "", content)
            content = re.sub(r"@superclaude/[^\n]+\n?", "", content)
            content = re.sub(r"@superclaude\\[^\n]+\n?", "", content)

        if import_line not in content:
            if not content.endswith("\n"):
                content += "\n"
            content += f"\n# SuperClaude Framework\n{import_line}\n"

        claude_md.write_text(content, encoding="utf-8")
        return True, f"{target_label} updated with CLAUDE_SC.md import"
    else:
        header = (
            "# Claude Code Configuration (personal, gitignored)"
            if scope == "local"
            else "# Claude Code Configuration"
        )
        content = f"""{header}

# SuperClaude Framework
{import_line}
"""
        claude_md.parent.mkdir(parents=True, exist_ok=True)
        claude_md.write_text(content, encoding="utf-8")
        return True, f"{target_label} created with CLAUDE_SC.md import"


def remove_claude_md_import(base_path: Path, scope: str = "user") -> Tuple[bool, str]:
    """
    Remove @superclaude/CLAUDE_SC.md import from CLAUDE.md (or CLAUDE.local.md for local scope).

    Args:
        base_path: Installation base path (.claude directory)
        scope: Installation scope

    Returns:
        Tuple of (success, message)
    """
    claude_md, _ = _claude_md_target(base_path, scope)
    target_label = claude_md.name

    if not claude_md.exists():
        return True, f"No {target_label} found (nothing to clean)"

    try:
        content = claude_md.read_text(encoding="utf-8")
        original_content = content

        # Remove SuperClaude import lines and related comments (all variants)
        content = re.sub(r"# SuperClaude Framework\n@\.claude/superclaude/[^\n]+\n?", "", content)
        content = re.sub(r"# SuperClaude Framework\n@superclaude/[^\n]+\n?", "", content)
        content = re.sub(r"@\.claude/superclaude/[^\n]+\n?", "", content)
        content = re.sub(r"@superclaude/[^\n]+\n?", "", content)
        content = re.sub(r"@superclaude\\[^\n]+\n?", "", content)

        # Clean up multiple blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)
        stripped = content.strip()

        if content == original_content:
            return True, f"No SuperClaude import found in {target_label}"

        # For local/project scope: if CLAUDE.md/CLAUDE.local.md has no user content
        # (empty or only the SC-created header), remove it entirely.
        # User scope is excluded — global CLAUDE.md is likely to hold user config independent of SC.
        SC_HEADERS = {  # noqa: N806 — function-local constant
            "# Claude Code Configuration (personal, gitignored)",
            "# Claude Code Configuration",
        }
        if scope in ("local", "project") and (not stripped or stripped in SC_HEADERS):
            claude_md.unlink()
            return True, f"{target_label} removed (no user content after SC cleanup)"

        claude_md.write_text(stripped + "\n", encoding="utf-8")
        return True, f"SuperClaude import removed from {target_label}"

    except Exception as e:
        return False, f"Failed to update {target_label}: {e}"
