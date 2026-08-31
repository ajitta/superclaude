"""
Path Resolution for SuperClaude Installation

Provides path constants and resolution functions used by all install modules.
Leaf dependency: imports no other cli module, so every install module can import
it without a cycle. superclaude.utils is allowed — it imports nothing from cli.
"""

from pathlib import Path

from superclaude.utils import detect_scope

# Component definitions: (source_subdir, target_subdir, description)
# Note: hooks and scripts are handled specially by install_hooks_and_scripts()
COMPONENTS = {
    "commands": ("commands", "commands/sc", "Slash commands"),
    "agents": ("agents", "agents", "Agent definitions"),
    "core": ("core", "superclaude/core", "Core framework (PRINCIPLES, FLAGS, RULES)"),
    "modes": ("modes", "superclaude/modes", "Behavioral modes"),
    "mcp": ("mcp", "superclaude/mcp", "MCP server documentation"),
    "templates": (
        "templates",
        "superclaude/templates",
        "Doc scaffold templates (consumed by /sc:init, not slash commands)",
    ),
}


def get_base_path(scope: str = "user") -> Path:
    """
    Get base installation path based on scope.

    Args:
        scope: "user" for ~/.claude/, "project" for ./.claude/ (team-shared),
               or "local" for ./.claude/ (personal, gitignored)

    Returns:
        Path to base installation directory
    """
    if scope in ("project", "local"):
        return Path.cwd() / ".claude"
    else:  # user (default)
        return Path.home() / ".claude"


def find_install_root(start: Path) -> Path | None:
    """Nearest ancestor of ``start`` holding a project/local install, if any.

    $HOME is a candidate like any other. Skipping it — the first attempt at
    stopping a user-scope install from reading as a project one — made
    ``detect_scope``'s local-at-$HOME branch unreachable through the CLI, so the
    two disagreed for an install that is legal to create. Naming the scope is
    ``detect_scope``'s job and it now ranks $HOME correctly; this function only
    finds the directory.

    Args:
        start: Directory to search from, inclusive

    Returns:
        The directory containing ``.claude/superclaude``, or None
    """
    for candidate in [start, *start.parents]:
        if (candidate / ".claude" / "superclaude").is_dir():
            return candidate
    return None


def resolve_reporting_target(
    scope: str | None = None, start: Path | None = None
) -> tuple[str, Path]:
    """Scope and base path for the read-only commands: doctor, verify-drift, audit.

    These walk up to the install, unlike ``get_base_path``, which deliberately
    anchors on the CWD because ``superclaude install`` writes where the user is
    standing. Reporting has no such constraint, and not walking up reproduced
    the failure this resolver exists to remove: run from ``src/``, every command
    reported a healthy local install as absent.

    An explicit --scope still decides the scope name; ``user`` always resolves
    to the home directory and never walks up.

    Args:
        scope: Scope the user asked for, or None to detect
        start: Directory to resolve from; defaults to the CWD

    Returns:
        Tuple of (scope name, base installation path)
    """
    if scope == "user":
        return "user", get_base_path("user")

    root = find_install_root(start or Path.cwd())
    if root is None:
        resolved = scope or "user"
        return resolved, get_base_path(resolved)
    return scope or detect_scope(root), root / ".claude"


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
        component: Component name (commands, agents, core, modes, mcp, templates)

    Returns:
        Path to component source directory
    """
    package_root = _get_package_root()
    source_subdir = COMPONENTS[component][0]

    package_dir = package_root / source_subdir
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


# Skills shipped by releases before the skills layer was deleted. SuperClaude
# ships no skills now, so there is no source dir to diff against — the names are
# listed literally. Both install and uninstall prune them: without the install
# side, an upgrade leaves the directories in place, the two auto-invocable ones
# (confidence-check, verbalized-sampling) keep firing with no source left to
# explain them, and a local-scope install no longer git-excludes them, so they
# surface as untracked files in a team repo.
LEGACY_SKILL_NAMES = (
    "confidence-check",
    "finishing-a-development-branch",
    "ship",
    "simplicity-coach",
    "verbalized-sampling",
)


def find_legacy_skills(base_path: Path) -> list:
    """Installed skill directories left behind by a pre-removal release.

    Only the exact shipped names are matched: ``.claude/skills`` is shared with
    every other tool that installs skills, so anything else there is someone
    else's and must be left alone.
    """
    skills_dir = base_path / "skills"
    return [
        skills_dir / name for name in LEGACY_SKILL_NAMES if (skills_dir / name).is_dir()
    ]
