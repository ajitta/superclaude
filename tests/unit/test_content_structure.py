"""
Structural validation tests for mode and MCP documentation markdown files.

Validates XML structure consistency for all mode and MCP definitions.
"""

import re
from pathlib import Path

import pytest

MODES_DIR = Path(__file__).parent.parent.parent / "src" / "superclaude" / "modes"
MCP_DIR = Path(__file__).parent.parent.parent / "src" / "superclaude" / "mcp"

# Mode files: MODE_*.md
MODE_FILES = sorted(MODES_DIR.glob("MODE_*.md"))
MODE_IDS = [f.stem for f in MODE_FILES]

# MCP files: MCP_*.md
MCP_FILES = sorted(MCP_DIR.glob("MCP_*.md"))
MCP_IDS = [f.stem for f in MCP_FILES]


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


# --- Mode Tests ---


@pytest.fixture(params=MODE_FILES, ids=MODE_IDS)
def mode(request) -> tuple[str, str]:
    """Yield (stem, content) for each mode file."""
    path: Path = request.param
    return path.stem, path.read_text()


class TestModeXMLStructure:
    """Validate XML component structure in every mode file."""

    def test_has_component(self, mode):
        stem, content = mode
        assert "<component" in content, f"{stem}: missing <component> tag"
        assert "</component>" in content, f"{stem}: missing </component>"

    def test_component_type_is_mode(self, mode):
        stem, content = mode
        ctype = extract_xml_attr(content, "component", "type")
        assert ctype == "mode", (
            f"{stem}: component type='{ctype}', expected 'mode'"
        )

    def test_has_role(self, mode):
        stem, content = mode
        assert "<role>" in content, f"{stem}: missing <role> section"

    def test_has_mission(self, mode):
        stem, content = mode
        mission = extract_xml_content(content, "mission")
        assert mission, f"{stem}: missing or empty <mission>"

    def test_has_bounds(self, mode):
        stem, content = mode
        assert "<bounds " in content, f"{stem}: missing <bounds> tag"

    def test_has_handoff(self, mode):
        stem, content = mode
        assert "<handoff " in content, f"{stem}: missing <handoff> tag"

    def test_no_frontmatter(self, mode):
        """Modes should not have YAML frontmatter."""
        stem, content = mode
        assert not content.startswith("---"), (
            f"{stem}: modes should not have YAML frontmatter"
        )


# --- MCP Tests ---


@pytest.fixture(params=MCP_FILES, ids=MCP_IDS)
def mcp(request) -> tuple[str, str]:
    """Yield (stem, content) for each MCP file."""
    path: Path = request.param
    return path.stem, path.read_text()


class TestMcpXMLStructure:
    """Validate XML component structure in every MCP documentation file."""

    def test_has_component(self, mcp):
        stem, content = mcp
        assert "<component" in content, f"{stem}: missing <component> tag"
        assert "</component>" in content, f"{stem}: missing </component>"

    def test_component_type_is_mcp(self, mcp):
        stem, content = mcp
        ctype = extract_xml_attr(content, "component", "type")
        assert ctype == "mcp", (
            f"{stem}: component type='{ctype}', expected 'mcp'"
        )

    def test_has_role(self, mcp):
        stem, content = mcp
        assert "<role>" in content, f"{stem}: missing <role> section"

    def test_has_mission(self, mcp):
        stem, content = mcp
        mission = extract_xml_content(content, "mission")
        assert mission, f"{stem}: missing or empty <mission>"

    def test_has_bounds(self, mcp):
        stem, content = mcp
        assert "<bounds " in content, f"{stem}: missing <bounds> tag"

    def test_has_handoff(self, mcp):
        stem, content = mcp
        assert "<handoff " in content, f"{stem}: missing <handoff> tag"

    def test_no_frontmatter(self, mcp):
        """MCP docs should not have YAML frontmatter."""
        stem, content = mcp
        assert not content.startswith("---"), (
            f"{stem}: MCP docs should not have YAML frontmatter"
        )
