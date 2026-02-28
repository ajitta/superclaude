"""
SuperClaude Doctor Command

Health check for SuperClaude installation.
"""

import json
from pathlib import Path
from typing import Any, Dict


def run_doctor(verbose: bool = False) -> Dict[str, Any]:
    """
    Run SuperClaude health checks

    Args:
        verbose: Include detailed diagnostic information

    Returns:
        Dict with check results
    """
    checks = []

    # Check 1: pytest plugin loaded
    checks.append(_check_pytest_plugin())

    # Check 2: Skills installed
    checks.append(_check_skills_installed())

    # Check 3: Configuration
    checks.append(_check_configuration())

    # Check 4: Hooks in settings.json
    checks.append(_check_hooks_installed())

    # Check 5: CLAUDE_SC.md exists
    checks.append(_check_claude_sc_md())

    # Check 6: CLAUDE.md import
    checks.append(_check_claude_md_import())

    return {
        "checks": checks,
        "passed": all(check["passed"] for check in checks),
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


def _check_skills_installed() -> Dict[str, Any]:
    """
    Check if any skills are installed

    Returns:
        Check result dict
    """
    skills_dir = Path("~/.claude/skills").expanduser()

    if not skills_dir.exists():
        return {
            "name": "Skills installed",
            "passed": True,  # Optional, so pass
            "details": ["No skills installed (optional)"],
        }

    # Find skills (directories with SKILL.md or implementation.md)
    skills = []
    for item in skills_dir.iterdir():
        if not item.is_dir():
            continue
        has_manifest = (
            (item / "SKILL.md").exists()
            or (item / "skill.md").exists()
            or (item / "implementation.md").exists()
        )
        if has_manifest:
            skills.append(item.name)

    if skills:
        return {
            "name": "Skills installed",
            "passed": True,
            "details": [f"{len(skills)} skill(s) installed: {', '.join(skills)}"],
        }
    else:
        return {
            "name": "Skills installed",
            "passed": True,  # Optional
            "details": ["No skills installed (optional)"],
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


def _check_hooks_installed() -> Dict[str, Any]:
    """Check if SuperClaude hooks are present in settings.json."""
    settings_file = Path.home() / ".claude" / "settings.json"

    if not settings_file.exists():
        return {
            "name": "Hooks in settings.json",
            "passed": False,
            "details": ["settings.json not found"],
        }

    try:
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "name": "Hooks in settings.json",
            "passed": False,
            "details": ["settings.json is invalid or unreadable"],
        }

    hooks = settings.get("hooks", {})
    expected = ["SessionStart", "UserPromptSubmit", "PostToolUse", "PreToolUse"]
    found = [h for h in expected if hooks.get(h)]
    missing = [h for h in expected if not hooks.get(h)]

    if not missing:
        return {
            "name": "Hooks in settings.json",
            "passed": True,
            "details": [f"All {len(found)} hook types present"],
        }
    return {
        "name": "Hooks in settings.json",
        "passed": False,
        "details": [f"Missing hook types: {', '.join(missing)}"],
    }


def _check_claude_sc_md() -> Dict[str, Any]:
    """Check if CLAUDE_SC.md exists in ~/.claude/superclaude/."""
    sc_md = Path.home() / ".claude" / "superclaude" / "CLAUDE_SC.md"
    if sc_md.exists():
        return {
            "name": "CLAUDE_SC.md",
            "passed": True,
            "details": [f"Found at {sc_md}"],
        }
    return {
        "name": "CLAUDE_SC.md",
        "passed": False,
        "details": ["CLAUDE_SC.md not found — run 'superclaude install'"],
    }


def _check_claude_md_import() -> Dict[str, Any]:
    """Check if CLAUDE.md imports CLAUDE_SC.md."""
    claude_md = Path.home() / ".claude" / "CLAUDE.md"

    if not claude_md.exists():
        return {
            "name": "CLAUDE.md import",
            "passed": False,
            "details": ["CLAUDE.md not found"],
        }

    try:
        content = claude_md.read_text(encoding="utf-8")
    except OSError:
        return {
            "name": "CLAUDE.md import",
            "passed": False,
            "details": ["CLAUDE.md is unreadable"],
        }

    if "@superclaude/CLAUDE_SC.md" in content:
        return {
            "name": "CLAUDE.md import",
            "passed": True,
            "details": ["@superclaude/CLAUDE_SC.md import present"],
        }
    return {
        "name": "CLAUDE.md import",
        "passed": False,
        "details": ["Missing @superclaude/CLAUDE_SC.md import — run 'superclaude install'"],
    }
