"""
Unit tests for context_injection.format_skills_summary

Tests the compact single-line skill summary format.
"""

from dataclasses import dataclass

from superclaude.scripts.context_injection import format_skills_summary


@dataclass
class FakeTokenEstimate:
    """Minimal stand-in for TokenEstimate."""

    name: str
    frontmatter_tokens: int
    full_tokens: int


class TestFormatSkillsSummary:
    """Test format_skills_summary output format."""

    def test_empty_skills_returns_empty_string(self):
        assert format_skills_summary([]) == ""

    def test_single_skill_format(self):
        skills = [FakeTokenEstimate("confidence-check", 103, 2500)]
        result = format_skills_summary(skills)
        assert result == "<!-- 1 skills installed (confidence-check). ~2500 tokens full load. Use /sc:help for details. -->"

    def test_multiple_skills_format(self):
        skills = [
            FakeTokenEstimate("confidence-check", 103, 2500),
            FakeTokenEstimate("ship", 80, 1800),
            FakeTokenEstimate("simplicity-coach", 90, 3429),
        ]
        result = format_skills_summary(skills)
        assert result == "<!-- 3 skills installed (confidence-check, ship, simplicity-coach). ~7729 tokens full load. Use /sc:help for details. -->"

    def test_output_is_single_line(self):
        skills = [
            FakeTokenEstimate("a", 10, 100),
            FakeTokenEstimate("b", 20, 200),
        ]
        result = format_skills_summary(skills)
        assert "\n" not in result

    def test_output_is_html_comment(self):
        skills = [FakeTokenEstimate("test", 10, 100)]
        result = format_skills_summary(skills)
        assert result.startswith("<!--")
        assert result.endswith("-->")
