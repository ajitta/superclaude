"""Skill quality linter.

Validates SKILL.md manifests against required structure and content rules.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class LintIssue:
    """Single lint finding."""

    rule: str
    severity: str  # "error" | "warning"
    message: str


@dataclass
class SkillLintResult:
    """Results of linting a single skill."""

    skill_name: str
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter_dict, body) or (None, full_text) if no frontmatter."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None, text

    raw_yaml = match.group(1)
    body = match.group(2)

    if yaml is not None:
        try:
            data = yaml.safe_load(raw_yaml)
            return (data if isinstance(data, dict) else None), body
        except yaml.YAMLError:
            return None, body

    # Fallback: simple key: value extraction (no nested support)
    data: dict = {}
    for line in raw_yaml.splitlines():
        m = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if m:
            data[m.group(1)] = m.group(2).strip()
    return data, body


# ---------------------------------------------------------------------------
# Individual rule implementations
# ---------------------------------------------------------------------------

# Rule type: (skill_dir, frontmatter, body) -> list[LintIssue]
_RuleFunc = Callable[[Path, dict | None, str], list[LintIssue]]


def _rule_frontmatter_required(
    skill_dir: Path, fm: dict | None, body: str
) -> list[LintIssue]:
    """SKILL.md must have YAML frontmatter between --- delimiters."""
    if fm is None:
        return [
            LintIssue(
                rule="frontmatter-required",
                severity="error",
                message="SKILL.md is missing YAML frontmatter (expected --- delimiters)",
            )
        ]
    return []


def _rule_frontmatter_types(
    skill_dir: Path, fm: dict | None, body: str
) -> list[LintIssue]:
    """Required fields: name (str), description (str). Optional metadata must be dict."""
    if fm is None:
        # Already flagged by frontmatter-required; skip to avoid noise.
        return []

    issues: list[LintIssue] = []

    for field_name in ("name", "description"):
        if field_name not in fm:
            issues.append(
                LintIssue(
                    rule="frontmatter-types",
                    severity="error",
                    message=f"Required frontmatter field '{field_name}' is missing",
                )
            )
        elif not isinstance(fm[field_name], str):
            issues.append(
                LintIssue(
                    rule="frontmatter-types",
                    severity="error",
                    message=(
                        f"Frontmatter field '{field_name}' must be a string, "
                        f"got {type(fm[field_name]).__name__}"
                    ),
                )
            )

    if "metadata" in fm and not isinstance(fm["metadata"], dict):
        issues.append(
            LintIssue(
                rule="frontmatter-types",
                severity="error",
                message=(
                    f"Frontmatter field 'metadata' must be a dict if present, "
                    f"got {type(fm['metadata']).__name__}"
                ),
            )
        )

    return issues


def _rule_component_structure(
    skill_dir: Path, fm: dict | None, body: str
) -> list[LintIssue]:
    """Content must contain a <component XML tag."""
    if "<component" not in body:
        return [
            LintIssue(
                rule="component-structure",
                severity="error",
                message="SKILL.md body is missing a <component> XML element",
            )
        ]
    return []


def _rule_flow_section(
    skill_dir: Path, fm: dict | None, body: str
) -> list[LintIssue]:
    """Body should contain a <flow> section."""
    if "<flow" not in body and "<flow>" not in body:
        return [
            LintIssue(
                rule="flow-section",
                severity="warning",
                message="SKILL.md body is missing a <flow> section",
            )
        ]
    return []


def _rule_bounds_section(
    skill_dir: Path, fm: dict | None, body: str
) -> list[LintIssue]:
    """Body should contain a <bounds> section."""
    if "<bounds" not in body:
        return [
            LintIssue(
                rule="bounds-section",
                severity="warning",
                message="SKILL.md body is missing a <bounds> section",
            )
        ]
    return []


def _rule_examples_section(
    skill_dir: Path, fm: dict | None, body: str
) -> list[LintIssue]:
    """Body should contain an <examples> section."""
    if "<examples" not in body:
        return [
            LintIssue(
                rule="examples-section",
                severity="warning",
                message="SKILL.md body is missing an <examples> section",
            )
        ]
    return []


_SKILLS_PATH_SCRIPT_RE = re.compile(
    r"\{\{SKILLS_PATH\}\}/[^/]+/scripts/([^\s\"']+)"
)


def _extract_hook_commands(fm: dict | None) -> list[str]:
    """Recursively collect all 'command' string values from frontmatter metadata.hooks."""
    if not fm or not isinstance(fm.get("metadata"), dict):
        return []

    hooks_root = fm["metadata"].get("hooks")
    if not hooks_root:
        return []

    commands: list[str] = []

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            if "command" in node and isinstance(node["command"], str):
                commands.append(node["command"])
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(hooks_root)
    return commands


def _rule_file_references(
    skill_dir: Path, fm: dict | None, body: str
) -> list[LintIssue]:
    """Scripts referenced via {{SKILLS_PATH}} in hooks must exist under skills/<name>/scripts/."""
    commands = _extract_hook_commands(fm)
    if not commands:
        return []

    issues: list[LintIssue] = []
    for cmd in commands:
        for match in _SKILLS_PATH_SCRIPT_RE.finditer(cmd):
            script_filename = match.group(1)
            script_path = skill_dir / "scripts" / script_filename
            if not script_path.exists():
                issues.append(
                    LintIssue(
                        rule="file-references",
                        severity="warning",
                        message=(
                            f"Hook references script '{script_filename}' but "
                            f"'{script_path.relative_to(skill_dir.parent)}' does not exist"
                        ),
                    )
                )

    return issues


_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+")


def _rule_dependency_fields(
    skill_dir: Path, fm: dict | None, body: str
) -> list[LintIssue]:
    """Validate optional dependency/versioning fields: version, requires, enhances, changelog."""
    if fm is None:
        return []

    issues: list[LintIssue] = []
    metadata = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}

    # version: must be a string in semver format if present
    if "version" in fm:
        v = fm["version"]
        if not isinstance(v, str):
            issues.append(
                LintIssue(
                    rule="dependency-fields",
                    severity="warning",
                    message=(
                        f"Frontmatter field 'version' must be a string (e.g. \"1.0.0\"), "
                        f"got {type(v).__name__}"
                    ),
                )
            )
        elif not _SEMVER_RE.match(v):
            issues.append(
                LintIssue(
                    rule="dependency-fields",
                    severity="warning",
                    message=(
                        f"Frontmatter field 'version' should follow semver format "
                        f"(e.g. \"1.0.0\"), got {v!r}"
                    ),
                )
            )

    # requires: must be a dict with optional 'skills' and 'mcp' list-of-strings keys
    if "requires" in metadata:
        req = metadata["requires"]
        if not isinstance(req, dict):
            issues.append(
                LintIssue(
                    rule="dependency-fields",
                    severity="warning",
                    message=(
                        f"metadata.requires must be a dict with optional keys "
                        f"'skills' and 'mcp', got {type(req).__name__}"
                    ),
                )
            )
        else:
            for key in ("skills", "mcp"):
                if key in req:
                    val = req[key]
                    if not isinstance(val, list) or not all(
                        isinstance(s, str) for s in val
                    ):
                        issues.append(
                            LintIssue(
                                rule="dependency-fields",
                                severity="warning",
                                message=f"metadata.requires.{key} must be a list of strings",
                            )
                        )

    # enhances: must be a dict with optional 'skills' list-of-strings key
    if "enhances" in metadata:
        enh = metadata["enhances"]
        if not isinstance(enh, dict):
            issues.append(
                LintIssue(
                    rule="dependency-fields",
                    severity="warning",
                    message=(
                        f"metadata.enhances must be a dict with optional key "
                        f"'skills', got {type(enh).__name__}"
                    ),
                )
            )
        else:
            if "skills" in enh:
                val = enh["skills"]
                if not isinstance(val, list) or not all(
                    isinstance(s, str) for s in val
                ):
                    issues.append(
                        LintIssue(
                            rule="dependency-fields",
                            severity="warning",
                            message="metadata.enhances.skills must be a list of strings",
                        )
                    )

    # changelog: must be a list of strings if present
    if "changelog" in fm:
        cl = fm["changelog"]
        if not isinstance(cl, list) or not all(isinstance(s, str) for s in cl):
            issues.append(
                LintIssue(
                    rule="dependency-fields",
                    severity="warning",
                    message="Frontmatter field 'changelog' must be a list of strings",
                )
            )

    return issues


_ALL_RULES: list[_RuleFunc] = [
    _rule_frontmatter_required,
    _rule_frontmatter_types,
    _rule_component_structure,
    _rule_flow_section,
    _rule_bounds_section,
    _rule_examples_section,
    _rule_file_references,
    _rule_dependency_fields,
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def lint_skill(skill_dir: Path) -> SkillLintResult:
    """Lint a single skill directory.

    Looks for SKILL.md (case-insensitive: SKILL.md then skill.md). If neither
    exists the manifest is treated as absent and frontmatter-required is raised.
    """
    skill_name = skill_dir.name
    result = SkillLintResult(skill_name=skill_name)

    # Locate manifest
    manifest: Path | None = None
    for candidate in ("SKILL.md", "skill.md"):
        p = skill_dir / candidate
        if p.exists():
            manifest = p
            break

    if manifest is None:
        result.issues.append(
            LintIssue(
                rule="frontmatter-required",
                severity="error",
                message=f"No SKILL.md found in '{skill_dir}'",
            )
        )
        return result

    text = manifest.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)

    for rule_fn in _ALL_RULES:
        result.issues.extend(rule_fn(skill_dir, fm, body))

    return result


def lint_all_skills(root: Path) -> list[SkillLintResult]:
    """Lint all skills found directly under *root*.

    Directories whose names start with '_' (e.g. ``_testing``) are excluded.
    Results are sorted alphabetically by skill name.
    """
    results: list[SkillLintResult] = []

    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("_"):
            continue
        # Must contain SKILL.md (or skill.md) to be considered a skill
        if not (entry / "SKILL.md").exists() and not (entry / "skill.md").exists():
            continue
        results.append(lint_skill(entry))

    return results


def extract_dependencies(skill_dir: Path) -> dict:
    """Extract dependency info from a skill's SKILL.md frontmatter.

    Returns dict with keys: name, version, requires_skills, requires_mcp, enhances_skills.
    """
    manifest: Path | None = None
    for candidate in ("SKILL.md", "skill.md"):
        p = skill_dir / candidate
        if p.exists():
            manifest = p
            break

    if manifest is None:
        return {
            "name": skill_dir.name,
            "version": None,
            "requires_skills": [],
            "requires_mcp": [],
            "enhances_skills": [],
        }

    text = manifest.read_text(encoding="utf-8")
    fm, _ = _parse_frontmatter(text)

    if not fm:
        return {
            "name": skill_dir.name,
            "version": None,
            "requires_skills": [],
            "requires_mcp": [],
            "enhances_skills": [],
        }

    metadata = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    requires = metadata.get("requires") if isinstance(metadata.get("requires"), dict) else {}
    enhances = metadata.get("enhances") if isinstance(metadata.get("enhances"), dict) else {}

    version = fm.get("version")
    requires_skills = requires.get("skills", []) if isinstance(requires.get("skills"), list) else []
    requires_mcp = requires.get("mcp", []) if isinstance(requires.get("mcp"), list) else []
    enhances_skills = enhances.get("skills", []) if isinstance(enhances.get("skills"), list) else []

    return {
        "name": fm.get("name", skill_dir.name),
        "version": version if isinstance(version, str) else None,
        "requires_skills": [s for s in requires_skills if isinstance(s, str)],
        "requires_mcp": [s for s in requires_mcp if isinstance(s, str)],
        "enhances_skills": [s for s in enhances_skills if isinstance(s, str)],
    }
