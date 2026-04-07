"""
Structural validation tests for agent markdown files.

Validates frontmatter fields, XML structure, and cross-field consistency
for all agent definitions in src/superclaude/agents/.
"""

import re
from pathlib import Path

import pytest

AGENTS_DIR = Path(__file__).parent.parent.parent / "src" / "superclaude" / "agents"

VALID_PERMISSION_MODES = {"acceptEdits", "default", "plan", "auto", "dontAsk", "bypassPermissions"}
VALID_MEMORY_SCOPES = {"user", "project", "local"}
VALID_COLORS = {"blue", "green", "orange", "purple", "yellow", "cyan", "red"}
VALID_EFFORT_VALUES = {"low", "medium", "high", "max"}
SKILLS_DIR = Path(__file__).parent.parent.parent / "src" / "superclaude" / "skills"
# All agent .md files (excluding README and _ prefixed test agents)
AGENT_FILES = sorted(
    [f for f in AGENTS_DIR.glob("*.md")
     if f.name != "README.md" and not f.name.startswith("_")]
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

    def test_permission_mode_valid_if_present(self, agent):
        """If permissionMode is set, it must be a valid value."""
        stem, content, fm = agent
        if "permissionMode" not in fm:
            return
        mode = fm.get("permissionMode", "")
        assert mode in VALID_PERMISSION_MODES, (
            f"{stem}: permissionMode '{mode}' not in {VALID_PERMISSION_MODES}"
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

    def test_has_color(self, agent):
        stem, content, fm = agent
        assert "color" in fm, f"{stem}: frontmatter missing 'color'"

    def test_color_valid(self, agent):
        stem, content, fm = agent
        color = fm.get("color", "")
        assert color in VALID_COLORS, (
            f"{stem}: color '{color}' not in {VALID_COLORS}"
        )

    def test_no_autonomy_field(self, agent):
        """autonomy is not an official Claude Code field — should not be in frontmatter."""
        stem, content, fm = agent
        assert "autonomy" not in fm, (
            f"{stem}: frontmatter contains non-official 'autonomy' field"
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
        should_attr = extract_xml_attr(content, "bounds", "should")
        avoid_attr = extract_xml_attr(content, "bounds", "avoid")
        assert should_attr, f"{stem}: <bounds> missing 'should' attribute"
        assert avoid_attr, f"{stem}: <bounds> missing 'avoid' attribute"


class TestAgentCrossFieldConsistency:
    """Validate that frontmatter and XML body are consistent."""

    def test_tool_guidance_has_content(self, agent):
        """tool_guidance should contain Proceed/Ask First/Never behavioral rules."""
        stem, content, _ = agent
        tg = extract_xml_content(content, "tool_guidance")
        assert tg, f"{stem}: tool_guidance is empty"
        assert "Proceed" in tg or "Ask First" in tg or "Never" in tg, (
            f"{stem}: tool_guidance missing behavioral rules (Proceed/Ask First/Never)"
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


class TestAgentMemoryGuide:
    """Validate <memory_guide> section in every agent file."""

    def test_has_memory_guide(self, agent):
        stem, content, _ = agent
        assert "<memory_guide>" in content, (
            f"{stem}: missing <memory_guide> section"
        )

    def test_memory_guide_has_categories(self, agent):
        stem, content, _ = agent
        mg = extract_xml_content(content, "memory_guide")
        assert mg, f"{stem}: <memory_guide> is empty"
        categories = [line.strip() for line in mg.splitlines()
                      if line.strip().startswith("- ")]
        assert len(categories) >= 2, (
            f"{stem}: memory_guide has {len(categories)} categories, need >= 2"
        )

    def test_memory_guide_has_refs(self, agent):
        stem, content, _ = agent
        mg = extract_xml_content(content, "memory_guide") or ""
        assert '<refs agents="' in mg, (
            f"{stem}: memory_guide missing <refs agents=\"...\"/>"
        )

    def test_memory_guide_refs_valid(self, agent):
        stem, content, _ = agent
        mg = extract_xml_content(content, "memory_guide") or ""
        match = re.search(r'<refs agents="([^"]+)"', mg)
        if match:
            refs = [r.strip() for r in match.group(1).split(",")]
            for ref in refs:
                assert ref in AGENT_IDS, (
                    f"{stem}: memory_guide refs unknown agent '{ref}'"
                )


class TestSimplicityGuideSpecific:
    """Targeted tests for the simplicity-guide agent."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = AGENTS_DIR / "simplicity-guide.md"
        self.content = path.read_text()
        self.fm = parse_frontmatter(self.content)

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



class TestAgentOptionalFields:
    """Validate optional CC-native fields when present (effort, maxTurns, tools, skills)."""

    def test_effort_valid_if_present(self, agent):
        """If effort is set, it must be 1-5."""
        stem, content, fm = agent
        if "effort" in fm:
            assert fm["effort"] in VALID_EFFORT_VALUES, (
                f"{stem}: effort '{fm['effort']}' not in {VALID_EFFORT_VALUES}"
            )

    def test_max_turns_valid_if_present(self, agent):
        """If maxTurns is set, it must be a positive integer."""
        stem, content, fm = agent
        if "maxTurns" in fm:
            val = fm["maxTurns"]
            assert val.isdigit() and int(val) > 0, (
                f"{stem}: maxTurns '{val}' must be a positive integer"
            )

    def test_tools_and_disallowed_mutually_exclusive(self, agent):
        """tools (allow-list) and disallowedTools (deny-list) must not coexist."""
        stem, content, fm = agent
        has_tools = "tools" in fm
        has_disallowed = "disallowedTools" in fm
        assert not (has_tools and has_disallowed), (
            f"{stem}: has both 'tools' and 'disallowedTools' — pick one"
        )

    def test_skills_reference_existing_dirs(self, agent):
        """If skills are declared, each must exist as a skill directory."""
        stem, content, fm = agent
        if "skills" not in fm:
            return
        # Parse skill names from raw frontmatter (YAML list items)
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            return
        fm_text = fm_match.group(1)
        in_skills = False
        skill_names = []
        for line in fm_text.splitlines():
            if line.startswith("skills:"):
                in_skills = True
                continue
            if in_skills:
                stripped = line.strip()
                if stripped.startswith("- "):
                    skill_names.append(stripped[2:].strip())
                else:
                    break
        existing_skills = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}
        for skill in skill_names:
            assert skill in existing_skills, (
                f"{stem}: skills references '{skill}' but no such skill dir exists"
            )
