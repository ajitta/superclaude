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

# Markers to identify SuperClaude hooks (for merge/replace logic)
SUPERCLAUDE_HOOK_MARKERS = [
    "superclaude",
    "session_init",
    "skill_activator",
    "prettier_hook",
    "test_runner_hook",
    "[experimental]",
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
        - project: Merges to ./.claude/settings.json (relative paths)
        - target: Merges to {target}/.claude/settings.json (absolute paths)
    """
    settings_file = base_path / "settings.json"
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

        # Check if SuperClaude hooks already exist
        has_sc_hooks = any(_is_superclaude_hook(h) for h in existing_array)

        if has_sc_hooks and not force:
            skipped_any = True
            continue

        merged_array = _merge_hook_arrays(existing_array, new_hook_array, force)
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


def uninstall_hooks_from_settings(base_path: Path) -> Tuple[bool, str]:
    """
    Remove SuperClaude hooks from settings.json, preserving user hooks.

    Args:
        base_path: Installation base path (.claude directory)

    Returns:
        Tuple of (success, message)
    """
    settings_file = base_path / "settings.json"

    if not settings_file.exists():
        return True, "No settings.json found (nothing to clean)"

    settings = _load_settings(settings_file)

    if "hooks" not in settings or not settings["hooks"]:
        return True, "No hooks in settings.json"

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

    # Save updated settings
    success, save_msg = _save_settings(settings_file, settings)

    if not success:
        return False, save_msg

    if cleaned_any:
        return True, f"SuperClaude hooks removed from {settings_file}"
    else:
        return True, "No SuperClaude hooks found in settings.json"


def check_claude_md_import(base_path: Path = None) -> Tuple[bool, str]:
    """
    Check if ~/.claude/CLAUDE.md has the CLAUDE_SC.md import.

    Args:
        base_path: Base installation path

    Returns:
        Tuple of (has_import: bool, status_message: str)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    claude_md = base_path / "CLAUDE.md"

    if not claude_md.exists():
        return False, "CLAUDE.md not found"

    content = claude_md.read_text(encoding="utf-8")

    # Check for import pattern (with or without leading @)
    patterns = [
        r"@superclaude/CLAUDE_SC\.md",
        r"@superclaude\\CLAUDE_SC\.md",  # Windows path
    ]

    for pattern in patterns:
        if re.search(pattern, content):
            return True, "CLAUDE.md already imports CLAUDE_SC.md"

    return False, "CLAUDE.md does not import CLAUDE_SC.md"


def update_claude_md_import(base_path: Path = None, force: bool = False) -> Tuple[bool, str]:
    """
    Add CLAUDE_SC.md import to ~/.claude/CLAUDE.md if not present.

    Args:
        base_path: Base installation path
        force: Force update even if import exists

    Returns:
        Tuple of (success: bool, message: str)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    claude_md = base_path / "CLAUDE.md"

    # Check if already has import
    has_import, status = check_claude_md_import(base_path)

    if has_import and not force:
        return True, status

    # Create or update CLAUDE.md
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")

        # If force, replace any existing superclaude imports
        if force:
            # Remove old superclaude imports
            content = re.sub(r"@superclaude/[^\n]+\n?", "", content)
            content = re.sub(r"@superclaude\\[^\n]+\n?", "", content)

        # Add import if not present
        if CLAUDE_SC_IMPORT not in content:
            # Add at the end with proper spacing
            if not content.endswith("\n"):
                content += "\n"
            content += f"\n# SuperClaude Framework\n{CLAUDE_SC_IMPORT}\n"

        claude_md.write_text(content, encoding="utf-8")
        return True, "CLAUDE.md updated with CLAUDE_SC.md import"
    else:
        # Create new CLAUDE.md
        content = f"""# Claude Code Configuration

# SuperClaude Framework
{CLAUDE_SC_IMPORT}
"""
        base_path.mkdir(parents=True, exist_ok=True)
        claude_md.write_text(content, encoding="utf-8")
        return True, "CLAUDE.md created with CLAUDE_SC.md import"


def remove_claude_md_import(base_path: Path) -> Tuple[bool, str]:
    """
    Remove @superclaude/CLAUDE_SC.md import from CLAUDE.md.

    Args:
        base_path: Installation base path (.claude directory)

    Returns:
        Tuple of (success, message)
    """
    claude_md = base_path / "CLAUDE.md"

    if not claude_md.exists():
        return True, "No CLAUDE.md found (nothing to clean)"

    try:
        content = claude_md.read_text(encoding="utf-8")
        original_content = content

        # Remove SuperClaude import lines and related comments
        # Pattern: # SuperClaude Framework\n@superclaude/CLAUDE_SC.md\n
        content = re.sub(r"# SuperClaude Framework\n@superclaude/[^\n]+\n?", "", content)
        content = re.sub(r"@superclaude/[^\n]+\n?", "", content)
        content = re.sub(r"@superclaude\\[^\n]+\n?", "", content)

        # Clean up multiple blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = content.strip() + "\n"

        if content != original_content:
            claude_md.write_text(content, encoding="utf-8")
            return True, "SuperClaude import removed from CLAUDE.md"
        else:
            return True, "No SuperClaude import found in CLAUDE.md"

    except Exception as e:
        return False, f"Failed to update CLAUDE.md: {e}"
