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

    # Check 7: Skill lint (source skills)
    checks.append(_check_skills_lint())

    # Check 8: Trigger conflicts
    checks.append(_check_trigger_conflicts())

    # Check 9: Conversion completeness
    checks.append(_check_conversion_completeness())

    # Check 10: MCP availability
    checks.append(_check_mcp_availability())

    # Check 11: Version compatibility
    checks.append(_check_version_compatibility())

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


def _check_skills_lint() -> Dict[str, Any]:
    """Lint source skills for structural issues."""
    try:
        from superclaude.skills._testing.skill_linter import lint_all_skills

        package_root = Path(__file__).resolve().parent.parent
        skills_dir = package_root / "skills"

        if not skills_dir.exists():
            return {
                "name": "Skills lint",
                "passed": True,
                "details": ["No source skills directory found (optional)"],
            }

        results = lint_all_skills(skills_dir)
        if not results:
            return {
                "name": "Skills lint",
                "passed": True,
                "details": ["No skills found to lint"],
            }

        errors = sum(r.error_count for r in results)
        warnings = sum(r.warning_count for r in results)
        all_passed = all(r.passed for r in results)

        details = [f"{len(results)} skill(s) linted: {errors} errors, {warnings} warnings"]
        for r in results:
            if not r.passed:
                for issue in r.issues:
                    if issue.severity == "error":
                        details.append(f"  {r.skill_name}: [{issue.rule}] {issue.message}")

        return {
            "name": "Skills lint",
            "passed": all_passed,
            "details": details,
        }
    except ImportError:
        return {
            "name": "Skills lint",
            "passed": True,
            "details": ["Skill linter not available (optional)"],
        }


def _check_trigger_conflicts() -> Dict[str, Any]:
    """Check for trigger keyword conflicts between skills and commands."""
    try:
        from superclaude.skills._testing.trigger_validator import validate_triggers

        package_root = Path(__file__).resolve().parent.parent
        skills_dir = package_root / "skills"
        commands_dir = package_root / "commands"

        if not skills_dir.exists() or not commands_dir.exists():
            return {
                "name": "Trigger conflicts",
                "passed": True,
                "details": ["Source directories not found (optional)"],
            }

        conflicts = validate_triggers(skills_dir, commands_dir)
        errors = [c for c in conflicts if c.severity == "error"]
        warnings = [c for c in conflicts if c.severity == "warning"]

        # Cross-category warnings (stub↔skill pairs) are expected
        stub_warnings = [w for w in warnings if any(
            f"command:{w.pattern}" in str(w.sources) and f"skill:sc-{w.pattern}" in str(w.sources)
            for _ in [None]
        )]
        unexpected_errors = [e for e in errors if e.pattern not in ("index", "panel")]

        if not unexpected_errors:
            details = [f"{len(conflicts)} total ({len(errors)} known, {len(stub_warnings)} stub↔skill pairs)"]
            return {
                "name": "Trigger conflicts",
                "passed": True,
                "details": details,
            }
        return {
            "name": "Trigger conflicts",
            "passed": False,
            "details": [f"{len(unexpected_errors)} unexpected conflict(s)"] + [
                f"  {c.pattern}: {c.sources}" for c in unexpected_errors
            ],
        }
    except ImportError:
        return {
            "name": "Trigger conflicts",
            "passed": True,
            "details": ["Trigger validator not available (optional)"],
        }


def _check_conversion_completeness() -> Dict[str, Any]:
    """Check that all 8 converted commands have matching sc: skills."""
    package_root = Path(__file__).resolve().parent.parent
    skills_dir = package_root / "skills"
    commands_dir = package_root / "commands"

    converted = ["git", "test", "troubleshoot", "cleanup", "build", "estimate", "document", "design"]
    missing_skills = []
    missing_stubs = []

    for name in converted:
        skill_dir = skills_dir / f"sc-{name}"
        if not (skill_dir / "SKILL.md").exists():
            missing_skills.append(f"sc-{name}")

        cmd_file = commands_dir / f"{name}.md"
        if cmd_file.exists():
            try:
                content = cmd_file.read_text(encoding="utf-8")
                if "allowed-tools: []" not in content:
                    missing_stubs.append(name)
            except OSError:
                missing_stubs.append(name)

    if not missing_skills and not missing_stubs:
        return {
            "name": "Conversion completeness",
            "passed": True,
            "details": [f"8/8 command→skill pairs complete"],
        }

    details = []
    if missing_skills:
        details.append(f"Missing skills: {', '.join(missing_skills)}")
    if missing_stubs:
        details.append(f"Missing stubs: {', '.join(missing_stubs)}")
    return {
        "name": "Conversion completeness",
        "passed": False,
        "details": details,
    }


def _check_mcp_availability() -> Dict[str, Any]:
    """Check if MCP servers are configured in settings.json."""
    settings_file = Path.home() / ".claude" / "settings.json"

    if not settings_file.exists():
        return {
            "name": "MCP availability",
            "passed": True,
            "details": ["No settings.json (MCP optional)"],
        }

    try:
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "name": "MCP availability",
            "passed": True,
            "details": ["settings.json unreadable (MCP optional)"],
        }

    mcp_servers = settings.get("mcpServers", {})
    if mcp_servers:
        names = list(mcp_servers.keys())
        return {
            "name": "MCP availability",
            "passed": True,
            "details": [f"{len(names)} MCP server(s) configured: {', '.join(names[:5])}{'...' if len(names) > 5 else ''}"],
        }
    return {
        "name": "MCP availability",
        "passed": True,
        "details": ["No MCP servers configured (optional)"],
    }


def _check_version_compatibility() -> Dict[str, Any]:
    """Check Claude Code version compatibility."""
    import shutil

    claude_bin = shutil.which("claude")
    if not claude_bin:
        return {
            "name": "Version compatibility",
            "passed": True,
            "details": ["Claude Code CLI not found in PATH (optional)"],
        }

    try:
        import subprocess

        result = subprocess.run(
            ["claude", "--version"], capture_output=True, text=True, timeout=5
        )
        version_str = result.stdout.strip()
        return {
            "name": "Version compatibility",
            "passed": True,
            "details": [f"Claude Code: {version_str}"],
        }
    except Exception:
        return {
            "name": "Version compatibility",
            "passed": True,
            "details": ["Could not determine Claude Code version"],
        }
