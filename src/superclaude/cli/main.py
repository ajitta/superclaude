"""
SuperClaude CLI Main Entry Point

Provides command-line interface for SuperClaude operations.
"""

import sys
from pathlib import Path

import click

# Add parent directory to path to import superclaude
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from superclaude import __version__


@click.group()
@click.version_option(version=__version__, prog_name="SuperClaude")
def main():
    """
    SuperClaude - AI-enhanced development framework for Claude Code

    A pytest plugin providing PM Agent capabilities and optional skills system.
    """
    pass


@main.command()
@click.option(
    "--force",
    is_flag=True,
    help="Force reinstall if components already exist",
)
@click.option(
    "--list",
    "list_only",
    is_flag=True,
    help="List available commands without installing",
)
@click.option(
    "--list-all",
    "list_all",
    is_flag=True,
    help="List all components and their installation status",
)
@click.option(
    "--scope",
    default="user",
    type=click.Choice(["user", "project"]),
    help="Installation scope: user (~/.claude/) or project (./.claude/)",
)
def install(force: bool, list_only: bool, list_all: bool, scope: str):
    """
    Install all SuperClaude components to Claude Code

    Installs:
    - Slash commands to commands/sc/
    - Agent definitions to agents/
    - Skills to skills/
    - Framework files to superclaude/ (core, modes, mcp)

    Scopes:
    - user (default): Install to ~/.claude/
    - project: Install to ./.claude/ (current directory)

    Examples:
        superclaude install
        superclaude install --force
        superclaude install --scope project
        superclaude install --list
    """
    from .install_commands import (
        install_all,
        list_available_commands,
        list_installed_commands,
        list_all_components,
        get_base_path,
    )

    # Get base path based on scope
    base_path = get_base_path(scope)

    # List all components mode
    if list_all:
        components = list_all_components(base_path=base_path)
        click.echo(f"📋 SuperClaude Components (scope: {scope}):\n")
        for name, info in components.items():
            status = f"{info['installed']}/{info['available']}"
            icon = "✅" if info['installed'] == info['available'] and info['available'] > 0 else "⬜"
            click.echo(f"   {icon} {info['description']:40} [{status}]")
            click.echo(f"      └─ {info['target_path']}")
        return

    # List commands only mode
    if list_only:
        available = list_available_commands()
        installed = list_installed_commands(base_path=base_path)

        click.echo(f"📋 Available Commands (scope: {scope}):")
        for cmd in available:
            status = "✅ installed" if cmd in installed else "⬜ not installed"
            click.echo(f"   /{cmd:20} {status}")

        click.echo(f"\nTotal: {len(available)} available, {len(installed)} installed")
        return

    # Install all components
    click.echo(f"📦 Installing SuperClaude components (scope: {scope})...")
    click.echo()

    success, message = install_all(base_path=base_path, force=force, scope=scope)

    click.echo(message)

    if not success:
        sys.exit(1)


@main.command()
@click.option(
    "--scope",
    default="user",
    type=click.Choice(["user", "project"]),
    help="Uninstall scope: user (~/.claude/) or project (./.claude/)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be removed without actually removing",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.option(
    "--keep-settings",
    is_flag=True,
    help="Keep settings.json hooks (only remove files/directories)",
)
def uninstall(scope: str, dry_run: bool, yes: bool, keep_settings: bool):
    """
    Uninstall all SuperClaude components from Claude Code

    Removes:
    - superclaude/ directory (core, modes, mcp, scripts)
    - commands/sc/ directory (slash commands)
    - agents/ directory
    - skills/ directory
    - hooks/hooks.json file
    - SuperClaude hooks from settings.json (preserves user hooks)
    - @superclaude import from CLAUDE.md

    Scopes:
    - user (default): Uninstall from ~/.claude/
    - project: Uninstall from ./.claude/ (current directory)

    Examples:
        superclaude uninstall --dry-run        # Preview what will be removed
        superclaude uninstall --yes            # Skip confirmation
        superclaude uninstall --scope project  # Uninstall from current project
        superclaude uninstall --keep-settings  # Keep settings.json hooks
    """
    from .install_commands import uninstall_all, get_base_path

    base_path = get_base_path(scope)

    # Dry-run mode: show what would be removed
    if dry_run:
        click.echo(f"🔍 Dry-run mode: Showing what would be removed (scope: {scope})\n")
        success, message = uninstall_all(
            base_path=base_path,
            scope=scope,
            dry_run=True,
            keep_settings=keep_settings
        )
        click.echo(message)
        return

    # Confirmation prompt (unless --yes)
    if not yes:
        click.echo(f"⚠️  This will remove SuperClaude from {base_path}")
        click.echo("   User hooks in settings.json will be preserved.\n")
        if not click.confirm("Do you want to continue?"):
            click.echo("❌ Uninstall cancelled")
            return

    click.echo(f"🗑️  Uninstalling SuperClaude components (scope: {scope})...")
    click.echo()

    success, message = uninstall_all(
        base_path=base_path,
        scope=scope,
        dry_run=False,
        keep_settings=keep_settings
    )

    click.echo(message)

    if not success:
        sys.exit(1)


@main.command()
@click.option("--servers", "-s", multiple=True, help="Specific MCP servers to install")
@click.option("--list", "list_only", is_flag=True, help="List available MCP servers")
@click.option(
    "--scope",
    default="user",
    type=click.Choice(["local", "project", "user"]),
    help="Installation scope",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be installed without actually installing",
)
def mcp(servers, list_only, scope, dry_run):
    """
    Install and manage MCP servers for Claude Code

    Examples:
        superclaude mcp --list
        superclaude mcp --servers tavily --servers context7
        superclaude mcp --scope project
        superclaude mcp --dry-run
    """
    from .install_mcp import install_mcp_servers, list_available_servers

    if list_only:
        list_available_servers()
        return

    click.echo(f"🔌 Installing MCP servers (scope: {scope})...")
    click.echo()

    success, message = install_mcp_servers(
        selected_servers=list(servers) if servers else None,
        scope=scope,
        dry_run=dry_run,
    )

    click.echo(message)

    if not success:
        sys.exit(1)


@main.command()
@click.option(
    "--target",
    default="~/.claude/commands/sc",
    help="Installation directory (default: ~/.claude/commands/sc)",
)
def update(target: str):
    """
    Update SuperClaude commands to latest version

    Re-installs all slash commands to match the current package version.
    This is a convenience command equivalent to 'install --force'.

    Example:
        superclaude update
        superclaude update --target /custom/path
    """
    from .install_commands import install_commands

    target_path = Path(target).expanduser()

    click.echo(f"🔄 Updating SuperClaude commands to version {__version__}...")
    click.echo()

    success, message = install_commands(target_path=target_path, force=True)

    click.echo(message)

    if not success:
        sys.exit(1)


@main.command()
@click.argument("skill_name")
@click.option(
    "--target",
    default="~/.claude/skills",
    help="Installation directory (default: ~/.claude/skills)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force reinstall if skill already exists",
)
def install_skill(skill_name: str, target: str, force: bool):
    """
    Install a SuperClaude skill to Claude Code

    SKILL_NAME: Name of the skill to install (e.g., pm-agent)

    Example:
        superclaude install-skill pm-agent
        superclaude install-skill pm-agent --target ~/.claude/skills --force
    """
    from .install_skill import install_skill_command

    target_path = Path(target).expanduser()

    click.echo(f"📦 Installing skill '{skill_name}' to {target_path}...")

    success, message = install_skill_command(
        skill_name=skill_name, target_path=target_path, force=force
    )

    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed diagnostic information",
)
def doctor(verbose: bool):
    """
    Check SuperClaude installation health

    Verifies:
        - pytest plugin loaded correctly
        - Skills installed (if any)
        - Configuration files present
    """
    from .doctor import run_doctor

    click.echo("🔍 SuperClaude Doctor\n")

    results = run_doctor(verbose=verbose)

    # Display results
    for check in results["checks"]:
        status_symbol = "✅" if check["passed"] else "❌"
        click.echo(f"{status_symbol} {check['name']}")

        if verbose and check.get("details"):
            for detail in check["details"]:
                click.echo(f"    {detail}")

    # Summary
    click.echo()
    total = len(results["checks"])
    passed = sum(1 for check in results["checks"] if check["passed"])

    if passed == total:
        click.echo("✅ SuperClaude is healthy")
    else:
        click.echo(f"⚠️  {total - passed}/{total} checks failed")
        sys.exit(1)


@main.command()
def version():
    """Show SuperClaude version"""
    click.echo(f"SuperClaude version {__version__}")


if __name__ == "__main__":
    main()
