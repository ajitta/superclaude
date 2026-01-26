"""
Path Resolution for SuperClaude Installation

Provides path constants and resolution functions used by all install modules.
This is a leaf dependency with no internal imports.
"""

from pathlib import Path

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
