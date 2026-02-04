"""
Component Installation & Orchestration for SuperClaude

Handles installing individual components, hooks/scripts, CLAUDE_SC.md,
and the top-level install_all orchestration.
"""

import json
import shutil
from pathlib import Path
from typing import List, Tuple

from .install_paths import (
    COMPONENTS,
    _get_package_root,
    _get_source_dir,
    _get_target_dir,
)
from .install_settings import (
    CLAUDE_SC_IMPORT,
    check_claude_md_import,
    merge_hooks_to_settings,
    update_claude_md_import,
)


def _safe_target_path(target: Path, base_path: Path) -> bool:
    """Check that a target path is safe (not a symlink to outside base_path).

    Args:
        target: Target path to validate
        base_path: Expected base directory

    Returns:
        True if the path is safe, False if it's a symlink to an unexpected location
    """
    if not target.exists():
        return True
    resolved = target.resolve()
    base_resolved = base_path.resolve()
    return str(resolved).startswith(str(base_resolved))


def install_component(
    component: str,
    base_path: Path = None,
    force: bool = False
) -> Tuple[int, int, int, List[str]]:
    """
    Install a single component.

    Args:
        component: Component name
        base_path: Base installation path
        force: Force reinstall

    Returns:
        Tuple of (installed_count, skipped_count, failed_count, failed_names)
    """
    source_dir = _get_source_dir(component)
    target_dir = _get_target_dir(component, base_path)

    if not source_dir.exists():
        return 0, 0, 1, [f"Source not found: {source_dir}"]

    target_dir.mkdir(parents=True, exist_ok=True)

    installed = 0
    skipped = 0
    failed = 0
    failed_names = []

    # Handle skills directory specially (has subdirectories)
    if component == "skills":
        for skill_dir in source_dir.iterdir():
            if skill_dir.is_dir():
                target_skill_dir = target_dir / skill_dir.name
                if target_skill_dir.exists() and not force:
                    skipped += 1
                    continue
                try:
                    if target_skill_dir.exists():
                        if not _safe_target_path(target_skill_dir, target_dir):
                            failed += 1
                            failed_names.append(f"{skill_dir.name}: symlink outside target")
                            continue
                        shutil.rmtree(target_skill_dir)
                    shutil.copytree(skill_dir, target_skill_dir)
                    installed += 1
                except Exception as e:
                    failed += 1
                    failed_names.append(f"{skill_dir.name}: {e}")
    else:
        # Copy .md files (excluding README.md)
        for source_file in source_dir.glob("*.md"):
            # Skip README files
            if source_file.stem.upper() == "README":
                continue

            target_file = target_dir / source_file.name
            if target_file.exists() and not force:
                skipped += 1
                continue
            try:
                shutil.copy2(source_file, target_file)
                installed += 1
            except Exception as e:
                failed += 1
                failed_names.append(f"{source_file.name}: {e}")

    return installed, skipped, failed, failed_names


def install_claude_sc_md(base_path: Path = None, force: bool = False) -> Tuple[bool, str]:
    """
    Install CLAUDE_SC.md to ~/.claude/superclaude/

    Args:
        base_path: Base installation path
        force: Force reinstall

    Returns:
        Tuple of (success, message)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    package_root = _get_package_root()
    source_file = package_root / "CLAUDE_SC.md"
    target_dir = base_path / "superclaude"
    target_file = target_dir / "CLAUDE_SC.md"

    if not source_file.exists():
        return False, f"CLAUDE_SC.md not found at {source_file}"

    target_dir.mkdir(parents=True, exist_ok=True)

    if target_file.exists() and not force:
        return True, "CLAUDE_SC.md already exists (use --force to reinstall)"

    try:
        shutil.copy2(source_file, target_file)
        return True, "CLAUDE_SC.md installed"
    except Exception as e:
        return False, f"Failed to install CLAUDE_SC.md: {e}"


def install_hooks_and_scripts(
    base_path: Path = None,
    force: bool = False,
    scope: str = "user"
) -> Tuple[int, int, int, List[str]]:
    """
    Install hooks configuration and scripts.

    This function:
    1. Copies scripts from src/superclaude/scripts/ to .claude/superclaude/scripts/
    2. Transforms hooks/hooks.json with correct paths and copies to .claude/hooks/hooks.json

    Args:
        base_path: Base installation path (default: ~/.claude)
        force: Force reinstall
        scope: Installation scope ("user", "project", or "target")

    Returns:
        Tuple of (installed_count, skipped_count, failed_count, messages)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    package_root = _get_package_root()
    scripts_source = package_root / "scripts"
    hooks_source = package_root / "hooks"
    scripts_target = base_path / "superclaude" / "scripts"
    hooks_target = base_path / "hooks"

    installed = 0
    skipped = 0
    failed = 0
    messages = []

    # Determine scripts path based on scope
    # - project scope: relative path (works from project root)
    # - user/target scope: absolute path (works from anywhere)
    if scope == "project":
        scripts_path_for_hooks = ".claude/superclaude/scripts"
    else:
        scripts_path_for_hooks = str(scripts_target.resolve())

    # 1. Copy scripts to .claude/superclaude/scripts/
    if scripts_source.exists():
        scripts_target.mkdir(parents=True, exist_ok=True)

        patterns = ["*.sh", "*.py"]
        for pattern in patterns:
            for source_file in scripts_source.glob(pattern):
                # Skip __init__.py and README files
                if source_file.name == "__init__.py" or source_file.stem.upper() == "README":
                    continue

                target_file = scripts_target / source_file.name
                if target_file.exists() and not force:
                    skipped += 1
                    continue

                try:
                    shutil.copy2(source_file, target_file)
                    installed += 1
                except Exception as e:
                    failed += 1
                    messages.append(f"Failed to copy {source_file.name}: {e}")

    # 2. Transform and copy hooks.json to .claude/hooks/hooks.json
    hooks_json_file = hooks_source / "hooks.json"
    if hooks_json_file.exists():
        hooks_target.mkdir(parents=True, exist_ok=True)
        target_hooks_json = hooks_target / "hooks.json"

        if target_hooks_json.exists() and not force:
            messages.append("hooks.json already exists (use --force to update)")
            skipped += 1
        else:
            try:
                # Read template and replace placeholder
                with open(hooks_json_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Replace {{SCRIPTS_PATH}} placeholder with actual path
                content = content.replace("{{SCRIPTS_PATH}}", scripts_path_for_hooks)

                # Write transformed content
                with open(target_hooks_json, "w", encoding="utf-8") as f:
                    f.write(content)

                installed += 1
                messages.append(f"hooks.json installed (scripts path: {scripts_path_for_hooks})")
            except Exception as e:
                failed += 1
                messages.append(f"Failed to install hooks.json: {e}")
    else:
        messages.append("hooks.json not found, skipping hooks configuration")

    # 3. Merge hooks to settings.json (ensures Claude Code recognizes hooks)
    if hooks_json_file.exists():
        try:
            # Read and transform hooks config
            with open(hooks_json_file, "r", encoding="utf-8") as f:
                hooks_content = f.read()
            # Use forward slashes for JSON compatibility (works on all platforms)
            scripts_path_json_safe = scripts_path_for_hooks.replace("\\", "/")
            hooks_content = hooks_content.replace("{{SCRIPTS_PATH}}", scripts_path_json_safe)
            hooks_config = json.loads(hooks_content)

            # Merge to settings.json
            merge_success, merge_msg = merge_hooks_to_settings(
                base_path=base_path,
                hooks_config=hooks_config,
                scope=scope,
                force=force
            )

            if merge_success:
                installed += 1
                messages.append(f"✓ {merge_msg}")
            else:
                failed += 1
                messages.append(f"✗ {merge_msg}")
        except json.JSONDecodeError as e:
            failed += 1
            messages.append(f"Failed to parse hooks.json for merge: {e}")
        except Exception as e:
            failed += 1
            messages.append(f"Failed to merge hooks to settings.json: {e}")

    return installed, skipped, failed, messages


def install_all(
    base_path: Path = None,
    force: bool = False,
    scope: str = "user"
) -> Tuple[bool, str]:
    """
    Install all SuperClaude components.

    Args:
        base_path: Base installation path (default: ~/.claude)
        force: Force reinstall if components exist
        scope: Installation scope ("user", "project", or "target")

    Returns:
        Tuple of (success: bool, message: str)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    messages = []
    total_installed = 0
    total_skipped = 0
    total_failed = 0

    # Install each component
    for component, (_, _, description) in COMPONENTS.items():
        installed, skipped, failed, failed_names = install_component(
            component, base_path, force
        )

        total_installed += installed
        total_skipped += skipped
        total_failed += failed

        if installed > 0:
            messages.append(f"✅ {description}: {installed} installed")
        if skipped > 0:
            messages.append(f"⏭️  {description}: {skipped} skipped")
        if failed > 0:
            messages.append(f"❌ {description}: {failed} failed")
            for name in failed_names:
                messages.append(f"   - {name}")

    # Install hooks and scripts
    hooks_installed, hooks_skipped, hooks_failed, hooks_messages = install_hooks_and_scripts(
        base_path, force, scope
    )
    total_installed += hooks_installed
    total_skipped += hooks_skipped
    total_failed += hooks_failed

    if hooks_installed > 0:
        messages.append(f"✅ Hooks and scripts: {hooks_installed} installed")
    if hooks_skipped > 0:
        messages.append(f"⏭️  Hooks and scripts: {hooks_skipped} skipped")
    if hooks_failed > 0:
        messages.append(f"❌ Hooks and scripts: {hooks_failed} failed")
    for msg in hooks_messages:
        messages.append(f"   {msg}")

    # Install CLAUDE_SC.md
    success, msg = install_claude_sc_md(base_path, force)
    messages.append(f"{'✅' if success else '❌'} {msg}")

    # Check and update CLAUDE.md import
    messages.append("")
    has_import, check_msg = check_claude_md_import(base_path)
    if has_import:
        messages.append(f"✅ {check_msg}")
    else:
        # Try to add the import
        update_success, update_msg = update_claude_md_import(base_path, force=False)
        if update_success:
            messages.append(f"✅ {update_msg}")
        else:
            messages.append(f"⚠️  {update_msg}")
            messages.append(f"   Add manually: {CLAUDE_SC_IMPORT}")

    # Summary
    messages.append("")
    messages.append(f"📊 Summary: {total_installed} installed, {total_skipped} skipped, {total_failed} failed")
    messages.append(f"📁 Installation directory: {base_path}")

    if total_skipped > 0:
        messages.append("\n💡 Tip: Use --force to reinstall existing files")

    messages.append("\n🔄 Restart Claude Code to use the new components")

    overall_success = total_failed == 0
    return overall_success, "\n".join(messages)


def install_commands(target_path: Path = None, force: bool = False) -> Tuple[bool, str]:
    """
    Install all SuperClaude commands to Claude Code (legacy function).

    Now installs ALL components, not just commands.

    Args:
        target_path: Base installation path (default: ~/.claude)
                     Note: Commands are installed to {base_path}/commands/sc/
        force: Force reinstall if commands exist

    Returns:
        Tuple of (success: bool, message: str)
    """
    # If target_path is provided, use its parent as base_path
    # (legacy behavior expected commands in target_path directly)
    if target_path is not None:
        base_path = target_path.parent if target_path.name == "commands" else target_path
    else:
        base_path = None
    return install_all(base_path=base_path, force=force)
