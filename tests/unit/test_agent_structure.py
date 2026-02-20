"""
Structural validation tests for agent markdown files.

Validates frontmatter fields, XML structure, and cross-field consistency
for all agent definitions in src/superclaude/agents/.
"""

import re
from pathlib import Path

import pytest

AGENTS_DIR = Path(__file__).parent.parent.parent / "src" / "superclaude" / "agents"

VALID_AUTONOMY_LEVELS = {"high", "medium", "low"}
VALID_MEMORY_SCOPES = {"user", "project", "local"}

# All agent .md files (excluding README)
AGENT_FILES = sorted(
    [f for f in AGENTS_DIR.glob("*.md") if f.name != "README.md"]
)
AGENT_IDS = [f.stem for f in AGENT_FILES]


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract YAML frontmatter from markdown text."""
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def extract_xml_attr(text: str, tag: str, attr: str) -> str | None:
    """Extract an attribute value from the first occurrence of an XML tag."""
    pattern = rf"<{tag}\b[^>]*\b{attr}=[\"']([^\"']*)[\"']"
    match = re.search(pattern, text)
    return match.group(1) if match else None


def extract_xml_content(text: str, tag: str) -> str | None:
    """Extract text content from the first occurrence of an XML tag."""
    pattern = rf"<{tag}\b[^>]*>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else None


@pytest.fixture(params=AGENT_FILES, ids=AGENT_IDS)
def agent(request) -> tuple[str, str, dict[str, str]]:
    """Yield (stem, content, frontmatter) for each agent file."""
    path: Path = request.param
    content = path.read_text()
    fm = parse_frontmatter(content)
    return path.stem, content, fm


class TestAgentFrontmatter:
    """Validate YAML frontmatter in every agent file."""

    def test_has_frontmatter(self, agent):
        stem, content, fm = agent
        assert fm, f"{stem}: missing YAML frontmatter (--- block)"

    def test_has_name(self, agent):
        stem, content, fm = agent
        assert "name" in fm, f"{stem}: frontmatter missing 'name'"

    def test_name_matches_filename(self, agent):
        stem, content, fm = agent
        assert fm.get("name") == stem, (
            f"{stem}: frontmatter name '{fm.get('name')}' != filename '{stem}'"
        )

    def test_has_description(self, agent):
        stem, content, fm = agent
        assert "description" in fm, f"{stem}: frontmatter missing 'description'"
        assert len(fm["description"]) > 10, (
            f"{stem}: description too short"
        )

    def test_has_autonomy(self, agent):
        stem, content, fm = agent
        assert "autonomy" in fm, f"{stem}: frontmatter missing 'autonomy'"

    def test_autonomy_valid(self, agent):
        stem, content, fm = agent
        level = fm.get("autonomy", "")
        assert level in VALID_AUTONOMY_LEVELS, (
            f"{stem}: autonomy '{level}' not in {VALID_AUTONOMY_LEVELS}"
        )

    def test_has_memory(self, agent):
        stem, content, fm = agent
        assert "memory" in fm, f"{stem}: frontmatter missing 'memory'"

    def test_memory_valid(self, agent):
        stem, content, fm = agent
        scope = fm.get("memory", "")
        assert scope in VALID_MEMORY_SCOPES, (
            f"{stem}: memory '{scope}' not in {VALID_MEMORY_SCOPES}"
        )


class TestAgentXMLStructure:
    """Validate XML component structure in every agent file."""

    def test_has_component_open(self, agent):
        stem, content, _ = agent
        assert "<component" in content, f"{stem}: missing <component> tag"

    def test_has_component_close(self, agent):
        stem, content, _ = agent
        assert "</component>" in content, f"{stem}: missing </component>"

    def test_component_name_matches(self, agent):
        stem, content, _ = agent
        name = extract_xml_attr(content, "component", "name")
        assert name == stem, (
            f"{stem}: component name='{name}' != filename '{stem}'"
        )

    def test_component_type_is_agent(self, agent):
        stem, content, _ = agent
        ctype = extract_xml_attr(content, "component", "type")
        assert ctype == "agent", (
            f"{stem}: component type='{ctype}', expected 'agent'"
        )

    def test_has_triggers(self, agent):
        stem, content, _ = agent
        triggers = extract_xml_content(content, "triggers")
        assert triggers, f"{stem}: missing or empty <triggers>"
        assert "|" in triggers, (
            f"{stem}: triggers should be pipe-delimited"
        )

    def test_has_role(self, agent):
        stem, content, _ = agent
        assert "<role>" in content, f"{stem}: missing <role> section"

    def test_has_mission(self, agent):
        stem, content, _ = agent
        mission = extract_xml_content(content, "mission")
        assert mission, f"{stem}: missing or empty <mission>"

    def test_has_mindset(self, agent):
        stem, content, _ = agent
        mindset = extract_xml_content(content, "mindset")
        assert mindset, f"{stem}: missing or empty <mindset>"

    def test_has_tool_guidance(self, agent):
        stem, content, _ = agent
        assert "<tool_guidance" in content, (
            f"{stem}: missing <tool_guidance> section"
        )

    def test_has_bounds(self, agent):
        stem, content, _ = agent
        assert "<bounds " in content, f"{stem}: missing <bounds> tag"


class TestAgentCrossFieldConsistency:
    """Validate that frontmatter and XML body are consistent."""

    def test_triggers_in_description(self, agent):
        """Frontmatter description should mention triggers."""
        stem, content, fm = agent
        desc = fm.get("description", "")
        assert "triggers" in desc.lower() or "trigger" in desc.lower(), (
            f"{stem}: description should include trigger keywords"
        )

    def test_autonomy_matches_tool_guidance(self, agent):
        """Frontmatter autonomy should match tool_guidance autonomy attr."""
        stem, content, fm = agent
        fm_level = fm.get("autonomy", "")
        xml_level = extract_xml_attr(content, "tool_guidance", "autonomy")
        assert xml_level, f"{stem}: tool_guidance missing autonomy attribute"
        assert fm_level == xml_level, (
            f"{stem}: frontmatter autonomy '{fm_level}' != "
            f"tool_guidance autonomy '{xml_level}'"
        )

    def test_mission_appears_in_description(self, agent):
        """Mission text should be reflected in the frontmatter description."""
        stem, content, fm = agent
        mission = extract_xml_content(content, "mission") or ""
        desc = fm.get("description", "")
        # Extract significant words (4+ chars) from mission
        stopwords = {"with", "that", "this", "from", "through", "about", "into"}
        mission_words = {
            w.lower()
            for w in re.findall(r"[a-zA-Z]{4,}", mission)
        } - stopwords
        desc_lower = desc.lower()
        matches = [w for w in mission_words if w in desc_lower]
        # At least 30% of significant mission words should appear in description
        threshold = max(1, len(mission_words) * 0.3)
        assert len(matches) >= threshold, (
            f"{stem}: description shares only {len(matches)}/{len(mission_words)} "
            f"words with mission (need {threshold:.0f}). "
            f"Missing: {mission_words - set(matches)}"
        )


class TestAgentMinimumContent:
    """Validate that agent files have sufficient content."""

    def test_minimum_length(self, agent):
        stem, content, _ = agent
        assert len(content) > 500, (
            f"{stem}: agent file too short ({len(content)} chars)"
        )

    def test_no_empty_sections(self, agent):
        """Check for self-closing or empty major sections."""
        stem, content, _ = agent
        empty_patterns = [
            r"<role>\s*</role>",
            r"<actions>\s*</actions>",
            r"<tool_guidance[^>]*>\s*</tool_guidance>",
        ]
        for pattern in empty_patterns:
            assert not re.search(pattern, content), (
                f"{stem}: empty section found matching {pattern}"
            )


class TestSimplicityGuideSpecific:
    """Targeted tests for the simplicity-guide agent."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = AGENTS_DIR / "simplicity-guide.md"
        self.content = path.read_text()
        self.fm = parse_frontmatter(self.content)

    def test_autonomy_is_low(self):
        assert self.fm["autonomy"] == "low"

    def test_has_osl_core_loop(self):
        """Orient-Step-Learn is the defining methodology."""
        assert "Orient-Step-Learn" in self.content

    def test_osl_phases_present(self):
        for phase in ("Orient:", "Step:", "Learn:"):
            assert phase in self.content, f"missing OSL phase: {phase}"

    def test_has_anti_patterns(self):
        assert "<anti_patterns" in self.content

    def test_has_osl_gate_in_checklist(self):
        """Checkpoints merged into checklist — OSL meta-check preserved."""
        assert "<checklist" in self.content
        assert "simplicity" in self.content.lower()

    def test_has_differentiation(self):
        """Should distinguish itself from adjacent agents."""
        assert "<differentiation" in self.content

    def test_has_examples(self):
        assert "<examples>" in self.content

    def test_has_checklist(self):
        assert "<checklist" in self.content

    def test_dave_thomas_attribution(self):
        assert "Dave Thomas" in self.content

    def test_triggers_include_key_terms(self):
        triggers = extract_xml_content(self.content, "triggers") or ""
        for term in ("simplicity", "yagni", "over-engineering"):
            assert term in triggers, f"missing trigger: {term}"

    def test_mcp_servers_declared(self):
        assert "<mcp " in self.content
        servers = extract_xml_attr(self.content, "mcp", "servers") or ""
        assert "serena" in servers
