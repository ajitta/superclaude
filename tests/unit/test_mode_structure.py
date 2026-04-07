"""
Structural validation tests for mode markdown files.

Validates the 4-axis structure (thinking/communication/priorities/behaviors)
and XML conventions for all mode definitions in src/superclaude/modes/.
"""

import re
from pathlib import Path

import pytest

MODES_DIR = Path(__file__).parent.parent.parent / "src" / "superclaude" / "modes"

# Mode files: MODE_*.md (excludes RESEARCH_CONFIG.md which is type="config")
MODE_FILES = sorted(MODES_DIR.glob("MODE_*.md"))
MODE_IDS = [f.stem for f in MODE_FILES]


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


@pytest.fixture(params=MODE_FILES, ids=MODE_IDS)
def mode(request) -> tuple[str, str]:
    """Yield (stem, content) for each mode file."""
    path: Path = request.param
    return path.stem, path.read_text()


class TestModeComponentStructure:
    """Validate XML component structure in every mode file."""

    def test_has_component_type_mode(self, mode):
        stem, content = mode
        ctype = extract_xml_attr(content, "component", "type")
        assert ctype == "mode", (
            f"{stem}: component type='{ctype}', expected 'mode'"
        )

    def test_has_role_and_mission(self, mode):
        stem, content = mode
        assert "<role>" in content, f"{stem}: missing <role> section"
        mission = extract_xml_content(content, "mission")
        assert mission, f"{stem}: missing or empty <mission>"

    def test_mission_is_descriptive(self, mode):
        stem, content = mode
        mission = extract_xml_content(content, "mission") or ""
        assert len(mission) > 10, (
            f"{stem}: mission too short ({len(mission)} chars), "
            "should describe the cognitive posture"
        )


class TestModeFourAxes:
    """Validate the 4-axis structure: thinking, communication, priorities, behaviors."""

    def test_has_thinking(self, mode):
        stem, content = mode
        thinking = extract_xml_content(content, "thinking")
        assert thinking, f"{stem}: missing or empty <thinking> axis"

    def test_has_communication(self, mode):
        stem, content = mode
        communication = extract_xml_content(content, "communication")
        assert communication, f"{stem}: missing or empty <communication> axis"

    def test_has_priorities(self, mode):
        stem, content = mode
        priorities = extract_xml_content(content, "priorities")
        assert priorities, f"{stem}: missing or empty <priorities> axis"

    def test_has_behaviors(self, mode):
        stem, content = mode
        behaviors = extract_xml_content(content, "behaviors")
        assert behaviors, f"{stem}: missing or empty <behaviors> axis"


class TestModeBoundary:
    """Validate bounds and handoff in every mode file."""

    def test_has_bounds(self, mode):
        stem, content = mode
        assert "<bounds " in content, f"{stem}: missing <bounds> tag"
        should_attr = extract_xml_attr(content, "bounds", "should")
        avoid_attr = extract_xml_attr(content, "bounds", "avoid")
        assert should_attr, f"{stem}: <bounds> missing 'should' attribute"
        assert avoid_attr, f"{stem}: <bounds> missing 'avoid' attribute"

    def test_has_handoff(self, mode):
        stem, content = mode
        assert "<handoff " in content, f"{stem}: missing <handoff> tag"
        next_attr = extract_xml_attr(content, "handoff", "next")
        assert next_attr, f"{stem}: <handoff> missing 'next' attribute"


class TestModeConventions:
    """Validate mode file conventions."""

    def test_no_frontmatter(self, mode):
        """Modes should not have YAML frontmatter."""
        stem, content = mode
        assert not content.startswith("---"), (
            f"{stem}: modes should not have YAML frontmatter"
        )

    def test_minimum_content(self, mode):
        stem, content = mode
        assert len(content) > 300, (
            f"{stem}: mode file too short ({len(content)} chars)"
        )

    def test_no_empty_axes(self, mode):
        """Check for self-closing or empty axis sections."""
        stem, content = mode
        empty_patterns = [
            r"<thinking>\s*</thinking>",
            r"<communication>\s*</communication>",
            r"<priorities>\s*</priorities>",
            r"<behaviors>\s*</behaviors>",
        ]
        for pattern in empty_patterns:
            assert not re.search(pattern, content), (
                f"{stem}: empty axis found matching {pattern}"
            )
