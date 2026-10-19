"""
superclaude Doctor Command

Health check for superclaude installation.

Every check that touches disk is scope-parameterised. Four of the six used to
read ~/.claude unconditionally, so on a local- or project-scope install two
reported a healthy install as broken and the other two passed by reading another
tool's skills and another tool's hooks — a 4/6 score in which no check had
actually looked at superclaude.
"""

import json
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, Dict, List

from superclaude.utils import (
    is_legacy_hook_command,
    is_superclaude_hook,
    settings_filename,
)

from .install_paths import (
    _get_package_root,
    config_dir_warning,
    console_script_problems,
    has_install,
    probe_console_script,
    resolve_reporting_target,
    scope_command,
)
from .install_settings import _hook_script_id, _split_entry, _unwritable_settings


def _repair_command(scope: str, base_path: Path) -> str:
    """The install invocation that repairs *this* scope, with where to run it.

    doctor resolves the install by walking up from the CWD; `superclaude
    install` writes to `Path.cwd() / ".claude"` for project and local scope
    (install_paths.get_base_path, pinned by the cli-vs-hook-cwd rule). Printing
    a bare command therefore told a user standing in a subdirectory to install a
    second, nested copy of the framework there, leaving the install doctor had
    just diagnosed untouched — and the next doctor run resolved to the stray
    copy and called it healthy.

    Args:
        scope: Scope being diagnosed
        base_path: That scope's .claude directory

    Returns:
        A command string safe to follow verbatim
    """
    return f"run {scope_command('install', scope, base_path)}"


def run_doctor(scope: str | None = None) -> Dict[str, Any]:
    """
    Run superclaude health checks

    Every check returns its own "details" list; rendering them is the caller's
    choice, which is why no verbose flag is taken here.

    Args:
        scope: Installation scope to check; detected by walking up from the
            working directory when omitted

    Returns:
        Dict with check results, plus the scope and base path they were run
        against so the caller can name what it inspected. "advisories" lists
        warnings that do not fail the run.
    """
    scope, base_path = resolve_reporting_target(scope)

    advisories: list[str] = []
    if scope == "user":
        warning = config_dir_warning()
        if warning:
            advisories.append(warning)

    hooks_check = _check_hooks_installed(base_path, scope)
    checks = [
        _check_pytest_plugin(),
        hooks_check,
        _check_console_entry(),
        _check_claude_sc_md(base_path, scope),
        _check_claude_md_import(base_path, scope),
    ]
    if scope in ("local", "project"):
        checks.append(_check_git_exclude(base_path, scope))
    if has_install(base_path):
        advisories.extend(_stale_install_advisories(base_path, scope, hooks_check))

    return {
        "checks": checks,
        "passed": all(check["passed"] for check in checks),
        "advisories": advisories,
        "scope": scope,
        "base_path": str(base_path),
    }


def _stale_install_advisories(
    base_path: Path, scope: str, hooks_check: Dict[str, Any]
) -> List[str]:
    """What an upgrade left behind, one line each (Q3 advisory tier, exit 0).

    The checks ask whether the install works; none asked whether it is this
    release, so a non-force upgrade read as healthy with 76 drifted files,
    deleted commands, registrations for scripts that are gone and agents still
    writing memory into every project. Hook identities are compared only when
    the hooks check passed: a failed check already says to install.
    """
    from .install_components import agent_memory_advisory
    from .install_inventory import _hook_registration_report
    from .verify_drift import drift_advisory

    lines = [drift_advisory(base_path, scope), agent_memory_advisory(base_path, scope)]
    if hooks_check["passed"]:
        settings_file = base_path / settings_filename(scope)
        report = _hook_registration_report(
            _get_package_root() / "hooks" / "hooks.json", settings_file
        )
        parts = [
            f"{report[key]} {key}"
            for key in ("missing", "obsolete", "duplicate")
            if report[key]
        ]
        if parts:
            lines.append(
                f"ℹ️  Hook registrations in {settings_file.name}: {', '.join(parts)} "
                "against this release's hooks: run "
                f"{scope_command('update', scope, base_path)} to re-register them."
            )
    return [line for line in lines if line]


def _check_pytest_plugin() -> Dict[str, Any]:
    """
    Check that the superclaude pytest plugin's entry point is registered

    Returns:
        Check result dict
    """
    found = any(
        ep.value.split(".")[0] == "superclaude" for ep in entry_points(group="pytest11")
    )
    return {
        "name": "pytest plugin loaded",
        "passed": found,
        "details": [
            "superclaude pytest plugin is active"
            if found
            else "superclaude plugin not found in pytest plugins"
        ],
    }


def _check_console_entry() -> Dict[str, Any]:
    """
    Check that the `superclaude` Claude Code's hook shell finds can run this release's hooks.

    Every registered hook command is `superclaude hook <name>`, so whichever
    console script PATH resolves is the package whose hooks run. The probe
    (install_paths.probe_console_script) leaves out the running interpreter's
    own bin — under `uv run` that is the project venv, which the user's shell
    sees only while activated — and asks the script it finds for `hook --help`
    and its version. This process's PATH is still a proxy for the hook shell's:
    that shell inherits the launching shell's PATH (measured 2026-09-05 on
    macOS; Windows unmeasured), and a Claude Code launched from a GUI with a
    narrower PATH can fail while this passes.

    Returns:
        Check result dict
    """
    label = "superclaude on PATH"
    probe = probe_console_script()
    problems = console_script_problems(probe)
    if problems:
        return {"name": label, "passed": False, "details": problems}
    return {
        "name": label,
        "passed": True,
        "details": [
            f"Hook commands run `superclaude hook <name>` — {probe['path']} "
            f"({probe['version'] or 'version unknown'})"
        ],
    }


def _check_hooks_installed(base_path: Path, scope: str) -> Dict[str, Any]:
    """
    Check that superclaude's hooks are registered in this scope's settings file.

    Only entries the marker check attributes to superclaude count. Asking merely
    whether an event array is non-empty passed on hooks belonging to unrelated
    plugins, certifying an install whose own hooks were absent.

    Args:
        base_path: Base installation path of the scope being checked
        scope: Installation scope, which decides the settings filename

    Returns:
        Check result dict
    """
    filename = settings_filename(scope)
    settings_file = base_path / filename
    label = f"Hooks in {filename}"

    if not settings_file.exists():
        return {
            "name": label,
            "passed": False,
            "details": [f"{settings_file} not found"],
        }

    # The reason install and uninstall would refuse the file, not a traceback:
    # a UTF-16 file raised UnicodeDecodeError here, a JSON array AttributeError.
    problem = _unwritable_settings(settings_file)
    if problem:
        return {"name": label, "passed": False, "details": [problem]}

    settings = json.loads(settings_file.read_text(encoding="utf-8"))
    hooks = settings.get("hooks", {})

    # A pre-console-entry registration runs a script copy under
    # superclaude/scripts/; with that copy gone python exits 2, the code that
    # blocks the prompt or tool call. Not stale content: a broken install.
    gone = set()
    for array in hooks.values():
        if not isinstance(array, list):
            continue
        for entry in array:
            if not isinstance(entry, dict):
                continue
            for hook in _split_entry(entry)[0]:
                if not is_legacy_hook_command(hook.get("command", "")):
                    continue
                name, _subcommand = _hook_script_id(hook)
                if not (base_path / "superclaude" / "scripts" / f"{name}.py").is_file():
                    gone.add(name)
    if gone:
        return {
            "name": label,
            "passed": False,
            "details": [
                f"Registrations run script copies that are gone ({', '.join(sorted(gone))}): "
                "each exits 2 in Claude Code, which blocks the prompt or tool call",
                f"Checked {settings_file} — {_repair_command(scope, base_path)}",
            ],
        }

    expected = ["SessionStart", "UserPromptSubmit", "PostToolUse", "PreToolUse"]
    missing = [
        event
        for event in expected
        if not any(
            is_superclaude_hook(entry)
            for entry in hooks.get(event, [])
            if isinstance(entry, dict)
        )
    ]

    if not missing:
        return {
            "name": label,
            "passed": True,
            "details": [
                f"All {len(expected)} hook types registered in {settings_file}"
            ],
        }
    return {
        "name": label,
        "passed": False,
        "details": [
            f"No superclaude hook registered for: {', '.join(missing)}",
            f"Checked {settings_file} — {_repair_command(scope, base_path)}",
        ],
    }


def _check_claude_sc_md(base_path: Path, scope: str) -> Dict[str, Any]:
    """
    Check that CLAUDE_SC.md is installed in this scope.

    Args:
        base_path: Base installation path of the scope being checked

    Returns:
        Check result dict
    """
    sc_md = base_path / "superclaude" / "CLAUDE_SC.md"
    if sc_md.exists():
        return {
            "name": "CLAUDE_SC.md",
            "passed": True,
            "details": [f"Found at {sc_md}"],
        }
    return {
        "name": "CLAUDE_SC.md",
        "passed": False,
        "details": [f"Not found at {sc_md} — {_repair_command(scope, base_path)}"],
    }


def _check_claude_md_import(base_path: Path, scope: str) -> Dict[str, Any]:
    """
    Check that the scope's CLAUDE.md carries the CLAUDE_SC.md import.

    Local scope writes the import to <project>/CLAUDE.local.md with a path that
    walks into .claude/, so the target file and the import line both differ by
    scope. install_settings owns that mapping; this defers to it rather than
    restating it.

    Args:
        base_path: Base installation path of the scope being checked
        scope: Installation scope

    Returns:
        Check result dict
    """
    from .install_settings import _claude_md_target, check_claude_md_import

    target, _import_line = _claude_md_target(base_path, scope)
    has_import, message = check_claude_md_import(base_path=base_path, scope=scope)

    return {
        "name": f"{target.name} import",
        "passed": has_import,
        "details": [message if has_import else f"{message} ({target})"],
    }


def _check_git_exclude(base_path: Path, scope: str) -> Dict[str, Any]:
    """
    Check that the project's git exclude file carries superclaude's block.

    Local scope excludes everything it installs and project scope its runtime
    state; without the block git sees those files as untracked, one `git add .`
    from being committed. Install writes the block last, so a non-UTF-8
    exclude file or an install interrupted at that step left the install
    without it, and doctor called that healthy.

    Args:
        base_path: Base installation path of the scope being checked
        scope: Installation scope ("local" or "project")

    Returns:
        Check result dict
    """
    from .install_git_exclude import (
        _resolve_git_exclude_file,
        exclude_problem,
        has_exclude_block,
    )

    label = ".git/info/exclude block"
    project_root = base_path.parent
    exclude_file = _resolve_git_exclude_file(project_root)
    if exclude_file is None:
        return {
            "name": label,
            "passed": True,
            "details": [f"Not a git repository: {project_root}"],
        }
    problem = exclude_problem(project_root)
    if problem:
        return {"name": label, "passed": False, "details": [problem]}
    if has_exclude_block(project_root):
        return {
            "name": label,
            "passed": True,
            "details": [f"superclaude block present in {exclude_file}"],
        }
    return {
        "name": label,
        "passed": False,
        "details": [
            f"No superclaude block in {exclude_file}: git sees the files this "
            f"{scope} install keeps out of the repository — "
            f"{_repair_command(scope, base_path)}"
        ],
    }
