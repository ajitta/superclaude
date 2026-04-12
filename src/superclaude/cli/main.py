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
    - Behavioral modes to superclaude/modes/
    - Framework files to superclaude/ (core, mcp)

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

    SKILL_NAME: Name of the skill to install (e.g., project-manager)

    Scopes:
    - user (default): Install to ~/.claude/skills/
    - project: Install to ./.claude/skills/

    Example:
        superclaude install-skill project-manager
        superclaude install-skill project-manager --scope project --force
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

    for skill_dir, manifest in skill_dirs:
        content = manifest.read_text(encoding="utf-8")

        # Parse frontmatter
        fm = parse_frontmatter(content)
        description = fm.get("description", "N/A")
        if len(description) > 40:
            description = description[:37] + "..."
        context = " [fork]" if fm.get("context") == "fork" else ""

        click.echo(f"   {skill_dir.name:25} {description}{context}")

    click.echo(f"\n   Total: {len(skill_dirs)} skills")
    click.echo("   Use --info <skill> for details, --tokens for estimates")


@main.command(name="verify-drift")
@click.option(
    "--scope",
    default="user",
    type=click.Choice(["user", "project"]),
    help="Installation scope: user (~/.claude/) or project (./.claude/)",
)
@click.option("--verbose", is_flag=True, help="Show per-file details")
def verify_drift_cmd(scope: str, verbose: bool):
    """
    Check for installation drift between source and installed files.

    Compares each installed file against the package source to detect:
    - MISSING: source file not installed
    - DRIFTED: installed file differs from source
    - EXTRA: installed file has no source counterpart

    Examples:
        superclaude verify-drift
        superclaude verify-drift --verbose
        superclaude verify-drift --scope project
    """
    from .install_commands import get_base_path
    from .verify_drift import DRIFTED, EXTRA, MISSING, OK, verify_drift

    base_path = get_base_path(scope)
    click.echo(f"🔍 Checking installation drift (scope: {scope})...\n")

    result = verify_drift(base_path, verbose=verbose)

    # Display per-component results
    for comp, data in result["components"].items():
        ok = data["ok"]
        total = ok + data["drifted"] + data["missing"] + data["extra"]
        if total == 0:
            continue

        issues = data["drifted"] + data["missing"] + data["extra"]
        icon = "✅" if issues == 0 else "⚠️"
        click.echo(f"   {icon} {comp:15} {ok}/{total} OK", nl=False)
        parts = []
        if data["drifted"]:
            parts.append(f"{data['drifted']} drifted")
        if data["missing"]:
            parts.append(f"{data['missing']} missing")
        if data["extra"]:
            parts.append(f"{data['extra']} extra")
        if parts:
            click.echo(f"  ({', '.join(parts)})")
        else:
            click.echo()

        # Verbose: show individual files
        if verbose and data.get("files"):
            for fname, status in data["files"].items():
                s_icon = {"OK": "✅", "DRIFTED": "🔶", "MISSING": "❌", "EXTRA": "➕"}
                click.echo(f"      {s_icon.get(status, '?')} {fname}: {status}")

    # CLAUDE_SC.md
    sc = result["claude_sc_md"]
    sc_icon = "✅" if sc == OK else "⚠️"
    click.echo(f"   {sc_icon} CLAUDE_SC.md: {sc}")

    # Summary
    click.echo()
    if result["clean"]:
        click.echo("✅ No drift detected — installation matches source")
    else:
        click.echo(
            f"⚠️  Drift detected: {result['total_drifted']} drifted, "
            f"{result['total_missing']} missing, {result['total_extra']} extra"
        )
        click.echo("   Run 'superclaude install --force' to re-sync")
        sys.exit(1)


@main.command()
@click.option(
    "--scope",
    default="user",
    type=click.Choice(["user", "project"]),
    help="Installation scope: user (~/.claude/) or project (./.claude/)",
)
@click.option("--verbose", is_flag=True, help="Show detailed results")
@click.option(
    "--check",
    type=click.Choice(["drift", "cross-refs", "usage", "all"]),
    default="all",
    help="Which check to run (default: all)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "markdown"]),
    default="text",
    help="Output format (default: text). markdown writes a committed report.",
)
@click.option(
    "--out",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Output path for --format markdown (default: docs/reports/AUDIT.md)",
)
def audit(scope: str, verbose: bool, check: str, output_format: str, out: Path | None):
    """
    Run content integrity audit.

    Combines drift detection, cross-reference validation, and content usage
    checks into a single report.

    Examples:
        superclaude audit
        superclaude audit --check drift --verbose
        superclaude audit --format markdown --out docs/reports/AUDIT.md
    """
    from .audit import run_audit
    from .install_commands import get_base_path

    base_path = get_base_path(scope)

    # Markdown format always needs per-file detail
    effective_verbose = verbose or output_format == "markdown"
    result = run_audit(base_path, verbose=effective_verbose, check=check)

    if output_format == "markdown":
        report_path = out or Path("docs/reports/AUDIT.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(_format_audit_markdown(result, scope, check), encoding="utf-8")
        click.echo(f"📝 Audit report written to {report_path}")
        if not result["clean"]:
            sys.exit(1)
        return

    click.echo(f"🔍 SuperClaude Audit (scope: {scope}, check: {check})\n")

    # Drift results
    if "drift" in result:
        drift = result["drift"]
        icon = "✅" if drift["clean"] else "⚠️"
        click.echo(f"{icon} Drift: {drift['total_ok']} OK, "
                    f"{drift['total_drifted']} drifted, "
                    f"{drift['total_missing']} missing, "
                    f"{drift['total_extra']} extra")
        if verbose and not drift["clean"]:
            for component, stats in drift["components"].items():
                if stats["drifted"] + stats["missing"] + stats["extra"] == 0:
                    continue
                click.echo(f"   {component}:")
                for filename, status in stats.get("files", {}).items():
                    if status != "OK":
                        click.echo(f"      - [{status}] {filename}")

    # Cross-reference results
    if "cross_refs" in result:
        xref = result["cross_refs"]
        icon = "✅" if xref["clean"] else "⚠️"
        click.echo(f"{icon} Cross-refs: {xref['total_issues']} issues")
        if verbose and not xref["clean"]:
            for category, items in xref["issues"].items():
                if items:
                    click.echo(f"   {category}:")
                    for item in items:
                        click.echo(f"      - {item}")

    # Usage results
    if "usage" in result:
        usage = result["usage"]
        icon = "✅" if usage["clean"] else "⚠️"
        click.echo(f"{icon} Usage: {usage['total_issues']} issues")
        if verbose and not usage["clean"]:
            for issue in usage["issues"]:
                click.echo(f"      - {issue}")

    # Overall
    click.echo()
    if result["clean"]:
        click.echo("✅ All checks passed")
    else:
        click.echo("⚠️  Issues found — see above for details")
        sys.exit(1)


def _format_audit_markdown(result: dict, scope: str, check: str) -> str:
    """Render audit result as a committable markdown health report."""
    from datetime import datetime, timezone

    lines = [
        "# SuperClaude Audit Report",
        "",
        f"- **Generated:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- **Scope:** `{scope}`",
        f"- **Checks:** `{check}`",
        f"- **Status:** {'✅ Clean' if result['clean'] else '⚠️ Issues found'}",
        "",
    ]

    if "drift" in result:
        drift = result["drift"]
        lines += [
            "## Drift",
            "",
            f"- OK: {drift['total_ok']}",
            f"- Drifted: {drift['total_drifted']}",
            f"- Missing: {drift['total_missing']}",
            f"- Extra: {drift['total_extra']}",
            "",
        ]
        if not drift["clean"]:
            for component, stats in drift["components"].items():
                non_ok = [(f, s) for f, s in stats.get("files", {}).items() if s != "OK"]
                if not non_ok:
                    continue
                lines.append(f"### {component}")
                lines.append("")
                for filename, status in non_ok:
                    lines.append(f"- `{status}` — `{filename}`")
                lines.append("")

    if "cross_refs" in result:
        xref = result["cross_refs"]
        lines += [f"## Cross-references ({xref['total_issues']} issues)", ""]
        if not xref["clean"]:
            for category, items in xref["issues"].items():
                if items:
                    lines.append(f"### {category}")
                    lines.append("")
                    for item in items:
                        lines.append(f"- {item}")
                    lines.append("")

    if "usage" in result:
        usage = result["usage"]
        lines += [f"## Usage ({usage['total_issues']} issues)", ""]
        if not usage["clean"]:
            for issue in usage["issues"]:
                lines.append(f"- {issue}")
            lines.append("")

    return "\n".join(lines) + "\n"


@main.command()
def version():
    """Show SuperClaude version"""
    click.echo(f"SuperClaude version {__version__}")


if __name__ == "__main__":
    main()
