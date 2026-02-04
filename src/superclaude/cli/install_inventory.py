"""
Listing & Uninstallation for SuperClaude

Handles listing available/installed components and full uninstallation.
"""

import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .install_paths import (
    COMPONENTS,
    _get_package_root,
    _get_source_dir,
    _get_target_dir,
    get_base_path,
)
from .install_settings import (
    _is_superclaude_hook,
    _load_settings,
    remove_claude_md_import,
    uninstall_hooks_from_settings,
)


def list_available_commands() -> List[str]:
    """
    List all available commands.

    Returns:
        List of command names
    """
    source_dir = _get_source_dir("commands")

    if not source_dir.exists():
        return []

    commands = []
    for file in source_dir.glob("*.md"):
        if file.stem != "README":
            commands.append(file.stem)

    return sorted(commands)


def list_installed_commands(base_path: Path = None) -> List[str]:
    """
    List installed commands.

    Args:
        base_path: Base installation path (default: ~/.claude)

    Returns:
        List of installed command names
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    commands_dir = base_path / "commands" / "sc"

    if not commands_dir.exists():
        return []

    installed = []
    for file in commands_dir.glob("*.md"):
        if file.stem != "README":
            installed.append(file.stem)

    return sorted(installed)


def list_all_components(base_path: Path = None) -> Dict[str, Dict[str, Any]]:
    """
    List all components with their installation status.

    Args:
        base_path: Base installation path (default: ~/.claude)

    Returns:
        Dict with component info and status
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    result = {}
    package_root = _get_package_root()

    # Regular components
    for component, (_, _, description) in COMPONENTS.items():
        source_dir = _get_source_dir(component)
        target_dir = _get_target_dir(component, base_path)

        # Count source files (excluding README.md and __init__.py)
        if component == "skills":
            source_count = sum(1 for d in source_dir.iterdir() if d.is_dir()) if source_dir.exists() else 0
            installed_count = sum(1 for d in target_dir.iterdir() if d.is_dir()) if target_dir.exists() else 0
        else:
            source_count = sum(1 for f in source_dir.glob("*.md") if f.stem.upper() != "README") if source_dir.exists() else 0
            installed_count = sum(1 for f in target_dir.glob("*.md") if f.stem.upper() != "README") if target_dir.exists() else 0

        result[component] = {
            "description": description,
            "source_path": str(source_dir),
            "target_path": str(target_dir),
            "available": source_count,
            "installed": installed_count,
        }

    # Scripts (special handling - now in superclaude/scripts/)
    scripts_source = package_root / "scripts"
    scripts_target = base_path / "superclaude" / "scripts"

    # Count scripts
    scripts_available = 0
    if scripts_source.exists():
        scripts_available = sum(1 for f in scripts_source.glob("*.sh"))
        scripts_available += sum(1 for f in scripts_source.glob("*.py") if f.name != "__init__.py")

    scripts_installed = 0
    if scripts_target.exists():
        scripts_installed = sum(1 for f in scripts_target.glob("*.sh"))
        scripts_installed += sum(1 for f in scripts_target.glob("*.py") if f.name != "__init__.py")

    result["scripts"] = {
        "description": "Hook scripts",
        "source_path": str(scripts_source),
        "target_path": str(scripts_target),
        "available": scripts_available,
        "installed": scripts_installed,
    }

    # Hooks configuration (now in .claude/hooks/hooks.json)
    hooks_source = package_root / "hooks"
    hooks_target = base_path / "hooks"
    hooks_json_installed = (hooks_target / "hooks.json").exists()

    result["hooks"] = {
        "description": "Hook configuration",
        "source_path": str(hooks_source),
        "target_path": str(hooks_target),
        "available": 1 if (hooks_source / "hooks.json").exists() else 0,
        "installed": 1 if hooks_json_installed else 0,
    }

    return result


def uninstall_all(
    base_path: Path = None,
    scope: str = "user",
    dry_run: bool = False,
    keep_settings: bool = False
) -> Tuple[bool, str]:
    """
    Uninstall all SuperClaude components.

    This function removes:
    1. .claude/superclaude/ directory (entire directory)
    2. .claude/hooks/hooks.json file
    3. SuperClaude hooks from settings.json (preserves user hooks)
    4. @superclaude import from CLAUDE.md

    Args:
        base_path: Installation base path (default: ~/.claude or ./.claude based on scope)
        scope: Installation scope ("user" or "project")
        dry_run: If True, only show what would be removed
        keep_settings: If True, don't modify settings.json hooks

    Returns:
        Tuple of (success: bool, message: str)
    """
    if base_path is None:
        base_path = get_base_path(scope)

    messages = []
    removed = 0
    skipped = 0
    failed = 0

    # 1. Remove .claude/superclaude/ directory
    superclaude_dir = base_path / "superclaude"
    if superclaude_dir.exists():
        if dry_run:
            # Count items for dry-run display
            item_count = sum(1 for _ in superclaude_dir.rglob("*") if _.is_file())
            messages.append(f"[DRY-RUN] Would remove: {superclaude_dir}/ ({item_count} files)")
            removed += 1
        else:
            try:
                shutil.rmtree(superclaude_dir)
                messages.append(f"✅ Removed: {superclaude_dir}/")
                removed += 1
            except Exception as e:
                messages.append(f"❌ Failed to remove {superclaude_dir}/: {e}")
                failed += 1
    else:
        messages.append(f"⏭️  Not found: {superclaude_dir}/")
        skipped += 1

    # 2. Remove .claude/commands/sc/ directory (slash commands)
    commands_sc_dir = base_path / "commands" / "sc"
    if commands_sc_dir.exists():
        if dry_run:
            item_count = sum(1 for _ in commands_sc_dir.glob("*.md"))
            messages.append(f"[DRY-RUN] Would remove: {commands_sc_dir}/ ({item_count} files)")
            removed += 1
        else:
            try:
                shutil.rmtree(commands_sc_dir)
                messages.append(f"✅ Removed: {commands_sc_dir}/")
                removed += 1
            except Exception as e:
                messages.append(f"❌ Failed to remove {commands_sc_dir}/: {e}")
                failed += 1
    else:
        messages.append(f"⏭️  Not found: {commands_sc_dir}/")
        skipped += 1

    # 3. Remove .claude/agents/ directory
    agents_dir = base_path / "agents"
    if agents_dir.exists():
        if dry_run:
            item_count = sum(1 for _ in agents_dir.glob("*.md"))
            messages.append(f"[DRY-RUN] Would remove: {agents_dir}/ ({item_count} files)")
            removed += 1
        else:
            try:
                shutil.rmtree(agents_dir)
                messages.append(f"✅ Removed: {agents_dir}/")
                removed += 1
            except Exception as e:
                messages.append(f"❌ Failed to remove {agents_dir}/: {e}")
                failed += 1
    else:
        messages.append(f"⏭️  Not found: {agents_dir}/")
        skipped += 1

    # 4. Remove .claude/skills/ directory
    skills_dir = base_path / "skills"
    if skills_dir.exists():
        if dry_run:
            item_count = sum(1 for _ in skills_dir.iterdir() if _.is_dir())
            messages.append(f"[DRY-RUN] Would remove: {skills_dir}/ ({item_count} skills)")
            removed += 1
        else:
            try:
                shutil.rmtree(skills_dir)
                messages.append(f"✅ Removed: {skills_dir}/")
                removed += 1
            except Exception as e:
                messages.append(f"❌ Failed to remove {skills_dir}/: {e}")
                failed += 1
    else:
        messages.append(f"⏭️  Not found: {skills_dir}/")
        skipped += 1

    # 5. Remove .claude/hooks/hooks.json file
    hooks_json = base_path / "hooks" / "hooks.json"
    if hooks_json.exists():
        if dry_run:
            messages.append(f"[DRY-RUN] Would remove: {hooks_json}")
            removed += 1
        else:
            try:
                hooks_json.unlink()
                messages.append(f"✅ Removed: {hooks_json}")
                removed += 1
                # Remove hooks directory if empty
                hooks_dir = base_path / "hooks"
                if hooks_dir.exists() and not any(hooks_dir.iterdir()):
                    hooks_dir.rmdir()
            except Exception as e:
                messages.append(f"❌ Failed to remove {hooks_json}: {e}")
                failed += 1
    else:
        messages.append(f"⏭️  Not found: {hooks_json}")
        skipped += 1

    # 6. Remove SuperClaude hooks from settings.json (preserve user hooks)
    if keep_settings:
        messages.append("⏭️  Skipped: settings.json hooks (--keep-settings)")
        skipped += 1
    else:
        if dry_run:
            settings_file = base_path / "settings.json"
            if settings_file.exists():
                settings = _load_settings(settings_file)
                if "hooks" in settings:
                    sc_hook_count = sum(
                        1 for hook_array in settings["hooks"].values()
                        for h in hook_array if _is_superclaude_hook(h)
                    )
                    if sc_hook_count > 0:
                        messages.append(f"[DRY-RUN] Would remove {sc_hook_count} SuperClaude hooks from settings.json")
                        removed += 1
                    else:
                        messages.append("⏭️  No SuperClaude hooks in settings.json")
                        skipped += 1
                else:
                    messages.append("⏭️  No hooks section in settings.json")
                    skipped += 1
            else:
                messages.append("⏭️  No settings.json found")
                skipped += 1
        else:
            success, msg = uninstall_hooks_from_settings(base_path)
            if success:
                messages.append(f"✅ {msg}")
                removed += 1
            else:
                messages.append(f"❌ {msg}")
                failed += 1

    # 7. Remove @superclaude import from CLAUDE.md
    if dry_run:
        claude_md = base_path / "CLAUDE.md"
        if claude_md.exists():
            content = claude_md.read_text(encoding="utf-8")
            if "@superclaude" in content:
                messages.append("[DRY-RUN] Would remove SuperClaude import from CLAUDE.md")
                removed += 1
            else:
                messages.append("⏭️  No SuperClaude import in CLAUDE.md")
                skipped += 1
        else:
            messages.append("⏭️  No CLAUDE.md found")
            skipped += 1
    else:
        success, msg = remove_claude_md_import(base_path)
        if success:
            messages.append(f"✅ {msg}")
            removed += 1
        else:
            messages.append(f"❌ {msg}")
            failed += 1

    # Summary
    messages.append("")
    if dry_run:
        messages.append(f"📊 Summary (DRY-RUN): {removed} would be removed, {skipped} not found/skipped")
        messages.append("\n💡 Run without --dry-run to actually remove components")
    else:
        messages.append(f"📊 Summary: {removed} removed, {skipped} skipped, {failed} failed")
        messages.append(f"📁 Uninstall directory: {base_path}")

        if failed == 0 and removed > 0:
            messages.append("\n🔄 Restart Claude Code to complete the uninstall")

    overall_success = failed == 0
    return overall_success, "\n".join(messages)
