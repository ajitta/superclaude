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
            source_count = (
                sum(
                    1
                    for d in source_dir.iterdir()
                    if d.is_dir() and not d.name.startswith(("_", "."))
                )
                if source_dir.exists()
                else 0
            )
            installed_count = (
                sum(
                    1
                    for d in target_dir.iterdir()
                    if d.is_dir() and not d.name.startswith(("_", "."))
                )
                if target_dir.exists()
                else 0
            )
        else:
            source_count = (
                sum(1 for f in source_dir.glob("*.md") if f.stem.upper() != "README")
                if source_dir.exists()
                else 0
            )
            installed_count = (
                sum(1 for f in target_dir.glob("*.md") if f.stem.upper() != "README")
                if target_dir.exists()
                else 0
            )

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
        scripts_available += sum(
            1 for f in scripts_source.glob("*.py") if f.name != "__init__.py"
        )

    scripts_installed = 0
    if scripts_target.exists():
        scripts_installed = sum(1 for f in scripts_target.glob("*.sh"))
        scripts_installed += sum(
            1 for f in scripts_target.glob("*.py") if f.name != "__init__.py"
        )

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
    keep_settings: bool = False,
    keep_mcp: bool = True,
) -> Tuple[bool, str]:
    """
    Uninstall all SuperClaude components.

    This function removes:
    1. .claude/superclaude/ directory (entire directory)
    2. .claude/hooks/hooks.json file
    3. SuperClaude hooks from settings.json (preserves user hooks)
    4. @superclaude import from CLAUDE.md
    5. MCP servers registered by SuperClaude at the given scope
       (scope-aware; user-added servers are preserved)

    Args:
        base_path: Installation base path (default: ~/.claude or ./.claude based on scope)
        scope: Installation scope ("user", "project", or "local")
        dry_run: If True, only show what would be removed
        keep_settings: If True, don't modify settings.json hooks
        keep_mcp: If True (default), don't remove MCP server registrations.
            MCP servers are a shared CC resource — other tools/agents may
            rely on them, so we preserve them by default. Pass False (via
            `uninstall --remove-mcp`) to also clean SuperClaude-registered
            servers at this scope.

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
            messages.append(
                f"[DRY-RUN] Would remove: {superclaude_dir}/ ({item_count} files)"
            )
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
            messages.append(
                f"[DRY-RUN] Would remove: {commands_sc_dir}/ ({item_count} files)"
            )
            removed += 1
        else:
            try:
                shutil.rmtree(commands_sc_dir)
                # Remove empty parent commands/ directory
                commands_parent = commands_sc_dir.parent
                if commands_parent.exists() and not any(commands_parent.iterdir()):
                    commands_parent.rmdir()
                    messages.append(
                        f"✅ Removed: {commands_sc_dir}/ (and empty {commands_parent.name}/)"
                    )
                else:
                    messages.append(f"✅ Removed: {commands_sc_dir}/")
                removed += 1
            except Exception as e:
                messages.append(f"❌ Failed to remove {commands_sc_dir}/: {e}")
                failed += 1
    else:
        messages.append(f"⏭️  Not found: {commands_sc_dir}/")
        skipped += 1

    # 3. Remove SuperClaude-installed agents (preserves user-added agents)
    agents_dir = base_path / "agents"
    agents_source = _get_source_dir("agents")
    if agents_dir.exists():
        sc_agent_names = (
            {f.name for f in agents_source.glob("*.md")}
            if agents_source.exists()
            else set()
        )
        sc_agents_present = [
            agents_dir / name
            for name in sc_agent_names
            if (agents_dir / name).is_file()
        ]
        if sc_agents_present:
            if dry_run:
                messages.append(
                    f"[DRY-RUN] Would remove: {len(sc_agents_present)} SC agent file(s) from {agents_dir}/"
                )
                removed += 1
            else:
                try:
                    for f in sc_agents_present:
                        f.unlink()
                    if not any(agents_dir.iterdir()):
                        agents_dir.rmdir()
                        messages.append(
                            f"✅ Removed: {agents_dir}/ (empty after SC cleanup)"
                        )
                    else:
                        messages.append(
                            f"✅ Removed: {len(sc_agents_present)} SC agent file(s) from {agents_dir}/ (preserved non-SC files)"
                        )
                    removed += 1
                except Exception as e:
                    messages.append(
                        f"❌ Failed to remove SC agents from {agents_dir}/: {e}"
                    )
                    failed += 1
        else:
            messages.append(f"⏭️  No SC agents found in: {agents_dir}/")
            skipped += 1
    else:
        messages.append(f"⏭️  Not found: {agents_dir}/")
        skipped += 1

    # 4. Remove SuperClaude-installed skills (preserves user-added skills)
    skills_dir = base_path / "skills"
    skills_source = _get_source_dir("skills")
    if skills_dir.exists():
        sc_skill_names = (
            {
                d.name
                for d in skills_source.iterdir()
                if d.is_dir() and not d.name.startswith(("_", "."))
            }
            if skills_source.exists()
            else set()
        )
        sc_skills_present = [
            skills_dir / name for name in sc_skill_names if (skills_dir / name).is_dir()
        ]
        if sc_skills_present:
            if dry_run:
                messages.append(
                    f"[DRY-RUN] Would remove: {len(sc_skills_present)} SC skill(s) from {skills_dir}/"
                )
                removed += 1
            else:
                try:
                    for d in sc_skills_present:
                        shutil.rmtree(d)
                    if not any(skills_dir.iterdir()):
                        skills_dir.rmdir()
                        messages.append(
                            f"✅ Removed: {skills_dir}/ (empty after SC cleanup)"
                        )
                    else:
                        messages.append(
                            f"✅ Removed: {len(sc_skills_present)} SC skill(s) from {skills_dir}/ (preserved non-SC skills)"
                        )
                    removed += 1
                except Exception as e:
                    messages.append(
                        f"❌ Failed to remove SC skills from {skills_dir}/: {e}"
                    )
                    failed += 1
        else:
            messages.append(f"⏭️  No SC skills found in: {skills_dir}/")
            skipped += 1
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

    # 5a. Remove hook runtime state files (written during normal operation).
    # Safe to remove — they will be regenerated if SuperClaude is reinstalled.
    for state_file in (base_path / "loop_guard_state.json",):
        if state_file.exists():
            if dry_run:
                messages.append(f"[DRY-RUN] Would remove: {state_file}")
                removed += 1
            else:
                try:
                    state_file.unlink()
                    messages.append(f"✅ Removed: {state_file}")
                    removed += 1
                except Exception as e:
                    messages.append(f"❌ Failed to remove {state_file}: {e}")
                    failed += 1

    # 6. Remove SuperClaude hooks from settings file (preserve user hooks)
    settings_filename = "settings.local.json" if scope == "local" else "settings.json"
    if keep_settings:
        messages.append(f"⏭️  Skipped: {settings_filename} hooks (--keep-settings)")
        skipped += 1
    else:
        if dry_run:
            settings_file = base_path / settings_filename
            if settings_file.exists():
                settings = _load_settings(settings_file)
                if "hooks" in settings:
                    sc_hook_count = sum(
                        1
                        for hook_array in settings["hooks"].values()
                        for h in hook_array
                        if _is_superclaude_hook(h)
                    )
                    if sc_hook_count > 0:
                        messages.append(
                            f"[DRY-RUN] Would remove {sc_hook_count} SuperClaude hooks from {settings_filename}"
                        )
                        removed += 1
                    else:
                        messages.append(
                            f"⏭️  No SuperClaude hooks in {settings_filename}"
                        )
                        skipped += 1
                else:
                    messages.append(f"⏭️  No hooks section in {settings_filename}")
                    skipped += 1
            else:
                messages.append(f"⏭️  No {settings_filename} found")
                skipped += 1
        else:
            success, msg = uninstall_hooks_from_settings(base_path, scope=scope)
            if success:
                messages.append(f"✅ {msg}")
                removed += 1
            else:
                messages.append(f"❌ {msg}")
                failed += 1

    # 7. Remove @superclaude import from CLAUDE.md (or CLAUDE.local.md for local scope)
    if scope == "local":
        claude_md_target = base_path.parent / "CLAUDE.local.md"
    else:
        claude_md_target = base_path / "CLAUDE.md"
    claude_md_label = claude_md_target.name

    if dry_run:
        if claude_md_target.exists():
            content = claude_md_target.read_text(encoding="utf-8")
            if "@superclaude" in content or "@.claude/superclaude" in content:
                messages.append(
                    f"[DRY-RUN] Would remove SuperClaude import from {claude_md_label}"
                )
                removed += 1
            else:
                messages.append(f"⏭️  No SuperClaude import in {claude_md_label}")
                skipped += 1
        else:
            messages.append(f"⏭️  No {claude_md_label} found")
            skipped += 1
    else:
        success, msg = remove_claude_md_import(base_path, scope=scope)
        if success:
            messages.append(f"✅ {msg}")
            removed += 1
        else:
            messages.append(f"❌ {msg}")
            failed += 1

    # 8. Remove .git/info/exclude block for local scope (and migrate any
    #    legacy block from .gitignore for backward-compat)
    if scope == "local":
        project_root = base_path.parent
        if dry_run:
            from .install_git_exclude import (
                has_exclude_block,
                has_legacy_gitignore_block,
            )

            in_exclude = has_exclude_block(project_root)
            in_legacy = has_legacy_gitignore_block(project_root)
            if in_exclude or in_legacy:
                locations = []
                if in_exclude:
                    locations.append(".git/info/exclude")
                if in_legacy:
                    locations.append(".gitignore (legacy)")
                messages.append(
                    f"[DRY-RUN] Would remove SC local block from {', '.join(locations)}"
                )
                removed += 1
            else:
                messages.append(f"⏭️  No SC local block found in {project_root}")
                skipped += 1
        else:
            from .install_git_exclude import remove_local_git_exclude

            gi_ok, gi_msg = remove_local_git_exclude(project_root)
            messages.append(f"{'✅' if gi_ok else '❌'} {gi_msg}")
            if gi_ok:
                removed += 1
            else:
                failed += 1

    # 9. Remove SuperClaude-registered MCP servers (scope-aware, preserves user servers)
    if keep_mcp:
        messages.append(
            "⏭️  Skipped: MCP server cleanup (default; pass --remove-mcp to clean)"
        )
        skipped += 1
    else:
        from .install_mcp import uninstall_mcp_servers

        project_root = base_path.parent if scope in ("project", "local") else None
        mcp_removed, mcp_skipped, mcp_failed, mcp_messages = uninstall_mcp_servers(
            scope=scope,
            project_root=project_root,
            dry_run=dry_run,
        )
        messages.extend(mcp_messages)
        if mcp_removed == 0 and mcp_failed == 0:
            messages.append(f"⏭️  No SuperClaude MCP servers at {scope} scope")
            skipped += 1
        else:
            removed += mcp_removed
            failed += mcp_failed

    # 10. For project/local scope: rmdir empty .claude/ if nothing else remains
    if not dry_run and scope in ("project", "local"):
        if base_path.exists() and not any(base_path.iterdir()):
            try:
                base_path.rmdir()
                messages.append(f"✅ Removed empty: {base_path}/")
            except OSError:
                pass

    # Summary
    messages.append("")
    if dry_run:
        messages.append(
            f"📊 Summary (DRY-RUN): {removed} would be removed, {skipped} not found/skipped"
        )
        messages.append("\n💡 Run without --dry-run to actually remove components")
    else:
        messages.append(
            f"📊 Summary: {removed} removed, {skipped} skipped, {failed} failed"
        )
        messages.append(f"📁 Uninstall directory: {base_path}")

        if failed == 0 and removed > 0:
            messages.append("\n🔄 Restart Claude Code to complete the uninstall")

    overall_success = failed == 0
    return overall_success, "\n".join(messages)
