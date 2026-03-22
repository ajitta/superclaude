"""
Unit tests for context_loader

Tests: format_skills_summary, resolve_flags (alias/fuzzy matching),
       tiered injection (TIER_0_MAP, INSTRUCTION_MAP, _get_injection_tier)
"""

from dataclasses import dataclass

from superclaude.scripts.context_loader import (
    FLAG_ALIASES,
    INSTRUCTION_MAP,
    TIER_0_MAP,
    VALID_FLAGS,
    _BEHAVIORAL_MCPS,
    _get_injection_tier,
    format_skills_summary,
    resolve_flags,
)


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


class TestResolveFlags:
    """Test flag alias resolution and fuzzy matching."""

    # --- Alias resolution ---

    def test_alias_ultrathink_resolves_to_seq(self):
        prompt, notes = resolve_flags("analyze code --ultrathink")
        assert "--seq" in prompt
        assert "--ultrathink" not in prompt
        assert len(notes) == 1
        assert "auto-corrected" in notes[0]

    def test_alias_parellel_resolves_to_delegate(self):
        prompt, notes = resolve_flags("run tasks --parellel")
        assert "--delegate" in prompt
        assert "--parellel" not in prompt
        assert "auto-corrected" in notes[0]

    def test_alias_conccurrency_resolves_to_concurrency(self):
        prompt, notes = resolve_flags("fast run --conccurrency 5")
        assert "--concurrency" in prompt
        assert "--conccurrency" not in prompt

    def test_alias_loo_resolves_to_loop(self):
        prompt, notes = resolve_flags("improve --loo")
        assert "--loop" in prompt

    def test_alias_sea_resolves_to_serena(self):
        prompt, notes = resolve_flags("explore --sea")
        assert "--serena" in prompt

    def test_alias_iteration_resolves_to_iterations(self):
        prompt, notes = resolve_flags("run --iteration 3")
        assert "--iterations" in prompt

    # --- Valid flags pass through unchanged ---

    def test_valid_flag_unchanged(self):
        prompt, notes = resolve_flags("analyze --seq --tavily --c7")
        assert prompt == "analyze --seq --tavily --c7"
        assert notes == []

    def test_no_flags_returns_unchanged(self):
        prompt, notes = resolve_flags("just a normal prompt")
        assert prompt == "just a normal prompt"
        assert notes == []

    # --- Fuzzy matching ---

    def test_fuzzy_suggests_close_match(self):
        prompt, notes = resolve_flags("run --seqq")
        # Should suggest --seq as a close match
        assert len(notes) == 1
        assert "not a recognized flag" in notes[0]
        assert "--seq" in notes[0]

    def test_totally_unknown_flag_no_suggestion(self):
        prompt, notes = resolve_flags("run --xyzzy123")
        # Too different from any valid flag — may or may not suggest
        # At minimum, prompt should be unchanged
        assert "--xyzzy123" in prompt

    # --- Multiple flags ---

    def test_multiple_aliases_resolved(self):
        prompt, notes = resolve_flags("go --ultrathink --parellel")
        assert "--seq" in prompt
        assert "--delegate" in prompt
        assert len(notes) == 2

    def test_mixed_valid_and_alias(self):
        prompt, notes = resolve_flags("run --seq --ultrathink --tavily")
        assert prompt.count("--seq") == 2  # original + alias resolution
        assert "--tavily" in prompt
        assert len(notes) == 1  # only ultrathink triggers notification

    # --- Edge cases ---

    def test_flag_with_value_preserved(self):
        prompt, notes = resolve_flags("run --concurrency 5 --seq")
        assert "--concurrency 5" in prompt
        assert notes == []

    def test_case_insensitive_flag_detection(self):
        """Flags in prompt are lowercased for matching."""
        prompt, notes = resolve_flags("run --Parellel")
        assert "--delegate" in prompt

    # --- Data integrity ---

    def test_all_alias_targets_are_valid(self):
        """Every alias must resolve to a valid flag."""
        for alias, targets in FLAG_ALIASES.items():
            for target in targets:
                assert target in VALID_FLAGS, (
                    f"Alias --{alias} maps to --{target} which is not in VALID_FLAGS"
                )

    def test_no_alias_is_also_valid(self):
        """No alias should shadow a valid flag."""
        for alias in FLAG_ALIASES:
            assert alias not in VALID_FLAGS, (
                f"--{alias} is in both FLAG_ALIASES and VALID_FLAGS"
            )


class TestTieredInjection:
    """Test 3-tier context injection system."""

    def test_tool_mcp_gets_tier_0(self):
        """Tool MCPs (Context7, Playwright, etc.) should get Tier 0."""
        assert _get_injection_tier("mcp/MCP_Context7.md", verbose=False) == 0
        assert _get_injection_tier("mcp/MCP_Playwright.md", verbose=False) == 0
        assert _get_injection_tier("mcp/MCP_Magic.md", verbose=False) == 0

    def test_behavioral_mcp_gets_tier_1(self):
        """Behavioral MCPs (Serena, Tavily) should get Tier 1."""
        assert _get_injection_tier("mcp/MCP_Serena.md", verbose=False) == 1
        assert _get_injection_tier("mcp/MCP_Tavily.md", verbose=False) == 1

    def test_mode_always_gets_tier_2(self):
        """Modes should always get Tier 2 (full .md)."""
        assert _get_injection_tier("modes/MODE_Brainstorming.md", verbose=False) == 2
        assert _get_injection_tier("modes/MODE_DeepResearch.md", verbose=False) == 2
        assert _get_injection_tier("modes/MODE_Token_Efficiency.md", verbose=False) == 2

    def test_verbose_context_forces_tier_2(self):
        """--verbose-context should force Tier 2 for everything."""
        assert _get_injection_tier("mcp/MCP_Context7.md", verbose=True) == 2
        assert _get_injection_tier("mcp/MCP_Serena.md", verbose=True) == 2
        assert _get_injection_tier("modes/MODE_Brainstorming.md", verbose=True) == 2

    def test_tier_0_and_instruction_map_no_conflicting_keys(self):
        """TIER_0_MAP and INSTRUCTION_MAP may share keys but should not
        both be applied — tier logic selects one or the other."""
        # Behavioral MCPs should be in INSTRUCTION_MAP but NOT in TIER_0_MAP
        for mcp in _BEHAVIORAL_MCPS:
            assert mcp in INSTRUCTION_MAP, f"{mcp} missing from INSTRUCTION_MAP"
            assert mcp not in TIER_0_MAP, f"{mcp} should NOT be in TIER_0_MAP"

    def test_all_tier_0_entries_are_concise(self):
        """Tier 0 entries should be 1-line summaries (< 100 chars)."""
        for key, value in TIER_0_MAP.items():
            assert len(value) < 100, (
                f"TIER_0_MAP[{key}] is {len(value)} chars — should be < 100"
            )

    def test_verbose_context_in_valid_flags(self):
        """--verbose-context should be a valid flag."""
        assert "verbose-context" in VALID_FLAGS
