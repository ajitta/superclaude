"""
Drift Detection for SuperClaude Installation

Compares source files against installed files to detect drift
(content mismatches, missing files, extra files).
"""

from pathlib import Path
from typing import Any, Dict

from .install_paths import COMPONENTS, _get_package_root, _get_source_dir, _get_target_dir


# File status constants
OK = "OK"
MISSING = "MISSING"       # In source but not in target
DRIFTED = "DRIFTED"       # Content mismatch
EXTRA = "EXTRA"           # In target but not in source


def _get_template_vars(base_path: Path) -> dict:
    """Get template variables that install resolves in SKILL.md files."""
    scripts = (base_path / "superclaude" / "scripts").resolve().as_posix()
    skills = (base_path / "skills").resolve().as_posix()
    return {"{{SCRIPTS_PATH}}": scripts, "{{SKILLS_PATH}}": skills}


def _compare_files(source: Path, target: Path, template_vars: dict | None = None) -> str:
    """Compare two files by content. Returns status string.

    If template_vars is provided, resolve them in source content before comparing
    (skills have {{SKILLS_PATH}} etc. replaced at install time).
    """
    if not target.exists():
        return MISSING
    try:
        source_content = source.read_text(encoding="utf-8")
        target_content = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return DRIFTED
    if template_vars:
        for placeholder, value in template_vars.items():
            source_content = source_content.replace(placeholder, value)
    return OK if source_content == target_content else DRIFTED


def _check_component(component: str, base_path: Path) -> Dict[str, str]:
    """Check a single component for drift. Returns {filename: status}."""
    source_dir = _get_source_dir(component)
    target_dir = _get_target_dir(component, base_path)
    results = {}

    if not source_dir.exists():
        return results

    if component == "skills":
        # Skills have template variables resolved at install time
        template_vars = _get_template_vars(base_path)

        for skill_dir in sorted(source_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith(("_", ".")):
                continue
            source_manifest = skill_dir / "SKILL.md"
            if not source_manifest.exists():
                source_manifest = skill_dir / "skill.md"
            if not source_manifest.exists():
                continue

            target_skill_dir = target_dir / skill_dir.name
            target_manifest = target_skill_dir / source_manifest.name
            key = f"{skill_dir.name}/{source_manifest.name}"

            if not target_skill_dir.exists():
                results[key] = MISSING
            elif not target_manifest.exists():
                results[key] = MISSING
            else:
                results[key] = _compare_files(source_manifest, target_manifest, template_vars)

        # Check for extra skill directories in target
        if target_dir.exists():
            source_skill_names = {
                d.name for d in source_dir.iterdir()
                if d.is_dir() and not d.name.startswith(("_", "."))
            }
            for target_skill in sorted(target_dir.iterdir()):
                if target_skill.is_dir() and target_skill.name not in source_skill_names:
                    results[f"{target_skill.name}/"] = EXTRA
    else:
        # Standard components: compare .md files (skip README)
        source_files = {
            f.name for f in source_dir.glob("*.md")
            if f.stem.upper() != "README"
        }

        for filename in sorted(source_files):
            source_file = source_dir / filename
            target_file = target_dir / filename
            results[filename] = _compare_files(source_file, target_file)

        # Check for extra files in target
        if target_dir.exists():
            target_files = {
                f.name for f in target_dir.glob("*.md")
                if f.stem.upper() != "README"
            }
            for filename in sorted(target_files - source_files):
                results[filename] = EXTRA

    return results


def _check_claude_sc_md(base_path: Path) -> str:
    """Check CLAUDE_SC.md specifically."""
    package_root = _get_package_root()
    source = package_root / "CLAUDE_SC.md"
    target = base_path / "superclaude" / "CLAUDE_SC.md"

    if not source.exists():
        return MISSING
    return _compare_files(source, target)


def verify_drift(base_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Compare source vs installed files for each component.

    Args:
        base_path: Installation base path (e.g., ~/.claude)
        verbose: Include per-file details

    Returns:
        Dict with drift results per component and totals.
    """
    components = {}
    total_ok = 0
    total_drifted = 0
    total_missing = 0
    total_extra = 0

    for component in COMPONENTS:
        file_results = _check_component(component, base_path)
        ok = sum(1 for s in file_results.values() if s == OK)
        drifted = sum(1 for s in file_results.values() if s == DRIFTED)
        missing = sum(1 for s in file_results.values() if s == MISSING)
        extra = sum(1 for s in file_results.values() if s == EXTRA)

        components[component] = {
            "ok": ok,
            "drifted": drifted,
            "missing": missing,
            "extra": extra,
            "files": file_results if verbose else {},
        }

        total_ok += ok
        total_drifted += drifted
        total_missing += missing
        total_extra += extra

    # Check CLAUDE_SC.md
    sc_status = _check_claude_sc_md(base_path)
    if sc_status == OK:
        total_ok += 1
    elif sc_status == DRIFTED:
        total_drifted += 1
    elif sc_status == MISSING:
        total_missing += 1

    return {
        "components": components,
        "claude_sc_md": sc_status,
        "total_ok": total_ok,
        "total_drifted": total_drifted,
        "total_missing": total_missing,
        "total_extra": total_extra,
        "clean": total_drifted == 0 and total_missing == 0 and total_extra == 0,
    }
