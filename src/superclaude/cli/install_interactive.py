"""
Interactive (step-by-step) wizard for `superclaude install`.

Triggered when the user passes `-i/--interactive` or runs `superclaude install`
with no flags at all. Walks through scope selection, optional `git init`,
force-reinstall toggle, install preview, and final confirmation, then
delegates to `install_all()`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Tuple

import click

from .install_inventory import list_all_components
from .install_paths import get_base_path

SCOPES = [
    ("user", "~/.claude/ — global, personal (default)"),
    ("project", "./.claude/ — team-shared, committed to repo"),
    ("local", "./.claude/ — personal in team repo, auto-gitignored"),
]


def _has_git(path: Path) -> bool:
    for p in [path, *path.parents]:
        if (p / ".git").exists():
            return True
    return False


def _prompt_scope() -> str:
    click.echo("Step 1/5: Installation scope")
    for i, (name, desc) in enumerate(SCOPES, start=1):
        click.echo(f"  {i}) {name:7} — {desc}")
    choice = click.prompt(
        "Select scope",
        type=click.IntRange(1, len(SCOPES)),
        default=1,
        show_default=True,
    )
    return SCOPES[choice - 1][0]


def _maybe_git_init(scope: str, project_root: Path) -> Tuple[bool, str]:
    """Offer `git init` when scope needs git but none is present.

    Returns (proceed, note) where proceed=False means user aborted.
    """
    if scope not in ("project", "local"):
        return True, ""
    if _has_git(project_root):
        return True, ""

    click.echo()
    click.echo(f"Step 2/5: Git check — no .git found at {project_root}")
    if scope == "local":
        click.echo(
            "  Local scope writes a .gitignore block to keep personal files "
            "out of the repo. Without git, the block is written but untracked."
        )
    else:
        click.echo(
            "  Project scope is intended for team-shared .claude/ checked "
            "into git. Without git, files install but won't be versioned."
        )

    if click.confirm("  Initialize a git repo here?", default=False):
        try:
            subprocess.run(
                ["git", "init"],
                cwd=str(project_root),
                check=True,
                capture_output=True,
                text=True,
            )
            click.echo(f"  ✅ git init complete at {project_root}")
            return True, "git initialized"
        except FileNotFoundError:
            click.echo("  ⚠️  git not found in PATH — skipping init.")
            return True, "git not available"
        except subprocess.CalledProcessError as e:
            click.echo(f"  ⚠️  git init failed: {e.stderr.strip() or e}")
            return True, "git init failed"
    else:
        click.echo("  Skipped git init. Continuing.")
        return True, "git init skipped"


def _show_preview(base_path: Path, scope: str, force: bool) -> None:
    click.echo()
    click.echo("Step 4/5: Preview")
    click.echo(f"  Scope:   {scope}")
    click.echo(f"  Target:  {base_path}")
    click.echo(f"  Force:   {'yes' if force else 'no'}")
    click.echo()
    components = list_all_components(base_path=base_path)
    click.echo("  Components:")
    for _name, info in components.items():
        avail = info.get("available", 0)
        installed = info.get("installed", 0)
        new = max(avail - installed, 0)
        action = "reinstall all" if force else f"{new} new, {installed} kept"
        click.echo(f"    - {info['description']:40} [{action}]")


def run_interactive_install() -> int:
    """Drive the interactive install. Returns process exit code."""
    click.echo("🪄  SuperClaude interactive installer")
    click.echo()

    scope = _prompt_scope()
    base_path = get_base_path(scope)
    project_root = base_path.parent if scope in ("project", "local") else Path.cwd()

    proceed, _note = _maybe_git_init(scope, project_root)
    if not proceed:
        click.echo("Aborted.")
        return 1

    click.echo()
    click.echo("Step 3/5: Force reinstall existing files?")
    force = click.confirm("  Overwrite already-installed files?", default=False)

    _show_preview(base_path, scope, force)

    click.echo()
    if not click.confirm("Step 5/5: Proceed with install?", default=True):
        click.echo("Aborted.")
        return 1

    from .install_components import install_all

    click.echo()
    click.echo(f"📦 Installing SuperClaude components (scope: {scope})...")
    click.echo()
    success, message = install_all(base_path=base_path, force=force, scope=scope)
    click.echo(message)

    if success:
        click.echo()
        click.echo("💡 Next: run `superclaude mcp install` to set up MCP servers.")
        return 0
    return 1
