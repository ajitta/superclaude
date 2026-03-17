"""
Structural validation tests for command markdown files.

Validates frontmatter fields, XML structure, and cross-field consistency
for all command definitions in src/superclaude/commands/.
"""

import re
from pathlib import Path

import pytest

COMMANDS_DIR = Path(__file__).parent.parent.parent / "src" / "superclaude" / "commands"

# Agent/skill-only fields that should never appear in command frontmatter
FORBIDDEN_FIELDS = {
    "name", "model", "permissionMode", "memory",
    "color", "autonomy", "context", "agent", "hooks",
}

# All command .md files (excluding README and __init__.py)
COMMAND_FILES = sorted(
    [f for f in COMMANDS_DIR.glob("*.md") if f.name not in ("README.md", "__init__.py")]
)
COMMAND_IDS = [f.stem for f in COMMAND_FILES]


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


@pytest.fixture(params=COMMAND_FILES, ids=COMMAND_IDS)
def command(request) -> tuple[str, str, dict[str, str]]:
    """Yield (stem, content, frontmatter) for each command file."""
    path: Path = request.param
    content = path.read_text()
    fm = parse_frontmatter(content)
    return path.stem, content, fm


class TestCommandFrontmatter:
    """Validate YAML frontmatter in every command file."""

    def test_has_frontmatter(self, command):
        stem, content, fm = command
        assert fm, f"{stem}: missing YAML frontmatter (--- block)"

    def test_has_description(self, command):
        stem, content, fm = command
        assert "description" in fm, f"{stem}: frontmatter missing 'description'"
        assert len(fm["description"]) > 10, f"{stem}: description too short"

    def test_no_forbidden_fields(self, command):
        """Commands should not contain agent/skill-only fields."""
        stem, content, fm = command
        found = set(fm.keys()) & FORBIDDEN_FIELDS
        assert not found, (
            f"{stem}: frontmatter contains forbidden field(s): {found}"
        )


class TestCommandXMLStructure:
    """Validate XML component structure in every command file."""

    def test_has_component_open(self, command):
        stem, content, _ = command
        assert "<component" in content, f"{stem}: missing <component> tag"

    def test_has_component_close(self, command):
        stem, content, _ = command
        assert "</component>" in content, f"{stem}: missing </component>"

    def test_component_name_matches(self, command):
        stem, content, _ = command
        name = extract_xml_attr(content, "component", "name")
        assert name == stem, (
            f"{stem}: component name='{name}' != filename '{stem}'"
        )

    def test_component_type_is_command(self, command):
        stem, content, _ = command
        ctype = extract_xml_attr(content, "component", "type")
        assert ctype == "command", (
            f"{stem}: component type='{ctype}', expected 'command'"
        )

    def test_has_role(self, command):
        stem, content, _ = command
        assert "<role>" in content, f"{stem}: missing <role> section"

    def test_has_mission(self, command):
        stem, content, _ = command
        mission = extract_xml_content(content, "mission")
        assert mission, f"{stem}: missing or empty <mission>"


class TestCommandCrossFieldConsistency:
    """Validate that frontmatter and XML body are consistent."""

    def test_mission_matches_description(self, command):
        """Mission text should share 30%+ significant words with description."""
        stem, content, fm = command
        mission = extract_xml_content(content, "mission") or ""
        desc = fm.get("description", "")
        stopwords = {"with", "that", "this", "from", "through", "about", "into"}
        mission_words = {
            w.lower()
            for w in re.findall(r"[a-zA-Z]{4,}", mission)
        } - stopwords
        desc_lower = desc.lower()
        matches = [w for w in mission_words if w in desc_lower]
        threshold = max(1, len(mission_words) * 0.3)
        assert len(matches) >= threshold, (
            f"{stem}: description shares only {len(matches)}/{len(mission_words)} "
            f"words with mission (need {threshold:.0f}). "
            f"Missing: {mission_words - set(matches)}"
        )

    def test_has_bounds(self, command):
        stem, content, _ = command
        assert "<bounds " in content, f"{stem}: missing <bounds> tag"

    def test_has_handoff(self, command):
        stem, content, _ = command
        assert "<handoff " in content, f"{stem}: missing <handoff> tag"


class TestCommandMinimumContent:
    """Validate that command files have sufficient content."""

    def test_minimum_length(self, command):
        stem, content, _ = command
        assert len(content) > 300, (
            f"{stem}: command file too short ({len(content)} chars)"
        )

    def test_no_empty_sections(self, command):
        """Check for empty major sections."""
        stem, content, _ = command
        empty_patterns = [
            r"<role>\s*</role>",
            r"<flow>\s*</flow>",
        ]
        for pattern in empty_patterns:
            assert not re.search(pattern, content), (
                f"{stem}: empty section found matching {pattern}"
            )
