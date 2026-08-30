"""
SuperClaude Doctor Command

Health check for SuperClaude installation.

Every check that touches disk is scope-parameterised. Four of the six used to
read ~/.claude unconditionally, so on a local- or project-scope install two
reported a healthy install as broken and the other two passed by reading another
tool's skills and another tool's hooks — a 4/6 score in which no check had
actually looked at SuperClaude.
"""

import json
from pathlib import Path
from typing import Any, Dict

from superclaude.utils import settings_filename

from .install_paths import resolve_reporting_target


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
    if scope == "user":
        return "run 'superclaude install --scope user'"
    return f"run 'superclaude install --scope {scope}' from {base_path.parent}"


def run_doctor(scope: str | None = None) -> Dict[str, Any]:
    """
    Run SuperClaude health checks

    Every check returns its own "details" list; rendering them is the caller's
    choice, which is why no verbose flag is taken here.

    Args:
        scope: Installation scope to check; detected by walking up from the
            working directory when omitted

    Returns:
        Dict with check results, plus the scope and base path they were run
        against so the caller can name what it inspected
    """
    scope, base_path = resolve_reporting_target(scope)

    checks = [
        _check_pytest_plugin(),
        _check_skills_installed(base_path, scope),
        _check_configuration(),
        _check_hooks_installed(base_path, scope),
        _check_claude_sc_md(base_path, scope),
        _check_claude_md_import(base_path, scope),
    ]

    return {
        "checks": checks,
        "passed": all(check["passed"] for check in checks),
        "scope": scope,
        "base_path": str(base_path),
    }


def _check_pytest_plugin() -> Dict[str, Any]:
    """
    Check if pytest plugin is loaded

    Returns:
        Check result dict
    """
    try:
        import pytest

        # Try to get pytest config
        try:
            config = pytest.Config.fromdictargs({}, [])
            plugins = config.pluginmanager.list_plugin_distinfo()

            # Check if superclaude plugin is loaded
            superclaude_loaded = any(
                "superclaude" in str(plugin[0]).lower() for plugin in plugins
            )

            if superclaude_loaded:
                return {
                    "name": "pytest plugin loaded",
                    "passed": True,
                    "details": ["SuperClaude pytest plugin is active"],
                }
            else:
                return {
                    "name": "pytest plugin loaded",
                    "passed": False,
                    "details": ["SuperClaude plugin not found in pytest plugins"],
                }
        except Exception as e:
            return {
                "name": "pytest plugin loaded",
                "passed": False,
                "details": [f"Could not check pytest plugins: {e}"],
            }

    except ImportError:
        return {
            "name": "pytest plugin loaded",
            "passed": False,
            "details": ["pytest not installed"],
        }


def _check_skills_installed(base_path: Path, scope: str) -> Dict[str, Any]:
    """
    Check whether the skills SuperClaude ships are installed in this scope.

    Counted against the source manifest rather than by listing the directory:
    .claude/skills is shared with every other tool that installs skills, so a
    raw listing reports someone else's work as SuperClaude's.

    Args:
        base_path: Base installation path of the scope being checked
        scope: Installation scope, which decides how to phrase the repair

    Returns:
        Check result dict
    """
    from .install_inventory import _source_dir_names
    from .install_paths import _get_source_dir

    skills_dir = base_path / "skills"
    shipped = _source_dir_names(_get_source_dir("skills"))
    installed = sorted(
        name
        for name in shipped
        if (skills_dir / name / "SKILL.md").exists()
        or (skills_dir / name / "skill.md").exists()
    )

    if len(installed) == len(shipped):
        return {
            "name": "Skills installed",
            "passed": True,
            "details": [
                f"{len(installed)}/{len(shipped)} installed: {', '.join(installed)}"
                if installed
                else "No skills shipped by this release"
            ],
        }
    missing = sorted(shipped - set(installed))
    return {
        "name": "Skills installed",
        "passed": False,
        "details": [
            f"{len(installed)}/{len(shipped)} installed at {skills_dir}",
            f"Missing: {', '.join(missing)} — {_repair_command(scope, base_path)}",
        ],
    }


def _check_configuration() -> Dict[str, Any]:
    """
    Check SuperClaude configuration

    Returns:
        Check result dict
    """
    # Check if package is importable
    try:
        import superclaude

        version = superclaude.__version__

        return {
            "name": "Configuration",
            "passed": True,
            "details": [f"SuperClaude {version} installed correctly"],
        }
    except ImportError as e:
        return {
            "name": "Configuration",
            "passed": False,
            "details": [f"Could not import superclaude: {e}"],
        }


def _check_hooks_installed(base_path: Path, scope: str) -> Dict[str, Any]:
    """
    Check that SuperClaude's hooks are registered in this scope's settings file.

    Only entries the marker check attributes to SuperClaude count. Asking merely
    whether an event array is non-empty passed on hooks belonging to unrelated
    plugins, certifying an install whose own hooks were absent.

    Args:
        base_path: Base installation path of the scope being checked
        scope: Installation scope, which decides the settings filename

    Returns:
        Check result dict
    """
    from .install_settings import _is_superclaude_hook

    filename = settings_filename(scope)
    settings_file = base_path / filename
    label = f"Hooks in {filename}"

    if not settings_file.exists():
        return {
            "name": label,
            "passed": False,
            "details": [f"{settings_file} not found"],
        }

    try:
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "name": label,
            "passed": False,
            "details": [f"{filename} is invalid or unreadable"],
        }

    hooks = settings.get("hooks", {})
    expected = ["SessionStart", "UserPromptSubmit", "PostToolUse", "PreToolUse"]
    missing = [
        event
        for event in expected
        if not any(
            _is_superclaude_hook(entry)
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
            f"No SuperClaude hook registered for: {', '.join(missing)}",
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
