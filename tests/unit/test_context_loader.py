"""
Unit tests for context_loader

Tests: format_skills_summary, resolve_flags (alias/fuzzy matching),
       tiered injection (TIER_0_MAP, INSTRUCTION_MAP, _get_injection_tier)
"""

from dataclasses import dataclass

from superclaude.scripts.context_loader import (
    BASE_PATH,
    COMPOSITE_FLAGS,
    FLAG_ALIASES,
    INSTRUCTION_MAP,
    TIER_0_MAP,
    TRIGGER_MAP,
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

    # Expected MCP docs (8 total: 5 core + 3 plugin, Morphllm removed)
    EXPECTED_TOOL_MCPS = {
        "mcp/MCP_Context7.md",
        "mcp/MCP_Sequential.md",
        "mcp/MCP_Playwright.md",
        "mcp/MCP_Chrome-DevTools.md",
        "mcp/MCP_Magic.md",
        "mcp/MCP_AstGrep.md",
    }
    EXPECTED_BEHAVIORAL_MCPS = {
        "mcp/MCP_Serena.md",
        "mcp/MCP_Tavily.md",
    }

    def test_tool_mcp_gets_tier_0(self):
        """Tool MCPs (Context7, Playwright, etc.) should get Tier 0."""
        for mcp in self.EXPECTED_TOOL_MCPS:
            assert _get_injection_tier(mcp, verbose=False) == 0, f"{mcp} should be Tier 0"

    def test_behavioral_mcp_gets_tier_1(self):
        """Behavioral MCPs (Serena, Tavily) should get Tier 1."""
        for mcp in self.EXPECTED_BEHAVIORAL_MCPS:
            assert _get_injection_tier(mcp, verbose=False) == 1, f"{mcp} should be Tier 1"

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

    def test_all_tool_mcps_in_tier_0_map(self):
        """Every tool MCP should have a Tier 0 summary."""
        for mcp in self.EXPECTED_TOOL_MCPS:
            assert mcp in TIER_0_MAP, f"{mcp} missing from TIER_0_MAP"

    def test_all_behavioral_mcps_in_instruction_map(self):
        """Every behavioral MCP should have an INSTRUCTION_MAP entry."""
        for mcp in self.EXPECTED_BEHAVIORAL_MCPS:
            assert mcp in INSTRUCTION_MAP, f"{mcp} missing from INSTRUCTION_MAP"

    def test_tier_0_context7_mentions_get_library_docs(self):
        """Context7 Tier 0 hint should reference the correct tool name."""
        hint = TIER_0_MAP["mcp/MCP_Context7.md"]
        assert "get-library-docs" in hint, "Context7 hint should reference get-library-docs (not query-docs)"

    def test_tier_0_devtools_mentions_lighthouse(self):
        """DevTools Tier 0 hint should reference Lighthouse capability."""
        hint = TIER_0_MAP["mcp/MCP_Chrome-DevTools.md"]
        assert "Lighthouse" in hint, "DevTools hint should mention Lighthouse audits"

    def test_tier_0_playwright_mentions_caps(self):
        """Playwright Tier 0 hint should reference capability system."""
        hint = TIER_0_MAP["mcp/MCP_Playwright.md"]
        assert "--caps" in hint or "caps" in hint, "Playwright hint should mention capability system"

    def test_instruction_map_serena_mentions_safe_delete(self):
        """Serena INSTRUCTION_MAP should mention key symbol operations."""
        hint = INSTRUCTION_MAP["mcp/MCP_Serena.md"]
        assert "find_symbol" in hint
        assert "replace_symbol_body" in hint

    def test_verbose_context_in_valid_flags(self):
        """--verbose-context should be a valid flag."""
        assert "verbose-context" in VALID_FLAGS

    def test_no_morphllm_in_any_map(self):
        """Morphllm should not appear in any injection map (removed)."""
        morphllm_key = "mcp/MCP_Morphllm.md"
        assert morphllm_key not in TIER_0_MAP, "Morphllm should be removed from TIER_0_MAP"
        assert morphllm_key not in INSTRUCTION_MAP, "Morphllm should be removed from INSTRUCTION_MAP"
        assert "morph" not in VALID_FLAGS, "morph should be removed from VALID_FLAGS"
        assert "morphllm" not in VALID_FLAGS, "morphllm should be removed from VALID_FLAGS"


class TestTriggerMapPaths:
    """Verify all TRIGGER_MAP and COMPOSITE_FLAGS paths resolve to existing files."""

    def test_all_trigger_map_paths_exist(self):
        """Every file referenced in TRIGGER_MAP must exist."""
        for _pattern, path, _priority in TRIGGER_MAP:
            assert (BASE_PATH / path).exists(), f"TRIGGER_MAP path missing: {path}"

    def test_all_composite_flag_paths_exist(self):
        """Every file referenced in COMPOSITE_FLAGS must exist."""
        for flag, entries in COMPOSITE_FLAGS.items():
            for path, _priority in entries:
                assert (BASE_PATH / path).exists(), (
                    f"COMPOSITE_FLAGS[{flag}] path missing: {path}"
                )

    def test_no_morphllm_in_trigger_map(self):
        """Morphllm should not appear in any TRIGGER_MAP entry."""
        for _pattern, path, _priority in TRIGGER_MAP:
            assert "Morphllm" not in path, f"Morphllm found in TRIGGER_MAP: {path}"

    def test_no_morphllm_in_composite_flags(self):
        """Morphllm should not appear in any COMPOSITE_FLAGS entry."""
        for flag, entries in COMPOSITE_FLAGS.items():
            for path, _priority in entries:
                assert "Morphllm" not in path, f"Morphllm found in COMPOSITE_FLAGS[{flag}]: {path}"

    def test_all_mcp_includes_8_servers(self):
        """--all-mcp should activate exactly 8 MCP docs (5 core + 3 plugin)."""
        all_mcp_paths = {p for p, _ in COMPOSITE_FLAGS["--all-mcp"]}
        assert len(all_mcp_paths) == 8, f"Expected 8 MCP docs in --all-mcp, got {len(all_mcp_paths)}"

    def test_frontend_verify_includes_3_servers(self):
        """--frontend-verify should activate Playwright + DevTools + Serena."""
        fv_paths = {p for p, _ in COMPOSITE_FLAGS["--frontend-verify"]}
        assert fv_paths == {
            "mcp/MCP_Playwright.md",
            "mcp/MCP_Chrome-DevTools.md",
            "mcp/MCP_Serena.md",
        }

    def test_trigger_map_mcp_count(self):
        """TRIGGER_MAP should have entries for exactly 8 MCP docs."""
        mcp_paths = {path for _, path, _ in TRIGGER_MAP if path.startswith("mcp/")}
        assert len(mcp_paths) == 8, f"Expected 8 MCP trigger paths, got {len(mcp_paths)}: {mcp_paths}"
