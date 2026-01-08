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
        get_base_path,
        install_all,
        list_all_components,
        list_available_commands,
        list_installed_commands,
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
    from .install_commands import get_base_path, uninstall_all

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
    "--scope",
    default="user",
    type=click.Choice(["user", "project"]),
    help="Installation scope: user (~/.claude/) or project (./.claude/)",
)
def update(scope: str):
    """
    Update SuperClaude commands to latest version

    Re-installs all components to match the current package version.
    This is a convenience command equivalent to 'install --force'.

    Scopes:
    - user (default): Update ~/.claude/
    - project: Update ./.claude/

    Example:
        superclaude update
        superclaude update --scope project
    """
    from .install_commands import get_base_path, install_all

    base_path = get_base_path(scope)

    click.echo(f"🔄 Updating SuperClaude to version {__version__} (scope: {scope})...")
    click.echo()

    success, message = install_all(base_path=base_path, force=True, scope=scope)

    click.echo(message)

    if not success:
        sys.exit(1)


@main.command()
@click.argument("skill_name")
@click.option(
    "--scope",
    default="user",
    type=click.Choice(["user", "project"]),
    help="Installation scope: user (~/.claude/) or project (./.claude/)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force reinstall if skill already exists",
)
def install_skill(skill_name: str, scope: str, force: bool):
    """
    Install a SuperClaude skill to Claude Code

    SKILL_NAME: Name of the skill to install (e.g., pm-agent)

    Scopes:
    - user (default): Install to ~/.claude/skills/
    - project: Install to ./.claude/skills/

    Example:
        superclaude install-skill pm-agent
        superclaude install-skill pm-agent --scope project --force
    """
    from .install_commands import get_base_path
    from .install_skill import install_skill_command

    base_path = get_base_path(scope)
    target_path = base_path / "skills"

    click.echo(f"📦 Installing skill '{skill_name}' (scope: {scope})...")

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


# =============================================================================
# PM Agent CLI Commands - DISABLED
# These commands use pm_agent Python implementation.
# Skill-based approach (confidence.ts) is preferred.
# To re-enable: uncomment the blocks below
# =============================================================================

# @main.command()
# @click.option("--task", "-t", help="Task name or description to check")
# @click.option("--json", "output_json", is_flag=True, help="Output as JSON")
# @click.option("--verbose", "-v", is_flag=True, help="Show detailed check results")
# @click.option("--project-root", "-p", type=click.Path(exists=True), help="Project root directory")
# def confidence(task: str, output_json: bool, verbose: bool, project_root: str):
#     """Run pre-implementation confidence check (DISABLED - use /confidence-check skill)"""
#     pass

# @main.command("self-check")
# @click.option("--tests-passed", "-t", is_flag=True, help="Mark tests as passed")
# @click.option("--json", "output_json", is_flag=True, help="Output as JSON")
# @click.option("--evidence", "-e", multiple=True, help="Evidence items")
# def self_check(tests_passed: bool, output_json: bool, evidence: tuple):
#     """Run post-implementation self-check protocol (DISABLED - use skill)"""
#     pass

# @main.command("token-budget")
# @click.option("--complexity", "-c", type=click.Choice(["simple", "medium", "complex"]), default="medium")
# @click.option("--json", "output_json", is_flag=True, help="Output as JSON")
# def token_budget(complexity: str, output_json: bool):
#     """Show token budget for task complexity (DISABLED - use skill)"""
#     pass


@main.command()
@click.option(
    "--list",
    "list_only",
    is_flag=True,
    help="List all available agents",
)
@click.option(
    "--info",
    "agent_name",
    default=None,
    help="Show details for a specific agent",
)
@click.option(
    "--tokens",
    is_flag=True,
    help="Show token estimates for all agents",
)
@click.option(
    "--scope",
    default="user",
    type=click.Choice(["user", "project"]),
    help="Scope to check: user (~/.claude/) or project (./.claude/)",
)
def agents(list_only: bool, agent_name: str, tokens: bool, scope: str):
    """
    Manage and inspect SuperClaude agents

    v2.1.0 Features:
    - Agent discovery and listing
    - Token estimation for context budgeting
    - Agent detail inspection

    Examples:
        superclaude agents --list
        superclaude agents --info backend-architect
        superclaude agents --tokens
        superclaude agents --scope project --list
    """
    from .install_commands import get_base_path

    base_path = get_base_path(scope)
    agents_path = base_path / "agents"

    if not agents_path.exists():
        click.echo(f"⚠️  No agents installed at {agents_path}")
        click.echo("   Run 'superclaude install' first")
        sys.exit(1)

    # Discover agents
    agent_files = sorted(agents_path.glob("*.md"))

    if not agent_files:
        click.echo(f"⚠️  No agent files found in {agents_path}")
        sys.exit(1)

    # Token estimation mode
    if tokens:
        click.echo(f"📊 Agent Token Estimates (scope: {scope}):\n")
        total_frontmatter = 0
        total_full = 0

        for agent_file in agent_files:
            content = agent_file.read_text(encoding="utf-8")
            full_tokens = len(content) // 4  # CHARS_PER_TOKEN

            # Extract frontmatter
            import re
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            frontmatter_tokens = len(match.group(1)) // 4 if match else 0

            total_frontmatter += frontmatter_tokens
            total_full += full_tokens

            click.echo(f"   {agent_file.stem:30} ~{frontmatter_tokens:4} tokens (full: ~{full_tokens})")

        click.echo()
        click.echo(f"   Total: ~{total_frontmatter} frontmatter, ~{total_full} full load")
        click.echo(f"   Agents: {len(agent_files)}")
        return

    # Info mode - show details for specific agent
    if agent_name:
        # Find agent file
        agent_file = None
        for f in agent_files:
            if f.stem == agent_name or f.stem.replace("-", "_") == agent_name.replace("-", "_"):
                agent_file = f
                break

        if not agent_file:
            click.echo(f"❌ Agent '{agent_name}' not found")
            click.echo(f"   Available agents: {', '.join(f.stem for f in agent_files[:5])}...")
            sys.exit(1)

        content = agent_file.read_text(encoding="utf-8")

        # Parse frontmatter
        import re

        import yaml
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                fm = yaml.safe_load(match.group(1))
            except Exception:
                fm = {}
        else:
            fm = {}

        click.echo(f"📋 Agent: {agent_file.stem}\n")
        click.echo(f"   Name: {fm.get('name', agent_file.stem)}")
        click.echo(f"   Description: {fm.get('description', 'N/A')}")
        if fm.get('triggers'):
            click.echo(f"   Triggers: {fm.get('triggers')}")
        if fm.get('context'):
            click.echo(f"   Context: {fm.get('context')}")
        if fm.get('allowed-tools'):
            click.echo(f"   Allowed Tools: {', '.join(fm.get('allowed-tools', []))}")

        click.echo(f"\n   File: {agent_file}")
        click.echo(f"   Tokens: ~{len(content) // 4}")
        return

    # Default: list agents
    click.echo(f"📋 Available Agents (scope: {scope}):\n")

    import re

    import yaml

    for agent_file in agent_files:
        content = agent_file.read_text(encoding="utf-8")

        # Parse frontmatter for description
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        description = "N/A"
        if match:
            try:
                fm = yaml.safe_load(match.group(1))
                description = fm.get("description", "N/A")
                if len(description) > 50:
                    description = description[:47] + "..."
            except Exception:
                pass

        click.echo(f"   {agent_file.stem:25} {description}")

    click.echo(f"\n   Total: {len(agent_files)} agents")
    click.echo("   Use --info <agent> for details, --tokens for estimates")


@main.command()
@click.option(
    "--list",
    "list_only",
    is_flag=True,
    help="List all available skills",
)
@click.option(
    "--info",
    "skill_name",
    default=None,
    help="Show details for a specific skill",
)
@click.option(
    "--tokens",
    is_flag=True,
    help="Show token estimates for all skills",
)
@click.option(
    "--scope",
    default="user",
    type=click.Choice(["user", "project"]),
    help="Scope to check: user (~/.claude/) or project (./.claude/)",
)
def skills(list_only: bool, skill_name: str, tokens: bool, scope: str):
    """
    Manage and inspect SuperClaude skills

    v2.1.0 Features:
    - Skill discovery with frontmatter parsing
    - Token estimation for context budgeting
    - Skill detail inspection

    Examples:
        superclaude skills --list
        superclaude skills --info confidence-check
        superclaude skills --tokens
    """
    from .install_commands import get_base_path

    base_path = get_base_path(scope)
    skills_path = base_path / "skills"

    if not skills_path.exists():
        click.echo(f"⚠️  No skills installed at {skills_path}")
        click.echo("   Run 'superclaude install' first")
        sys.exit(1)

    # Discover skills (directories with SKILL.md)
    skill_dirs = []
    for item in skills_path.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            manifest = item / "SKILL.md"
            if not manifest.exists():
                manifest = item / "skill.md"
            if manifest.exists():
                skill_dirs.append((item, manifest))

    skill_dirs.sort(key=lambda x: x[0].name)

    if not skill_dirs:
        click.echo(f"⚠️  No skills found in {skills_path}")
        sys.exit(1)

    # Token estimation mode
    if tokens:
        try:
            from superclaude.scripts.token_estimator import (
                format_token_report,
                get_context_token_summary,
            )
            summary = get_context_token_summary()
            report = format_token_report(summary)
            click.echo(report)
        except ImportError:
            click.echo("⚠️  Token estimator not available")
            sys.exit(1)
        return

    # Info mode
    if skill_name:
        skill_dir = None
        for d, m in skill_dirs:
            if d.name == skill_name or d.name.replace("-", "_") == skill_name.replace("-", "_"):
                skill_dir = d
                manifest = m
                break

        if not skill_dir:
            click.echo(f"❌ Skill '{skill_name}' not found")
            click.echo(f"   Available skills: {', '.join(d.name for d, _ in skill_dirs[:5])}...")
            sys.exit(1)

        content = manifest.read_text(encoding="utf-8")

        # Parse frontmatter
        import re

        import yaml
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                fm = yaml.safe_load(match.group(1))
            except Exception:
                fm = {}
        else:
            fm = {}

        click.echo(f"📋 Skill: {skill_dir.name}\n")
        click.echo(f"   Name: {fm.get('name', skill_dir.name)}")
        click.echo(f"   Description: {fm.get('description', 'N/A')}")
        if fm.get('triggers'):
            click.echo(f"   Triggers: {fm.get('triggers')}")
        if fm.get('context'):
            click.echo(f"   Context: {fm.get('context')} (v2.1.0)")
        if fm.get('agent'):
            click.echo(f"   Agent: {fm.get('agent')} (v2.1.0)")
        if fm.get('user-invocable') is False:
            click.echo("   User-Invocable: false (v2.1.0)")
        if fm.get('allowed-tools'):
            click.echo(f"   Allowed Tools: {len(fm.get('allowed-tools', []))} tools (v2.1.0)")
        if fm.get('hooks'):
            click.echo(f"   Hooks: {list(fm.get('hooks', {}).keys())} (v2.1.0)")

        click.echo(f"\n   Path: {skill_dir}")

        # Count files
        file_count = sum(1 for f in skill_dir.glob("**/*") if f.is_file())
        click.echo(f"   Files: {file_count}")
        return

    # Default: list skills
    click.echo(f"📋 Available Skills (scope: {scope}):\n")

    import re

    import yaml

    for skill_dir, manifest in skill_dirs:
        content = manifest.read_text(encoding="utf-8")

        # Parse frontmatter
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        description = "N/A"
        context = ""
        if match:
            try:
                fm = yaml.safe_load(match.group(1))
                description = fm.get("description", "N/A")
                if len(description) > 40:
                    description = description[:37] + "..."
                if fm.get("context") == "fork":
                    context = " [fork]"
            except Exception:
                pass

        click.echo(f"   {skill_dir.name:25} {description}{context}")

    click.echo(f"\n   Total: {len(skill_dirs)} skills")
    click.echo("   Use --info <skill> for details, --tokens for estimates")


@main.command()
def version():
    """Show SuperClaude version"""
    click.echo(f"SuperClaude version {__version__}")


if __name__ == "__main__":
    main()
