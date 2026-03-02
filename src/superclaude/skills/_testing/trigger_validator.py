"""Trigger conflict validator.

Detects trigger overlaps between skills and commands.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TriggerConflict:
    """A detected trigger overlap."""

    pattern: str
    sources: list[str]  # list of source names (e.g., ["skill:ship", "command:git"])
    severity: str  # "error" for same-category, "warning" for cross-category


def _extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    try:
        import yaml
    except ImportError:
        yaml = None

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    raw = match.group(1)
    if yaml:
        try:
            return yaml.safe_load(raw) or {}
        except yaml.YAMLError:
            return {}

    # Fallback: simple key-value parsing
    result = {}
    for line in raw.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def _collect_skill_triggers(skills_root: Path) -> dict[str, list[str]]:
    """Collect trigger patterns from skill manifests.

    Returns: {skill_name: [trigger_keywords]}
    """
    triggers: dict[str, list[str]] = {}
    if not skills_root.exists():
        return triggers

    for skill_dir in sorted(skills_root.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
            continue
        manifest = skill_dir / "SKILL.md"
        if not manifest.exists():
            manifest = skill_dir / "skill.md"
        if not manifest.exists():
            continue

        fm = _extract_frontmatter(manifest.read_text(encoding="utf-8"))
        name = fm.get("name", skill_dir.name)

        # Extract triggers from name as keywords
        keywords: set[str] = set()
        keywords.add(name)
        # Add name parts split by hyphens
        keywords.update(name.split("-"))

        triggers[f"skill:{name}"] = sorted(keywords)

    return triggers


def _collect_command_triggers(commands_root: Path) -> dict[str, list[str]]:
    """Collect trigger patterns from command files.

    Returns: {command_name: [trigger_keywords]}
    """
    triggers: dict[str, list[str]] = {}
    if not commands_root.exists():
        return triggers

    for cmd_file in sorted(commands_root.glob("*.md")):
        if cmd_file.name.startswith("_") or cmd_file.name == "README.md":
            continue

        fm = _extract_frontmatter(cmd_file.read_text(encoding="utf-8"))
        name = fm.get("name", cmd_file.stem)

        keywords: set[str] = set()
        keywords.add(name)
        keywords.update(name.split("-"))

        triggers[f"command:{name}"] = sorted(keywords)

    return triggers


def validate_triggers(
    skills_root: Path,
    commands_root: Path,
) -> list[TriggerConflict]:
    """Detect trigger overlaps between skills and commands.

    Args:
        skills_root: Path to skills directory
        commands_root: Path to commands directory

    Returns:
        List of detected conflicts, sorted by severity then pattern
    """
    skill_triggers = _collect_skill_triggers(skills_root)
    command_triggers = _collect_command_triggers(commands_root)

    # Build reverse index: keyword -> [sources]
    keyword_sources: dict[str, list[str]] = {}

    for source, keywords in {**skill_triggers, **command_triggers}.items():
        for kw in keywords:
            if len(kw) < 3:  # Skip very short keywords
                continue
            keyword_sources.setdefault(kw, []).append(source)

    # Find conflicts (keywords appearing in multiple sources)
    conflicts: list[TriggerConflict] = []
    for pattern, sources in sorted(keyword_sources.items()):
        if len(sources) <= 1:
            continue

        # Determine severity: same category = error, cross-category = warning
        categories = {s.split(":")[0] for s in sources}
        severity = "error" if len(categories) == 1 else "warning"

        conflicts.append(
            TriggerConflict(
                pattern=pattern,
                sources=sorted(sources),
                severity=severity,
            )
        )

    # Sort: errors first, then by pattern
    conflicts.sort(key=lambda c: (0 if c.severity == "error" else 1, c.pattern))
    return conflicts
