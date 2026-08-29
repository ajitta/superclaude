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


def _in_git_repo(start: Path) -> bool:
    """Return True if start (or any parent) contains a .git directory/file."""
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return True
    return False


def _stdin_can_answer() -> bool:
    """Whether an interactive prompt could actually be answered.

    Not `sys.stdin.isatty()` alone: on Windows NUL is a character device, so
    isatty() reports a terminal even at DEVNULL. A terminal is taken at its
    word; anything else has to have bytes waiting, which is what separates
    `echo 1 | superclaude install` from `superclaude install < /dev/null`.
    """
    stream = sys.stdin
    if stream is None or getattr(stream, "closed", False):
        return False
    try:
        if stream.isatty():
            return True
    except (OSError, ValueError):
        return False
    buffer = getattr(stream, "buffer", None)
    if buffer is None:
        return False
    try:
        if hasattr(buffer, "peek"):
            return bool(buffer.peek(1))
        # An in-memory stream (a test runner's, typically) has no peek but can
        # be rewound, so look one byte ahead and put it back.
        if buffer.seekable():
            here = buffer.tell()
            waiting = buffer.read(1)
            buffer.seek(here)
            return bool(waiting)
    except (OSError, ValueError):
        return False
    return False


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
    type=click.Choice(["user", "project", "local"]),
    help="Installation scope: user (~/.claude/), project (./.claude/ team-shared), or local (./.claude/ personal, gitignored)",
)
@click.option(
    "--interactive",
    "-i",
    "interactive",
    is_flag=True,
    help="Step-by-step wizard: scope, optional git init, force, preview, confirm",
)
def install(
    force: bool, list_only: bool, list_all: bool, scope: str, interactive: bool
):
    """
    Install all SuperClaude components to Claude Code

    Installs:
    - Slash commands to commands/sc/
    - Agent definitions to agents/
    - Skills to skills/
    - Behavioral modes to superclaude/modes/
    - Framework files to superclaude/ (core, mcp)

    Scopes:
    - user (default): Install to ~/.claude/ (global, personal)
    - project: Install to ./.claude/ (team-shared, committed to repo)
    - local: Install to ./.claude/ (personal in team repo; auto-gitignored, hooks to settings.local.json, CLAUDE.local.md at project root)

    Examples:
        superclaude install
        superclaude install --force
        superclaude install --scope project
        superclaude install --scope local
        superclaude install --list
    """
    from .install_commands import (
        get_base_path,
        install_all,
        list_all_components,
        list_available_commands,
        list_installed_commands,
    )

    # Decide whether to run the interactive wizard.
    # Trigger paths:
    #  - Explicit -i/--interactive
    #  - No flags at all (every option still at its DEFAULT source)
    ctx = click.get_current_context()

    def _all_defaults() -> bool:
        for opt in ("force", "list_only", "list_all", "scope", "interactive"):
            src = ctx.get_parameter_source(opt)
            if src is None or src.name != "DEFAULT":
                return False
        return True

    if interactive or _all_defaults():
        from . import install_interactive

        # Whether anything can answer the wizard is decided *before* it opens.
        # It used to be inferred afterwards from click.Abort — but Click raises
        # Abort for Ctrl-C as well as for EOF, so cancelling installed to user
        # scope, and a user who had already chosen local or project scope got
        # user scope instead of a cancel. With the question settled up front, an
        # Abort inside the wizard can only mean a person aborted it, and -i
        # stops needing to be a special case.
        if not interactive and not _stdin_can_answer():
            click.echo()
            click.echo(
                "💡 No input available for the wizard — continuing with defaults "
                "(scope: user). Pass --scope/--force to choose explicitly."
            )
            click.echo()
        else:
            sys.exit(install_interactive.run_interactive_install())

    # Get base path based on scope
    base_path = get_base_path(scope)

    # List all components mode
    if list_all:
        components = list_all_components(base_path=base_path, scope=scope)
        click.echo(f"📋 SuperClaude Components (scope: {scope}):\n")
        for name, info in components.items():
            status = f"{info['installed']}/{info['available']}"
            icon = (
                "✅"
                if info["installed"] == info["available"] and info["available"] > 0
                else "⬜"
            )
            click.echo(f"   {icon} {info['description']:40} [{status}]")
            click.echo(f"      └─ {info['target_path']}")
            # Counts alone cannot say whether the registered hooks are the
            # shipped ones, so name the mismatch when there is one.
            drift = ", ".join(
                f"{info[key]} {key}"
                for key in ("missing", "obsolete", "duplicate")
                if info.get(key)
            )
            if drift:
                click.echo(f"      └─ {drift}")
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

    # Hint: suggest --scope local when defaulting to user inside a git repo
    scope_source = click.get_current_context().get_parameter_source("scope")
    scope_was_default = scope_source is not None and scope_source.name == "DEFAULT"
    if scope_was_default and scope == "user" and _in_git_repo(Path.cwd()):
        click.echo(
            "💡 Installing at the default user scope → ~/.claude, which applies "
            "in every repository. Since this is a git repo, --scope local is the "
            "alternative: a personal install inside it, auto-gitignored, with its "
            "own settings."
        )
        click.echo()

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
    type=click.Choice(["user", "project", "local"]),
    help="Uninstall scope: user (~/.claude/), project (./.claude/), or local (./.claude/ personal)",
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
@click.option(
    "--remove-mcp",
    is_flag=True,
    help="Also remove SuperClaude-registered MCP servers (default: keep, since MCP is shared across tools)",
)
def uninstall(
    scope: str, dry_run: bool, yes: bool, keep_settings: bool, remove_mcp: bool
):
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

    Preserved by default (opt-in removal):
    - MCP servers registered by SuperClaude — shared with other CC tools/agents.
      Use --remove-mcp to clean them at the given scope (preserves user-added servers).

    Scopes:
    - user (default): Uninstall from ~/.claude/
    - project: Uninstall from ./.claude/ (team-shared)
    - local: Uninstall from ./.claude/ + remove CLAUDE.local.md + clean .gitignore block

    Examples:
        superclaude uninstall --dry-run        # Preview what will be removed
        superclaude uninstall --yes            # Skip confirmation
        superclaude uninstall --scope project  # Uninstall from current project
        superclaude uninstall --scope local    # Uninstall personal install (cleans .gitignore)
        superclaude uninstall --keep-settings  # Keep settings.json hooks
        superclaude uninstall --remove-mcp     # Also remove SuperClaude-registered MCP servers
    """
    keep_mcp = not remove_mcp
    from .install_commands import get_base_path, uninstall_all

    base_path = get_base_path(scope)

    # Dry-run mode: show what would be removed
    if dry_run:
        click.echo(f"🔍 Dry-run mode: Showing what would be removed (scope: {scope})\n")
        success, message = uninstall_all(
            base_path=base_path,
            scope=scope,
            dry_run=True,
            keep_settings=keep_settings,
            keep_mcp=keep_mcp,
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
        keep_settings=keep_settings,
        keep_mcp=keep_mcp,
    )

    click.echo(message)

    if not success:
        sys.exit(1)


@main.command()
@click.option("--servers", "-s", multiple=True, help="Specific MCP servers to install")
@click.option("--list", "list_only", is_flag=True, help="List available MCP servers")
@click.option(
    "--status",
    "show_status",
    is_flag=True,
    help="Show MCP server status with fallbacks",
)
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
        superclaude mcp --servers tavily --servers playwright
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
    type=click.Choice(["user", "project", "local"]),
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
    type=click.Choice(["user", "project", "local"]),
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
    type=click.Choice(["user", "project", "local"]),
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

            click.echo(
                f"   {agent_file.stem:30} ~{frontmatter_tokens:4} tokens (full: ~{full_tokens})"
            )

        click.echo()
        click.echo(
            f"   Total: ~{total_frontmatter} frontmatter, ~{total_full} full load"
        )
        click.echo(f"   Agents: {len(agent_files)}")
        return

    # Info mode - show details for specific agent
    if agent_name:
        # Find agent file
        agent_file = None
        for f in agent_files:
            if f.stem == agent_name or f.stem.replace("-", "_") == agent_name.replace(
                "-", "_"
            ):
                agent_file = f
                break

        if not agent_file:
            click.echo(f"❌ Agent '{agent_name}' not found")
            click.echo(
                f"   Available agents: {', '.join(f.stem for f in agent_files[:5])}..."
            )
            sys.exit(1)

        content = agent_file.read_text(encoding="utf-8")

        # Parse frontmatter
        fm = parse_frontmatter(content)

        click.echo(f"📋 Agent: {agent_file.stem}\n")
        click.echo(f"   Name: {fm.get('name', agent_file.stem)}")
        click.echo(f"   Description: {fm.get('description', 'N/A')}")
        if fm.get("context"):
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
    type=click.Choice(["user", "project", "local"]),
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
            if d.name == skill_name or d.name.replace("-", "_") == skill_name.replace(
                "-", "_"
            ):
                skill_dir = d
                manifest = m
                break

        if not skill_dir:
            click.echo(f"❌ Skill '{skill_name}' not found")
            click.echo(
                f"   Available skills: {', '.join(d.name for d, _ in skill_dirs[:5])}..."
            )
            sys.exit(1)

        content = manifest.read_text(encoding="utf-8")

        # Parse frontmatter
        fm = parse_frontmatter(content)

        click.echo(f"📋 Skill: {skill_dir.name}\n")
        click.echo(f"   Name: {fm.get('name', skill_dir.name)}")
        click.echo(f"   Description: {fm.get('description', 'N/A')}")
        if fm.get("context"):
            click.echo(f"   Context: {fm.get('context')}")
        if fm.get("agent"):
            click.echo(f"   Agent: {fm.get('agent')}")
        if fm.get("hooks"):
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
    type=click.Choice(["user", "project", "local"]),
    help="Installation scope: user (~/.claude/) or project (./.claude/)",
)
@click.option("--verbose", is_flag=True, help="Show per-file details")
def verify_drift_cmd(scope: str, verbose: bool):
    """
    Check for installation drift between source and installed files.

    Compares installed content against the package source to detect:
    - MISSING: source file not installed
    - DRIFTED: installed file differs from source
    - EXTRA: installed file has no source counterpart

    Coverage: component .md files (incl. core/rules/), skill SKILL.md
    manifests, and CLAUDE_SC.md. Not checked: templates/, installed
    scripts/, and the merged hooks.json.

    Examples:
        superclaude verify-drift
        superclaude verify-drift --verbose
        superclaude verify-drift --scope project
    """
    from .install_commands import get_base_path
    from .verify_drift import OK, verify_drift

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
    type=click.Choice(["user", "project", "local"]),
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
    checks into a single report. Drift coverage matches verify-drift
    (templates/, installed scripts/, and hooks.json are not checked).

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
        report_path.write_text(
            _format_audit_markdown(result, scope, check), encoding="utf-8"
        )
        click.echo(f"📝 Audit report written to {report_path}")
        if not result["clean"]:
            sys.exit(1)
        return

    click.echo(f"🔍 SuperClaude Audit (scope: {scope}, check: {check})\n")

    # Drift results
    if "drift" in result:
        drift = result["drift"]
        icon = "✅" if drift["clean"] else "⚠️"
        click.echo(
            f"{icon} Drift: {drift['total_ok']} OK, "
            f"{drift['total_drifted']} drifted, "
            f"{drift['total_missing']} missing, "
            f"{drift['total_extra']} extra"
        )
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
                non_ok = [
                    (f, s) for f, s in stats.get("files", {}).items() if s != "OK"
                ]
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


@main.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    add_help_option=False,
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def insight(args):
    """
    Capture and review session insights (/sc:insight backend).

    Forwards to insight_writer's own parser, so `superclaude insight --help`
    lists every subcommand. This entry point exists because the script imports
    superclaude.utils, which only the installing interpreter can resolve — a
    bare `python3 ~/.claude/superclaude/scripts/insight_writer.py` raises
    ModuleNotFoundError. The console script always carries its own environment.

    Examples:
        superclaude insight review
        superclaude insight list --limit 20
        superclaude insight promote --index 0 --type discovery --tags harvest
        superclaude insight append --json '{"type":"feedback","insight":"..."}'
    """
    from superclaude.scripts.insight_writer import main as insight_main

    sys.exit(insight_main(list(args), prog="superclaude insight"))


@main.command(
    name="auto-improve",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    add_help_option=False,
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def auto_improve_cmd(args):
    """
    Run the autonomous code-improvement loop (/sc:auto-improve backend).

    Forwards to the worker's own parser, so `superclaude auto-improve --help`
    lists every flag. This entry point exists because the worker imports
    superclaude.scripts.auto_improve.*, which only the installing interpreter
    can resolve — a bare `python -m superclaude.scripts.auto_improve` outside a
    checkout raises ModuleNotFoundError. The console script always carries its
    own environment.

    Examples:
        superclaude auto-improve --project . --eval-cmd 'pytest --json-report' --metric summary.passed --budget 8h
        superclaude auto-improve --project . --status
        superclaude auto-improve --project . --eval-cmd 'python eval.py' --metric pass_rate --dry-run
    """
    from superclaude.scripts.auto_improve.cli import main as auto_improve_main

    sys.exit(auto_improve_main(list(args), prog="superclaude auto-improve"))


@main.command(
    name="parallel-ab",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    add_help_option=False,
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def parallel_ab_cmd(args):
    """
    Run N prompt/skill variants in parallel and aggregate the results.

    Forwards to the harness's own parser, so `superclaude parallel-ab --help`
    lists every flag. This entry point exists because the harness imports
    superclaude.scripts.parallel_ab.*, which only the installing interpreter
    can resolve — a bare `python -m superclaude.scripts.parallel_ab` outside a
    checkout raises ModuleNotFoundError. The console script always carries its
    own environment.

    Examples:
        superclaude parallel-ab docs/experiments/brainstorm-ab/variants.yaml
        superclaude parallel-ab variants.yaml --out-dir /tmp/ab-run
    """
    from superclaude.scripts.parallel_ab.cli import main as parallel_ab_main

    sys.exit(parallel_ab_main(list(args), prog="superclaude parallel-ab"))


# --- `superclaude context` -------------------------------------------------
#
# context_loader.py and context_reset.py both import superclaude.*, so neither
# is runnable as a bare `python3 ~/.claude/superclaude/scripts/X.py` (see
# .claude/rules/gotchas/hooks.md `script-needs-console-entry`). `reset` gives
# context_reset.py its human path; `explain` gives context_loader.py a dry run.
#
# `explain` runs the loader as a subprocess, exactly the way
# tests/unit/test_context_loader.py's run_loader does, and never imports it for
# execution. The loader is the UserPromptSubmit hot path (hooks.json, 5s
# timeout) with no in-process test coverage, so the answer is taken from the
# real thing rather than from a second copy of its matching logic.

# Markers context_loader prints. Parsed rather than re-derived so the file list,
# the tiers and the Tier 2 token counts all come from the loader itself.
_CTX_HINT_RE = re.compile(r'^<sc-context-hint src="([^"]+)">(.*)</sc-context-hint>$')
_CTX_INSTRUCTION_RE = re.compile(r'^<sc-context src="([^"]+)">$')
_CTX_INJECT_RE = re.compile(r'^<context-inject file="([^"]+)" tokens="~(\d+)">$')
_CTX_LOAD_RE = re.compile(r'^<context-load file="(.+)"/>$')
_CTX_DIRECTIVE_RE = re.compile(r'^<sc-directive flag="([^"]+)">')
_CTX_TOTAL_RE = re.compile(r"^<!-- Context loaded: \d+ files \(~(\d+) tokens\) -->$")
_CTX_SKIPPED_RE = re.compile(r"^<!--.*Budget exceeded: skipped (.+) -->$")
_CTX_NOTICE_RE = re.compile(r"^<!--\s*(.*?)\s*-->$")


def _context_content_root() -> tuple[Path, str | None]:
    """Content root a dry run should read, plus a note when the anchors disagree.

    ``SUPERCLAUDE_PATH`` wins because that is the loader's own first priority.
    Otherwise a scoped install is looked for under ``$CLAUDE_PROJECT_DIR`` —
    the anchor ``claude_base()`` resolves from — with the CWD as the fallback
    when that variable is unset, then user scope when neither directory holds a
    ``.claude/superclaude``.

    Reading the variable is not the same as calling ``project_root()``, which
    .claude/rules/gotchas/hooks.md `cli-vs-hook-cwd` reserves for hook code, and
    the two cases pull in opposite directions: ``install_paths`` decides where
    the USER wants content written and so follows the shell, while this reports
    what the HOOK would read and so has to follow the hook's anchor. Under the
    CWD rule alone, an ``explain`` run from a subdirectory of a project-scope
    install silently answers user scope. When the anchors disagree the caller
    prints both rather than picking one in silence.

    Returns:
        (content root, note naming the disagreement, or None when they agree)
    """
    import os

    override = os.environ.get("SUPERCLAUDE_PATH")
    if override:
        return Path(override), None

    def scoped(base: Path) -> Path:
        local = base / ".claude" / "superclaude"
        return local if local.is_dir() else Path.home() / ".claude" / "superclaude"

    anchor = os.environ.get("CLAUDE_PROJECT_DIR")
    if not anchor:
        return scoped(Path.cwd()), None

    from_anchor = scoped(Path(anchor))
    from_cwd = scoped(Path.cwd())
    if from_anchor == from_cwd:
        return from_anchor, None
    return from_anchor, (
        f"$CLAUDE_PROJECT_DIR={anchor} decides this, as it does for the hook; "
        f"this directory alone would have answered {from_cwd}"
    )


def _packaged_loader() -> Path:
    """The context_loader.py copy this CLI runs: the one shipped in this package.

    The UserPromptSubmit hook runs the INSTALLED copy instead
    (hooks.json's ``{{SCRIPTS_PATH}}/context_loader.py``, which
    ``install_components._resolve_template_paths`` resolves to
    ``<content root>/scripts``), so the two can drift apart.
    """
    return Path(__file__).resolve().parent.parent / "scripts" / "context_loader.py"


def _loader_copies_differ(installed: Path, packaged: Path) -> bool:
    """True when the hook's loader is not byte-identical to the one just run.

    A correctly synced install still has two distinct PATHS, so naming them
    without a verdict would not tell a user chasing a phantom whether the copy
    the hook runs is the copy that was explained. Unreadable or absent counts as
    no difference: this is one disclosure line, not a gate —
    ``superclaude verify-drift`` is the real check.
    """
    try:
        return installed.read_bytes() != packaged.read_bytes()
    except OSError:
        return False


def _run_loader_isolated(prompt: str, content_root: Path) -> str:
    """Run context_loader.py on ``prompt`` without touching real hook state.

    Every write the loader makes lands under ``hook_state_dir()``, which resolves
    from ``$CLAUDE_PROJECT_DIR``. Pointing the child at a throwaway directory
    with a ``.claude/superclaude`` marker therefore redirects all of it — the
    session dedup cache AND the ``mcp_fallbacks.json`` ledger, which
    hooks/mcp_fallback.py writes on a server's first reference in a session —
    and the directory is deleted when this returns. ``SUPERCLAUDE_PATH`` is
    passed explicitly so the redirect does not also move the content being
    explained. The session id is synthetic and derived from the prompt, so it
    can never collide with a live session's cache.

    Only the child's environment is built here; ``os.environ`` is not modified.
    """
    import hashlib
    import json
    import os
    import subprocess
    import tempfile

    loader = _packaged_loader()
    if not loader.is_file():
        raise click.ClickException(f"context_loader.py not found at {loader}")

    session_id = "sc-explain-" + hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]

    with tempfile.TemporaryDirectory(prefix="sc-context-explain-") as sandbox:
        (Path(sandbox) / ".claude" / "superclaude").mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = sandbox
        env["SUPERCLAUDE_PATH"] = str(content_root)
        env["CLAUDE_SHOW_SKILLS"] = "0"  # once-per-session banner, not prompt-triggered
        try:
            result = subprocess.run(
                [sys.executable, str(loader)],
                input=json.dumps({"prompt": prompt, "session_id": session_id}),
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            raise click.ClickException(
                "context_loader.py did not finish in 60s"
            ) from None

    if result.returncode != 0:
        raise click.ClickException(
            f"context_loader.py exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout


def _parse_loader_output(stdout: str, content_root: Path) -> dict:
    """Turn the loader's stdout into the pieces the report prints."""
    from superclaude.scripts.token_estimator import estimate_tokens

    contexts: list[dict] = []
    directives: list[str] = []
    notices: list[str] = []
    dropped: list[str] = []
    total: int | None = None

    lines = stdout.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        hint = _CTX_HINT_RE.match(line)
        if hint:
            contexts.append(
                {
                    "file": hint.group(1),
                    "tier": 0,
                    "tokens": estimate_tokens(hint.group(2)),
                }
            )
            i += 1
            continue

        instruction = _CTX_INSTRUCTION_RE.match(line)
        if instruction:
            body: list[str] = []
            i += 1
            while i < len(lines) and lines[i] != "</sc-context>":
                body.append(lines[i])
                i += 1
            i += 1
            contexts.append(
                {
                    "file": instruction.group(1),
                    "tier": 1,
                    "tokens": estimate_tokens("\n".join(body)),
                }
            )
            continue

        inject = _CTX_INJECT_RE.match(line)
        if inject:
            i += 1
            while i < len(lines) and lines[i] != "</context-inject>":
                i += 1
            i += 1
            # The loader declares the count it charged against the budget; a
            # recount here could disagree with the number that did the dropping.
            contexts.append(
                {
                    "file": inject.group(1),
                    "tier": 2,
                    "tokens": int(inject.group(2)),
                }
            )
            continue

        load = _CTX_LOAD_RE.match(line)  # CLAUDE_CONTEXT_INJECT=0 (directive mode)
        if load:
            named = load.group(1)
            rel = named[len(str(content_root)) :].lstrip("/\\") or named
            contexts.append({"file": rel, "tier": None, "tokens": None})
            i += 1
            continue

        directive = _CTX_DIRECTIVE_RE.match(line)
        if directive:
            directives.append(directive.group(1))
            i += 1
            continue

        summary = _CTX_TOTAL_RE.match(line)
        if summary:
            total = int(summary.group(1))
            i += 1
            continue

        skipped = _CTX_SKIPPED_RE.match(line)
        if skipped:
            dropped = [name.strip() for name in skipped.group(1).split(",")]
            i += 1
            continue

        notice = _CTX_NOTICE_RE.match(line)
        if notice and notice.group(1):
            notices.append(notice.group(1))
            i += 1
            continue

        i += 1

    if total is None:
        total = sum(c["tokens"] or 0 for c in contexts)
    return {
        "contexts": contexts,
        "directives": directives,
        "notices": notices,
        "dropped": dropped,
        "total": total,
    }


def _attribute_triggers(prompt: str) -> dict[str, str]:
    """Map context file -> the trigger that would have fired for it.

    The loader stays the authority on WHICH files inject; this only explains
    WHY, by reading context_loader's own TRIGGER_MAP and COMPOSITE_FLAGS. The
    lowercased raw prompt and the composites-before-patterns order mirror
    ``check_triggers``; a file the loader emitted with no attribution is
    reported as such rather than guessed at.
    """
    from superclaude.scripts.context_loader import COMPOSITE_FLAGS, TRIGGER_MAP

    lowered = prompt.lower()
    attribution: dict[str, str] = {}
    for flag, entries in COMPOSITE_FLAGS.items():
        if flag in lowered:
            for context_file, _ in entries:
                attribution.setdefault(context_file, f"composite flag {flag}")
    for pattern, context_file, _ in TRIGGER_MAP:
        found = pattern.search(lowered)
        if found:
            attribution.setdefault(context_file, f'matched "{found.group(0)}"')
    return attribution


@main.group(name="context")
def context_group():
    """Inspect and reset context_loader state.

    `explain` is a dry run: it shows which context files a prompt would inject
    and what they cost. `reset` clears the dedup cache so contexts re-inject.
    """


@context_group.command(
    name="explain", context_settings={"ignore_unknown_options": True}
)
@click.argument("prompt", nargs=-1, type=click.UNPROCESSED)
def context_explain(prompt):
    """
    Dry run: show which context files PROMPT would inject, and why.

    Runs THIS PACKAGE's copy of context_loader.py as a subprocess against a
    throwaway state directory and a synthetic session id, so the report cannot
    consume the dedup entries or the one-per-session MCP hints of a live
    session. Nothing under the real .superclaude_hooks/ is read or written.

    The UserPromptSubmit hook runs the INSTALLED copy, so the copy that ran is
    named in the output and a byte difference from the installed one is flagged:
    on a drifted install the two can answer differently.

    The run always simulates a FRESH session: a live session that already
    received one of these files would not receive it again, and the
    once-per-session installed-skills banner is suppressed rather than shown.

    Examples:
        superclaude context explain "--serena rename this symbol"
        superclaude context explain --brainstorm a new CLI
    """
    import os

    # Mirrors context_loader.MAX_TOKENS_ESTIMATE, which that module freezes at
    # import: reading the env here is what keeps the reported budget equal to
    # the one the freshly-started child actually enforced.
    budget = int(os.environ.get("CLAUDE_CONTEXT_MAX_TOKENS", "8000"))

    text = " ".join(prompt).strip()
    if not text:
        raise click.UsageError('PROMPT is required, e.g. "--serena rename this"')

    content_root, root_note = _context_content_root()
    if not content_root.is_dir():
        click.echo(f"⚠️  content root not found: {content_root}")
        click.echo(
            "   install content first (superclaude install) or set SUPERCLAUDE_PATH"
        )

    report = _parse_loader_output(
        _run_loader_isolated(text, content_root), content_root
    )
    attribution = _attribute_triggers(text)

    packaged = _packaged_loader()
    installed = content_root / "scripts" / "context_loader.py"

    click.echo(f"prompt:  {text}")
    click.echo(f"content: {content_root}")
    if root_note:
        click.echo(f"         {root_note}")
    click.echo(f"budget:  {budget} tokens")
    click.echo(f"loader:  {packaged} (this package's copy)")
    if installed != packaged and _loader_copies_differ(installed, packaged):
        click.echo(f"         ⚠️  the hook runs {installed}, whose bytes differ")
        click.echo("         re-sync it (superclaude install) or see verify-drift")
    click.echo("session: dry run — fresh session simulated, no cache read or written")
    click.echo(
        "skills:  installed-skills banner suppressed "
        "(once-per-session, not prompt-triggered)"
    )
    click.echo("")

    contexts = report["contexts"]
    if not contexts:
        click.echo("would inject no context files.")
    else:
        click.echo(
            f"would inject {len(contexts)} context file(s) "
            f"(~{report['total']} of {budget} tokens):"
        )
        for entry in contexts:
            tier = "tier ?" if entry["tier"] is None else f"tier {entry['tier']}"
            cost = "     " if entry["tokens"] is None else f"~{entry['tokens']:<5}"
            why = attribution.get(
                entry["file"], "no matching trigger (composite or dedup)"
            )
            click.echo(f"  {tier}  {cost} {entry['file']}  <- {why}")

    if report["dropped"]:
        click.echo("")
        click.echo("dropped by the token budget:")
        for name in report["dropped"]:
            click.echo(f"  {name}")

    if report["directives"]:
        click.echo("")
        click.echo("execution directives (behavioral, no file injection):")
        for flag in report["directives"]:
            click.echo(f"  {flag}")

    if report["notices"]:
        click.echo("")
        click.echo("loader notices:")
        for note in report["notices"]:
            click.echo(f"  {note}")


@context_group.command(name="reset")
@click.option(
    "--session",
    "session_id",
    default=None,
    metavar="ID",
    help="Session to reset. Defaults to $CLAUDE_CODE_SESSION_ID, then to the "
    "project-only cache name.",
)
def context_reset_cmd(session_id):
    """
    Delete this project's context dedup cache so contexts re-inject.

    The same reset the SessionStart hook runs on /clear and /compact, exposed
    for manual use — context_reset.py imports superclaude.utils, so a bare
    `python3 ~/.claude/superclaude/scripts/context_reset.py` cannot run it.

    Also prunes hook state older than 7 days and the MCP fallback ledger, so
    MCP fallback hints re-arm. Everything removed is a rebuildable cache.

    The target is resolved as: --session, then $CLAUDE_CODE_SESSION_ID, then the
    project-only cache name. That variable is not set in every environment, so
    the resolved path and the removed count are always printed.

    Examples:
        superclaude context reset
        superclaude context reset --session abc123
    """
    import os

    from superclaude.scripts.context_reset import get_cache_file, reset_context_cache

    if session_id:
        source = "--session"
    else:
        session_id = os.environ.get("CLAUDE_CODE_SESSION_ID") or None
        source = "$CLAUDE_CODE_SESSION_ID" if session_id else "project-only fallback"

    # Mirrors reset_context_cache's own target list (context_reset.py): the
    # session file, plus the project-only name a pre-session-keying run left.
    # De-duplicated because session_slug() strips an id to [A-Za-z0-9_-], so one
    # that sanitizes to empty (`--session '///'`) names the same file twice —
    # printed twice, and counted twice in "reset N cache file(s)".
    candidates = [get_cache_file(session_id)]
    if session_id:
        candidates.append(get_cache_file())
    targets = list(dict.fromkeys(candidates))

    click.echo(f"session: {session_id or '(none)'} — from {source}")
    for target in targets:
        click.echo(f"cache:   {target}")

    existed = [t for t in targets if t.exists()]
    reset_context_cache(session_id)
    removed = [t for t in existed if not t.exists()]

    for target in removed:
        click.echo(f"removed: {target}")
    if removed:
        click.echo(f"reset {len(removed)} cache file(s)")
    else:
        looked = ", ".join(str(t) for t in targets)
        click.echo(f"nothing to reset (looked at {looked})")


@main.command()
def version():
    """Show SuperClaude version"""
    click.echo(f"SuperClaude version {__version__}")


if __name__ == "__main__":
    main()
