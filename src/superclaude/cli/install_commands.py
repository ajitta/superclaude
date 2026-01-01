"""
SuperClaude Installation

Installs all SuperClaude components to ~/.claude/ or ./.claude/ directory:
- commands/sc/     : Slash commands
- agents/          : Agent definitions
- skills/          : Skills
- hooks/           : Hook scripts (copied from scripts/, config merged into settings.json)
- superclaude/     : Framework files (core, modes, mcp, CLAUDE_SC.md)
- CLAUDE.md        : Auto-configured to import CLAUDE_SC.md
- settings.json    : Hook configurations merged from hooks/hooks.json

Supports two scopes:
- user: ~/.claude/ (default)
- project: ./.claude/ (current directory)
"""

import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Import line to add to CLAUDE.md
CLAUDE_SC_IMPORT = "@superclaude/CLAUDE_SC.md"


def get_base_path(scope: str = "user") -> Path:
    """
    Get base installation path based on scope.

    Args:
        scope: "user" for ~/.claude/ or "project" for ./.claude/

    Returns:
        Path to base installation directory
    """
    if scope == "project":
        return Path.cwd() / ".claude"
    else:  # user (default)
        return Path.home() / ".claude"

# Component definitions: (source_subdir, target_subdir, description)
# Note: hooks and scripts are handled specially by install_hooks_and_scripts()
COMPONENTS = {
    "commands": ("commands", "commands/sc", "Slash commands"),
    "agents": ("agents", "agents", "Agent definitions"),
    "core": ("core", "superclaude/core", "Core framework (PRINCIPLES, FLAGS, RULES)"),
    "modes": ("modes", "superclaude/modes", "Behavioral modes"),
    "mcp": ("mcp", "superclaude/mcp", "MCP server documentation"),
    "skills": ("skills", "skills", "Skills"),
}


def _get_package_root() -> Path:
    """
    Get the package root directory.

    Returns:
        Path to superclaude package root (src/superclaude/ in dev, site-packages/superclaude/ when installed)
    """
    return Path(__file__).resolve().parent.parent


def _get_source_dir(component: str) -> Path:
    """
    Get source directory for a component.

    Args:
        component: Component name (commands, agents, core, modes, mcp, skills)

    Returns:
        Path to component source directory
    """
    package_root = _get_package_root()
    source_subdir = COMPONENTS[component][0]

    # Priority 1: Package directory (installed or editable)
    package_dir = package_root / source_subdir
    if package_dir.exists():
        return package_dir

    # Priority 2: plugins directory (legacy source checkout)
    repo_root = package_root.parent.parent
    plugins_dir = repo_root / "plugins" / "superclaude" / source_subdir
    if plugins_dir.exists():
        return plugins_dir

    return package_dir


def _get_target_dir(component: str, base_path: Path = None) -> Path:
    """
    Get target directory for a component.

    Args:
        component: Component name
        base_path: Base installation path (default: ~/.claude)

    Returns:
        Path to target directory
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    target_subdir = COMPONENTS[component][1]
    return base_path / target_subdir


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
    force: bool = False
) -> Tuple[int, int, int, List[str]]:
    """
    Install hooks configuration and scripts.

    This function:
    1. Copies scripts from src/superclaude/scripts/ to .claude/hooks/
    2. Reads hooks/hooks.json and transforms paths
    3. Merges hooks configuration into settings.json

    Args:
        base_path: Base installation path (default: ~/.claude)
        force: Force reinstall

    Returns:
        Tuple of (installed_count, skipped_count, failed_count, messages)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    package_root = _get_package_root()
    scripts_source = package_root / "scripts"
    hooks_source = package_root / "hooks"
    hooks_target = base_path / "hooks"
    settings_file = base_path / "settings.json"

    installed = 0
    skipped = 0
    failed = 0
    messages = []

    # 1. Copy scripts to .claude/hooks/
    if scripts_source.exists():
        hooks_target.mkdir(parents=True, exist_ok=True)

        patterns = ["*.sh", "*.py"]
        for pattern in patterns:
            for source_file in scripts_source.glob(pattern):
                # Skip __init__.py and README files
                if source_file.name == "__init__.py" or source_file.stem.upper() == "README":
                    continue

                target_file = hooks_target / source_file.name
                if target_file.exists() and not force:
                    skipped += 1
                    continue

                try:
                    shutil.copy2(source_file, target_file)
                    installed += 1
                except Exception as e:
                    failed += 1
                    messages.append(f"Failed to copy {source_file.name}: {e}")

    # 2. Read hooks.json and transform paths
    hooks_json_file = hooks_source / "hooks.json"
    if hooks_json_file.exists():
        try:
            with open(hooks_json_file, "r", encoding="utf-8") as f:
                hooks_config = json.load(f)

            # Transform paths: ./scripts/* → .claude/hooks/*
            def transform_command(cmd: str) -> str:
                # Replace ./scripts/ with .claude/hooks/
                # Uses relative path from project root (works on all platforms)
                if "./scripts/" in cmd:
                    return cmd.replace("./scripts/", ".claude/hooks/")
                return cmd

            def transform_hooks(obj):
                """Recursively transform command paths in hooks configuration."""
                if isinstance(obj, dict):
                    result = {}
                    for key, value in obj.items():
                        if key == "command" and isinstance(value, str):
                            result[key] = transform_command(value)
                        else:
                            result[key] = transform_hooks(value)
                    return result
                elif isinstance(obj, list):
                    return [transform_hooks(item) for item in obj]
                else:
                    return obj

            transformed_hooks = transform_hooks(hooks_config)

            # 3. Merge into settings.json
            settings = {}
            if settings_file.exists():
                try:
                    with open(settings_file, "r", encoding="utf-8") as f:
                        settings = json.load(f)
                except json.JSONDecodeError:
                    messages.append("Warning: Existing settings.json is invalid, creating new one")

            # Check if hooks already exist
            if "hooks" in settings and not force:
                messages.append("Hooks already configured in settings.json (use --force to update)")
                skipped += 1
            else:
                # Merge hooks configuration
                if "hooks" in transformed_hooks:
                    settings["hooks"] = transformed_hooks["hooks"]
                else:
                    settings["hooks"] = transformed_hooks

                # Write updated settings.json
                base_path.mkdir(parents=True, exist_ok=True)
                with open(settings_file, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                    f.write("\n")

                installed += 1
                messages.append("Hooks configuration merged into settings.json")

        except Exception as e:
            failed += 1
            messages.append(f"Failed to process hooks.json: {e}")
    else:
        messages.append("hooks.json not found, skipping hooks configuration")

    return installed, skipped, failed, messages


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


def install_all(base_path: Path = None, force: bool = False) -> Tuple[bool, str]:
    """
    Install all SuperClaude components.

    Args:
        base_path: Base installation path (default: ~/.claude)
        force: Force reinstall if components exist

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
        base_path, force
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


def list_all_components(base_path: Path = None) -> Dict[str, Dict[str, any]]:
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

    # Hooks and scripts (special handling)
    scripts_source = package_root / "scripts"
    hooks_target = base_path / "hooks"
    settings_file = base_path / "settings.json"

    # Count scripts
    scripts_available = 0
    if scripts_source.exists():
        scripts_available = sum(1 for f in scripts_source.glob("*.sh"))
        scripts_available += sum(1 for f in scripts_source.glob("*.py") if f.name != "__init__.py")

    scripts_installed = 0
    if hooks_target.exists():
        scripts_installed = sum(1 for f in hooks_target.glob("*.sh"))
        scripts_installed += sum(1 for f in hooks_target.glob("*.py") if f.name != "__init__.py")

    # Check if hooks are configured in settings.json
    hooks_configured = False
    if settings_file.exists():
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
                hooks_configured = "hooks" in settings
        except (json.JSONDecodeError, IOError):
            pass

    result["hooks"] = {
        "description": "Hook scripts and configuration",
        "source_path": str(scripts_source),
        "target_path": str(hooks_target),
        "available": scripts_available,
        "installed": scripts_installed,
        "hooks_configured": hooks_configured,
    }

    return result
