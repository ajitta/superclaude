"""
SuperClaude Installation

Installs all SuperClaude components to ~/.claude/ directory:
- commands/sc/     : Slash commands
- superclaude/     : Framework files (agents, core, modes, mcp, skills)
- CLAUDE.md        : Auto-configured to import CLAUDE_SC.md
"""

import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Import line to add to CLAUDE.md
CLAUDE_SC_IMPORT = "@superclaude/CLAUDE_SC.md"

# Component definitions: (source_subdir, target_subdir, description)
COMPONENTS = {
    "commands": ("commands", "commands/sc", "Slash commands"),
    "agents": ("agents", "superclaude/agents", "Agent definitions"),
    "core": ("core", "superclaude/core", "Core framework (PRINCIPLES, FLAGS, RULES)"),
    "modes": ("modes", "superclaude/modes", "Behavioral modes"),
    "mcp": ("mcp", "superclaude/mcp", "MCP server documentation"),
    "skills": ("skills", "superclaude/skills", "Skills"),
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
        target_path: Ignored (kept for backwards compatibility)
        force: Force reinstall if commands exist

    Returns:
        Tuple of (success: bool, message: str)
    """
    return install_all(force=force)


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


def list_installed_commands() -> List[str]:
    """
    List installed commands in ~/.claude/commands/sc/

    Returns:
        List of installed command names
    """
    commands_dir = Path.home() / ".claude" / "commands" / "sc"

    if not commands_dir.exists():
        return []

    installed = []
    for file in commands_dir.glob("*.md"):
        if file.stem != "README":
            installed.append(file.stem)

    return sorted(installed)


def list_all_components() -> Dict[str, Dict[str, any]]:
    """
    List all components with their installation status.

    Returns:
        Dict with component info and status
    """
    result = {}

    for component, (_, _, description) in COMPONENTS.items():
        source_dir = _get_source_dir(component)
        target_dir = _get_target_dir(component)

        # Count source files (excluding README.md)
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

    return result
