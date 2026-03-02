"""
SuperClaude CLI Main Entry Point

Provides command-line interface for SuperClaude operations.
"""

import re
import sys
from pathlib import Path

import click

from superclaude import __version__
from superclaude.hooks.inline_hooks import parse_frontmatter


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
@click.option("--status", "show_status", is_flag=True, help="Show MCP server status with fallbacks")
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
def mcp(servers, list_only, show_status, scope, dry_run):
    """
    Install and manage MCP servers for Claude Code

    Examples:
        superclaude mcp --list
        superclaude mcp --status
        superclaude mcp --servers tavily --servers context7
        superclaude mcp --scope project
        superclaude mcp --dry-run
    """
    from .install_mcp import (
        install_mcp_servers,
        list_available_servers,
        show_mcp_status,
    )

    if list_only:
        list_available_servers()
        return

    if show_status:
        show_mcp_status()
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
        skill_name=skill_name, target_path=target_path, force=force, scope=scope
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
        fm = parse_frontmatter(content)

        click.echo(f"📋 Agent: {agent_file.stem}\n")
        click.echo(f"   Name: {fm.get('name', agent_file.stem)}")
        click.echo(f"   Description: {fm.get('description', 'N/A')}")
        if fm.get('context'):
            click.echo(f"   Context: {fm.get('context')}")

        click.echo(f"\n   File: {agent_file}")
        click.echo(f"   Tokens: ~{len(content) // 4}")
        return

    # Default: list agents
    click.echo(f"📋 Available Agents (scope: {scope}):\n")

    for agent_file in agent_files:
        content = agent_file.read_text(encoding="utf-8")

        # Parse frontmatter for description
        fm = parse_frontmatter(content)
        description = fm.get("description", "N/A")
        if len(description) > 50:
            description = description[:47] + "..."

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
    "--lint",
    is_flag=True,
    help="Lint all skills for structural issues",
)
@click.option(
    "--version-list",
    "version_list",
    is_flag=True,
    help="Show version info for all installed skills",
)
@click.option(
    "--outdated",
    is_flag=True,
    help="Check for outdated skills (requires registry)",
)
@click.option(
    "--deps",
    is_flag=True,
    help="Show skill dependency graph",
)
@click.option(
    "--deps-check",
    "deps_check",
    is_flag=True,
    help="Check for missing or circular dependencies",
)
@click.option(
    "--scope",
    default="user",
    type=click.Choice(["user", "project"]),
    help="Scope to check: user (~/.claude/) or project (./.claude/)",
)
def skills(
    list_only: bool,
    skill_name: str,
    tokens: bool,
    lint: bool,
    version_list: bool,
    outdated: bool,
    deps: bool,
    deps_check: bool,
    scope: str,
):
    """
    Manage and inspect SuperClaude skills

    v2.1.0 Features:
    - Skill discovery with frontmatter parsing
    - Token estimation for context budgeting
    - Skill detail inspection

    Examples:
        superclaude skills --list
        superclaude skills --info sc-confidence-check
        superclaude skills --tokens
        superclaude skills --lint
    """
    from .install_commands import get_base_path

    # Lint mode: use source skills directory
    if lint:
        try:
            from superclaude.skills._testing.skill_linter import lint_all_skills

            package_root = Path(__file__).resolve().parent.parent
            skills_dir = package_root / "skills"

            if not skills_dir.exists():
                click.echo("⚠️  No source skills directory found")
                sys.exit(1)

            results = lint_all_skills(skills_dir)
            if not results:
                click.echo("⚠️  No skills found to lint")
                sys.exit(1)

            click.echo(f"🔍 Linting {len(results)} skill(s):\n")
            all_passed = True
            for r in results:
                icon = "✅" if r.passed else "❌"
                click.echo(f"   {icon} {r.skill_name:25} {r.error_count} errors, {r.warning_count} warnings")
                for issue in r.issues:
                    severity = "E" if issue.severity == "error" else "W"
                    click.echo(f"      [{severity}] {issue.rule}: {issue.message}")
                if not r.passed:
                    all_passed = False

            click.echo()
            passed_count = sum(1 for r in results if r.passed)
            click.echo(f"   {passed_count}/{len(results)} skills passed")

            if not all_passed:
                sys.exit(1)
        except ImportError:
            click.echo("❌ Skill linter not available — install superclaude[dev]")
            sys.exit(1)
        return

    # Outdated mode: placeholder for future registry
    if outdated:
        click.echo(
            "Registry not configured. Version comparison requires a skill registry "
            "(planned for v5.2.0+ajitta)."
        )
        return

    # Version list mode: show skill versions from source
    if version_list:
        try:
            from superclaude.skills._testing.skill_linter import extract_dependencies

            package_root = Path(__file__).resolve().parent.parent
            skills_dir = package_root / "skills"

            if not skills_dir.exists():
                click.echo("⚠️  No source skills directory found")
                sys.exit(1)

            click.echo(f"📋 Skills Versions (scope: {scope}):\n")
            versioned = 0
            total = 0

            for entry in sorted(skills_dir.iterdir()):
                if not entry.is_dir() or entry.name.startswith("_"):
                    continue
                if not (entry / "SKILL.md").exists() and not (entry / "skill.md").exists():
                    continue

                deps = extract_dependencies(entry)
                ver = deps.get("version") or "unversioned"
                if ver != "unversioned":
                    versioned += 1
                total += 1
                click.echo(f"   {entry.name:25} {ver}")

            click.echo(
                f"\n   Total: {total} skills ({versioned} versioned, {total - versioned} unversioned)"
            )
        except ImportError:
            click.echo("❌ Dependency tools not available — install superclaude[dev]")
            sys.exit(1)
        return

    # Deps mode: show dependency graph
    if deps:
        try:
            from superclaude.skills._testing.dependency_resolver import build_graph

            package_root = Path(__file__).resolve().parent.parent
            skills_dir = package_root / "skills"

            if not skills_dir.exists():
                click.echo("⚠️  No source skills directory found")
                sys.exit(1)

            graph = build_graph(skills_dir)
            nodes = graph.nodes
            enhancements = graph.enhancement_map()

            click.echo(f"📊 Skill Dependencies ({len(nodes)} skills):\n")
            for name in sorted(nodes):
                node = nodes[name]
                parts = [f"   {name:25}"]
                if node.requires_skills:
                    parts.append(f"requires: {', '.join(node.requires_skills)}")
                if node.requires_mcp:
                    parts.append(f"mcp: {', '.join(node.requires_mcp)}")
                if name in enhancements:
                    parts.append(f"enhanced by: {', '.join(enhancements[name])}")
                if len(parts) == 1:
                    parts.append("(no dependencies)")
                click.echo("  ".join(parts))

            order = graph.resolve_all()
            click.echo(f"\n   Install order: {' → '.join(order)}")
        except ImportError:
            click.echo("❌ Dependency resolver not available — install superclaude[dev]")
            sys.exit(1)
        return

    # Deps check mode: validate dependencies
    if deps_check:
        try:
            from superclaude.skills._testing.dependency_resolver import build_graph

            package_root = Path(__file__).resolve().parent.parent
            skills_dir = package_root / "skills"

            if not skills_dir.exists():
                click.echo("⚠️  No source skills directory found")
                sys.exit(1)

            graph = build_graph(skills_dir)
            cycles = graph.check_circular()
            missing = graph.missing_dependencies()

            click.echo("🔍 Dependency Check:\n")

            if not cycles and not missing:
                click.echo("   ✅ No circular dependencies")
                click.echo("   ✅ No missing dependencies")
            else:
                if cycles:
                    click.echo(f"   ❌ Circular dependencies found:")
                    for a, b in cycles:
                        click.echo(f"      {a} ↔ {b}")
                else:
                    click.echo("   ✅ No circular dependencies")

                if missing:
                    click.echo(f"   ⚠️  Missing dependencies:")
                    for issue in missing:
                        click.echo(f"      [{issue.kind}] {issue.message}")
                else:
                    click.echo("   ✅ No missing dependencies")

            if cycles:
                sys.exit(1)
        except ImportError:
            click.echo("❌ Dependency resolver not available — install superclaude[dev]")
            sys.exit(1)
        return

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
        fm = parse_frontmatter(content)

        click.echo(f"📋 Skill: {skill_dir.name}\n")
        click.echo(f"   Name: {fm.get('name', skill_dir.name)}")
        click.echo(f"   Description: {fm.get('description', 'N/A')}")
        if fm.get('context'):
            click.echo(f"   Context: {fm.get('context')}")
        if fm.get('agent'):
            click.echo(f"   Agent: {fm.get('agent')}")
        if fm.get('hooks'):
            click.echo(f"   Hooks: {list(fm.get('hooks', {}).keys())}")

        click.echo(f"\n   Path: {skill_dir}")

        # Count files
        file_count = sum(1 for f in skill_dir.glob("**/*") if f.is_file())
        click.echo(f"   Files: {file_count}")
        return

    # Default: list skills
    click.echo(f"📋 Available Skills (scope: {scope}):\n")

    migrated_count = 0
    original_count = 0

    for skill_dir, manifest in skill_dirs:
        content = manifest.read_text(encoding="utf-8")

        # Parse frontmatter
        fm = parse_frontmatter(content)
        description = fm.get("description", "N/A")
        if len(description) > 40:
            description = description[:37] + "..."
        context = " [fork]" if fm.get("context") == "fork" else ""

        # Determine skill type
        is_migrated = skill_dir.name.startswith("sc-")
        if is_migrated:
            migrated_count += 1
        else:
            original_count += 1

        if list_only and not tokens:
            # Simple list mode
            tag = "[migrated]" if is_migrated else "[original]"
            click.echo(f"   {skill_dir.name:25} {tag:12} {description}{context}")
        else:
            click.echo(f"   {skill_dir.name:25} {description}{context}")

    click.echo(f"\n   Total: {len(skill_dirs)} skills ({migrated_count} migrated, {original_count} original)")
    click.echo("   Use --info <skill> for details, --tokens for estimates")


@main.command()
def version():
    """Show SuperClaude version"""
    click.echo(f"SuperClaude version {__version__}")


if __name__ == "__main__":
    main()
