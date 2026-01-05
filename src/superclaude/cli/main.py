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
    from .install_commands import install_all, get_base_path

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
    from .install_skill import install_skill_command
    from .install_commands import get_base_path

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


@main.command()
@click.option(
    "--task", "-t",
    help="Task name or description to check",
)
@click.option(
    "--json", "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed check results",
)
@click.option(
    "--project-root", "-p",
    type=click.Path(exists=True),
    help="Project root directory (default: current directory)",
)
def confidence(task: str, output_json: bool, verbose: bool, project_root: str):
    """
    Run pre-implementation confidence check

    Assesses readiness before starting implementation.
    Returns confidence score (0-100%) based on 5 checks:

    \b
    - No duplicate implementations (25%)
    - Architecture compliance (25%)
    - Official docs verified (20%)
    - OSS reference found (15%)
    - Root cause identified (15%)

    \b
    Thresholds:
    - ≥90%: Proceed with implementation
    - 70-89%: Continue investigation
    - <70%: STOP - gather more context

    \b
    Examples:
        superclaude confidence
        superclaude confidence --task "implement user auth"
        superclaude confidence --json
        superclaude confidence -v --project-root ./myproject
    """
    import json as json_module
    from pathlib import Path
    from superclaude.pm_agent import ConfidenceChecker

    checker = ConfidenceChecker()
    context = {
        "task_name": task or "",
        "project_root": project_root or str(Path.cwd()),
    }

    result = checker.assess(context)

    if output_json:
        output = {
            "score": result.score,
            "percentage": f"{result.score:.0%}",
            "recommendation": result.recommendation,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "message": c.message,
                    "weight": c.weight,
                }
                for c in result.checks
            ],
        }
        click.echo(json_module.dumps(output, indent=2, ensure_ascii=False))
    else:
        # Header
        click.echo("📋 Confidence Check Results\n")

        # Show each check result
        if verbose:
            for check in result.checks:
                icon = "✅" if check.passed else "❌"
                weight_pct = f"{check.weight * 100:.0f}%"
                click.echo(f"   {icon} {check.name} ({weight_pct})")
                if check.message:
                    click.echo(f"      └─ {check.message}")
            click.echo()

        # Score and recommendation
        score_pct = result.score * 100
        if score_pct >= 90:
            icon = "✅"
            color = "green"
        elif score_pct >= 70:
            icon = "⚠️"
            color = "yellow"
        else:
            icon = "❌"
            color = "red"

        click.echo(f"📊 Confidence: {click.style(f'{score_pct:.0f}%', fg=color, bold=True)}")
        click.echo(f"{icon} {result.recommendation}")

        # Exit with non-zero if confidence too low
        if score_pct < 70:
            sys.exit(1)


@main.command("self-check")
@click.option(
    "--tests-passed", "-t",
    is_flag=True,
    help="Mark tests as passed",
)
@click.option(
    "--json", "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.option(
    "--evidence", "-e",
    multiple=True,
    help="Evidence items (can be repeated)",
)
def self_check(tests_passed: bool, output_json: bool, evidence: tuple):
    """
    Run post-implementation self-check protocol

    Validates implementation with evidence-based verification.
    Prevents hallucination by requiring concrete proof.

    \b
    Checks:
    - Tests executed and passed
    - Requirements met with evidence
    - Assumptions verified
    - No speculation

    \b
    Examples:
        superclaude self-check --tests-passed
        superclaude self-check --tests-passed --evidence "pytest output" --evidence "linting passed"
        superclaude self-check --json
    """
    import json as json_module
    from superclaude.pm_agent import SelfCheckProtocol

    protocol = SelfCheckProtocol()

    implementation = {
        "tests_passed": tests_passed,
        "evidence": {item: "provided" for item in evidence} if evidence else {},
        "requirements": [],
        "requirements_met": [],
        "assumptions": [],
        "assumptions_verified": [],
    }

    passed, issues = protocol.validate(implementation)

    if output_json:
        output = {
            "passed": passed,
            "issues": issues,
            "evidence_count": len(evidence),
        }
        click.echo(json_module.dumps(output, indent=2, ensure_ascii=False))
    else:
        if passed:
            click.echo("✅ Self-check passed")
            if evidence:
                click.echo(f"   Evidence items: {len(evidence)}")
        else:
            click.echo("❌ Self-check failed")
            for issue in issues:
                click.echo(f"   - {issue}")
            sys.exit(1)


@main.command("token-budget")
@click.option(
    "--complexity", "-c",
    type=click.Choice(["simple", "medium", "complex"]),
    default="medium",
    help="Task complexity level",
)
@click.option(
    "--json", "output_json",
    is_flag=True,
    help="Output as JSON",
)
def token_budget(complexity: str, output_json: bool):
    """
    Show token budget for task complexity

    \b
    Complexity levels:
    - simple: 200 tokens (typo fix, trivial change)
    - medium: 1,000 tokens (bug fix, small feature)
    - complex: 2,500 tokens (large feature, refactoring)

    \b
    Examples:
        superclaude token-budget
        superclaude token-budget --complexity complex
        superclaude token-budget -c simple --json
    """
    import json as json_module
    from superclaude.pm_agent import TokenBudgetManager

    manager = TokenBudgetManager(complexity=complexity)

    if output_json:
        output = {
            "complexity": complexity,
            "limit": manager.limit,
            "used": manager.used,
            "remaining": manager.remaining,
        }
        click.echo(json_module.dumps(output, indent=2, ensure_ascii=False))
    else:
        click.echo(f"📊 Token Budget: {complexity.upper()}")
        click.echo(f"   Limit: {manager.limit:,} tokens")
        click.echo(f"   Used: {manager.used:,} tokens")
        click.echo(f"   Remaining: {manager.remaining:,} tokens")


@main.command()
def version():
    """Show SuperClaude version"""
    click.echo(f"SuperClaude version {__version__}")


if __name__ == "__main__":
    main()
