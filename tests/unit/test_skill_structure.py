"""
Structural validation tests for skill SKILL.md files.

Validates frontmatter fields, body content, and cross-field consistency
for all skill definitions in src/superclaude/skills/.

Skills are CC-native execution containers limited to hooks, safety,
and script execution. Workflow procedures belong in commands/.
"""

import re
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent.parent / "src" / "superclaude" / "skills"

# All superclaude skill names — only CC-native capability skills remain
# (hooks, disable-model-invocation, allowed-tools, scripts)
HOOK_SKILL_NAMES = {
    "confidence-check",       # PreToolUse hook + validation script
    "simplicity-coach",       # Stop hook + dependency-audit script
}

SAFETY_SKILL_NAMES = {
    "ship",                          # disable-model-invocation
    "finishing-a-development-branch", # disable-model-invocation + allowed-tools
}

ALL_SKILL_NAMES = HOOK_SKILL_NAMES | SAFETY_SKILL_NAMES

# Skills that MUST have disable-model-invocation: true
SIDE_EFFECT_SKILLS = {
    "ship",
    "finishing-a-development-branch",
}

# No fork-context skills remain (requesting-code-review migrated to /sc:review)
FORK_CONTEXT_SKILLS: set[str] = set()

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
        """Must have exactly 4 skills (2 hook + 2 safety)."""
        assert len(SKILL_DIRS) == 4, (
            f"Expected 4 skills, found {len(SKILL_DIRS)}: {SKILL_IDS}"
        )

    def test_all_hook_skills_present(self):
        """Both hook skills must exist."""
        actual = set(SKILL_IDS)
        missing = HOOK_SKILL_NAMES - actual
        assert not missing, f"Missing hook skills: {missing}"

    def test_all_safety_skills_present(self):
        """Both safety skills must exist."""
        actual = set(SKILL_IDS)
        missing = SAFETY_SKILL_NAMES - actual
        assert not missing, f"Missing safety skills: {missing}"

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


# --- Frontmatter Policy Tests ---


class TestSkillFrontmatterPolicy:
    """Validate frontmatter matches policy."""

    def test_side_effect_skills_have_disable_model_invocation(self, skill):
        dirname, content, fm = skill
        if dirname in SIDE_EFFECT_SKILLS:
            assert fm.get("disable-model-invocation") == "true", (
                f"{dirname}: side-effect skill must have disable-model-invocation: true"
            )

    def test_no_orphaned_fork_context(self, skill):
        """No remaining skills should have context: fork."""
        dirname, content, fm = skill
        assert fm.get("context") != "fork", (
            f"{dirname}: context: fork skills have been migrated to commands"
        )

    def test_no_orphaned_agent_field(self, skill):
        """No remaining skills should have agent: field."""
        dirname, content, fm = skill
        assert "agent" not in fm, (
            f"{dirname}: agent: field skills have been migrated to commands"
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
    """Validate workflow gates reference commands in RULES.md."""

    def test_rules_has_workflow_gates(self):
        rules_path = SKILLS_DIR.parent / "core" / "RULES.md"
        content = rules_path.read_text(encoding="utf-8")
        assert "<workflow_gates" in content, "RULES.md missing <workflow_gates> section"

    def test_workflow_gates_reference_commands(self):
        rules_path = SKILLS_DIR.parent / "core" / "RULES.md"
        content = rules_path.read_text(encoding="utf-8")
        for cmd in ["/sc:brainstorm", "/sc:plan", "/sc:implement", "/sc:test"]:
            assert cmd in content, (
                f"RULES.md workflow gates missing reference to '{cmd}'"
            )


class TestNoAggressiveLanguage:
    """Validate skills do not contain aggressive enforcement language.

    Per Anthropic Opus 4.6 prompting guidance: 'dial back aggressive language'
    and 'prefer general instructions over prescriptive steps'.
    """

    FORBIDDEN_PATTERNS = [
        "ABSOLUTELY MUST",
        "IRON LAW",
        "NOT NEGOTIABLE",
        "VIOLATING LETTER",
        "EXTREMELY_IMPORTANT",
        "EXTREMELY-IMPORTANT",
    ]

    def test_no_aggressive_language(self, skill):
        dirname, content, fm = skill
        for pattern in self.FORBIDDEN_PATTERNS:
            assert pattern not in content, (
                f"{dirname}: contains aggressive language '{pattern}'"
            )
