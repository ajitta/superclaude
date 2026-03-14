"""
Structural validation tests for skill SKILL.md files.

Validates frontmatter fields, body content, and cross-field consistency
for all skill definitions in src/superclaude/skills/.

Tests cover:
- Frontmatter: name, description required; name matches directory
- Frontmatter policy: disable-model-invocation, context, allowed-tools per spec
- Body: minimum content length, not empty
- Superpowers compatibility: skill names match upstream exactly
"""

import re
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent.parent / "src" / "superclaude" / "skills"

# Expected superpowers-compatible skill names (12 ported + 3 existing)
SUPERPOWERS_SKILL_NAMES = {
    "brainstorming",
    "writing-plans",
    "verification-before-completion",
    "executing-plans",
    "test-driven-development",
    "systematic-debugging",
    "requesting-code-review",
    "receiving-code-review",
    "finishing-a-development-branch",
    "dispatching-parallel-agents",
    "using-git-worktrees",
    "using-superclaude",
}

EXISTING_SKILL_NAMES = {
    "confidence-check",
    "ship",
    "simplicity-coach",
}

ALL_SKILL_NAMES = SUPERPOWERS_SKILL_NAMES | EXISTING_SKILL_NAMES

# Skills that MUST have disable-model-invocation: true (per spec)
SIDE_EFFECT_SKILLS = {
    "finishing-a-development-branch",
    "dispatching-parallel-agents",
    "using-git-worktrees",
}

# Skills that MUST have context: fork (per spec)
FORK_CONTEXT_SKILLS = {
    "executing-plans",
    "requesting-code-review",
}

# All skill directories with SKILL.md
SKILL_DIRS = sorted(
    [d for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
)
SKILL_IDS = [d.name for d in SKILL_DIRS]


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract YAML frontmatter from markdown text (simple key: value parsing)."""
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fields = {}
    current_key = None
    for line in match.group(1).strip().splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            key, _, value = line.partition(":")
            current_key = key.strip()
            fields[current_key] = value.strip()
        elif current_key and (line.startswith("  ") or line.startswith("\t")):
            # Continuation of multiline value
            fields[current_key] = (fields.get(current_key, "") + " " + line.strip()).strip()
    return fields


@pytest.fixture(params=SKILL_DIRS, ids=SKILL_IDS)
def skill(request) -> tuple[str, str, dict[str, str]]:
    """Yield (dirname, content, frontmatter) for each skill."""
    skill_dir: Path = request.param
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    return skill_dir.name, content, fm


# --- Skill Count Tests ---


class TestSkillCoverage:
    """Validate all expected skills exist."""

    def test_total_skill_count(self):
        """Must have exactly 15 skills (12 ported + 3 existing)."""
        assert len(SKILL_DIRS) == 15, (
            f"Expected 15 skills, found {len(SKILL_DIRS)}: {SKILL_IDS}"
        )

    def test_all_superpowers_skills_present(self):
        """All 12 superpowers-compatible skill names must exist."""
        actual = set(SKILL_IDS)
        missing = SUPERPOWERS_SKILL_NAMES - actual
        assert not missing, f"Missing superpowers skills: {missing}"

    def test_all_existing_skills_preserved(self):
        """Original 3 skills must still exist."""
        actual = set(SKILL_IDS)
        missing = EXISTING_SKILL_NAMES - actual
        assert not missing, f"Missing existing skills: {missing}"

    def test_no_unexpected_skills(self):
        """No unexpected skill directories."""
        actual = set(SKILL_IDS)
        unexpected = actual - ALL_SKILL_NAMES
        assert not unexpected, f"Unexpected skills: {unexpected}"


# --- Frontmatter Tests ---


class TestSkillFrontmatter:
    """Validate YAML frontmatter in every skill."""

    def test_has_frontmatter(self, skill):
        dirname, content, fm = skill
        assert fm, f"{dirname}: missing YAML frontmatter (--- block)"

    def test_has_name(self, skill):
        dirname, content, fm = skill
        assert "name" in fm, f"{dirname}: frontmatter missing 'name'"

    def test_name_matches_directory(self, skill):
        dirname, content, fm = skill
        assert fm.get("name") == dirname, (
            f"{dirname}: name='{fm.get('name')}' doesn't match directory '{dirname}'"
        )

    def test_has_description(self, skill):
        dirname, content, fm = skill
        assert "description" in fm, f"{dirname}: frontmatter missing 'description'"

    def test_description_not_empty(self, skill):
        dirname, content, fm = skill
        desc = fm.get("description", "")
        assert len(desc) > 10, (
            f"{dirname}: description too short ({len(desc)} chars)"
        )

    def test_no_forbidden_agent_fields(self, skill):
        """Skills must not have agent-only frontmatter fields."""
        dirname, content, fm = skill
        forbidden = {"model", "permissionMode", "memory", "maxTurns", "color"}
        found = forbidden & set(fm.keys())
        assert not found, f"{dirname}: has agent-only fields: {found}"


# --- Frontmatter Policy Tests (from spec) ---


class TestSkillFrontmatterPolicy:
    """Validate frontmatter matches the spec's policy table."""

    def test_side_effect_skills_have_disable_model_invocation(self, skill):
        dirname, content, fm = skill
        if dirname in SIDE_EFFECT_SKILLS:
            assert fm.get("disable-model-invocation") == "true", (
                f"{dirname}: side-effect skill must have disable-model-invocation: true"
            )

    def test_fork_skills_have_context(self, skill):
        dirname, content, fm = skill
        if dirname in FORK_CONTEXT_SKILLS:
            assert fm.get("context") == "fork", (
                f"{dirname}: must have context: fork per spec"
            )

    def test_non_fork_skills_no_agent_field(self, skill):
        """Skills without context: fork must not have agent: field."""
        dirname, content, fm = skill
        if fm.get("context") != "fork":
            assert "agent" not in fm, (
                f"{dirname}: has agent: without context: fork (agent is ignored inline)"
            )

    def test_non_side_effect_skills_no_disable_model(self, skill):
        """Non-side-effect skills should not block auto-invocation."""
        dirname, content, fm = skill
        if dirname not in SIDE_EFFECT_SKILLS and dirname in SUPERPOWERS_SKILL_NAMES:
            assert fm.get("disable-model-invocation") != "true", (
                f"{dirname}: process skill should not have disable-model-invocation"
            )


# --- Body Content Tests ---


class TestSkillBody:
    """Validate body content of skills."""

    def test_minimum_content_length(self, skill):
        dirname, content, fm = skill
        # Strip frontmatter to get body
        body = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL).strip()
        assert len(body) > 200, (
            f"{dirname}: body too short ({len(body)} chars), expected > 200"
        )

    def test_body_under_500_lines(self, skill):
        """Per skill-authoring rules, body must be under 500 lines."""
        dirname, content, fm = skill
        body = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL).strip()
        line_count = len(body.splitlines())
        assert line_count < 500, (
            f"{dirname}: body has {line_count} lines, max 500"
        )

    def test_has_title(self, skill):
        """Every skill body should start with a markdown heading."""
        dirname, content, fm = skill
        body = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL).strip()
        assert body.startswith("#") or body.startswith("<"), (
            f"{dirname}: body should start with heading or XML tag"
        )


# --- Workflow Gates Test ---


class TestWorkflowGates:
    """Validate workflow gates are defined in RULES.md."""

    def test_rules_has_workflow_gates(self):
        rules_path = SKILLS_DIR.parent / "core" / "RULES.md"
        content = rules_path.read_text(encoding="utf-8")
        assert "<workflow_gates" in content, "RULES.md missing <workflow_gates> section"

    def test_rules_has_skill_priority(self):
        rules_path = SKILLS_DIR.parent / "core" / "RULES.md"
        content = rules_path.read_text(encoding="utf-8")
        assert "<skill_priority" in content, "RULES.md missing <skill_priority> section"

    def test_workflow_gates_mention_key_skills(self):
        rules_path = SKILLS_DIR.parent / "core" / "RULES.md"
        content = rules_path.read_text(encoding="utf-8")
        for skill_name in ["brainstorming", "writing-plans", "executing-plans", "verification"]:
            assert skill_name in content, (
                f"RULES.md workflow gates missing reference to '{skill_name}'"
            )
