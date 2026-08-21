"""
Unit tests for context_loader

Tests: format_skills_summary, resolve_flags (alias/fuzzy matching),
       tiered injection (TIER_0_MAP, INSTRUCTION_MAP, _get_injection_tier)
"""

import json
from dataclasses import dataclass
from pathlib import Path

from superclaude.scripts.context_loader import (
    _BEHAVIORAL_MCPS,
    BASE_PATH,
    COMPOSITE_FLAGS,
    FLAG_ALIASES,
    INSTRUCTION_MAP,
    TIER_0_MAP,
    TRIGGER_MAP,
    VALID_FLAGS,
    _extract_session_id,
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


class TestExtractSessionId:
    """_extract_session_id pulls the CC session id from hook stdin JSON."""

    def test_extracts_session_id(self):
        stdin = json.dumps({"session_id": "abc123", "prompt": "hello"})
        assert _extract_session_id(stdin) == "abc123"

    def test_missing_session_id_returns_none(self):
        assert _extract_session_id(json.dumps({"prompt": "hello"})) is None

    def test_invalid_json_returns_none(self):
        assert _extract_session_id("not json") is None

    def test_non_dict_json_returns_none(self):
        assert _extract_session_id(json.dumps(["a", "b"])) is None

    def test_empty_session_id_returns_none(self):
        assert _extract_session_id(json.dumps({"session_id": ""})) is None


class TestFormatSkillsSummary:
    """Test format_skills_summary output format."""

    def test_empty_skills_returns_empty_string(self):
        assert format_skills_summary([]) == ""

    def test_single_skill_format(self):
        skills = [FakeTokenEstimate("confidence-check", 103, 2500)]
        result = format_skills_summary(skills)
        assert (
            result
            == "<!-- 1 skills installed (confidence-check). ~2500 tokens full load. Use /sc:help for details. -->"
        )

    def test_multiple_skills_format(self):
        skills = [
            FakeTokenEstimate("confidence-check", 103, 2500),
            FakeTokenEstimate("ship", 80, 1800),
            FakeTokenEstimate("simplicity-coach", 90, 3429),
        ]
        result = format_skills_summary(skills)
        assert (
            result
            == "<!-- 3 skills installed (confidence-check, ship, simplicity-coach). ~7729 tokens full load. Use /sc:help for details. -->"
        )

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

    def test_flag_aliases_table_is_empty(self):
        """FLAG_ALIASES intentionally empty — canonical flag names only."""
        assert FLAG_ALIASES == {}

    def test_ultrathink_not_remapped(self):
        """ultrathink is a CC native deep-reasoning trigger, not an SC alias."""
        prompt, notes = resolve_flags("analyze code --ultrathink")
        assert "--ultrathink" in prompt
        assert "--seq" not in prompt
        assert notes == []

    def test_fast_not_remapped(self):
        """fast is a CC native fast-mode toggle, not an SC flag."""
        prompt, notes = resolve_flags("analyze code --fast")
        assert "--fast" in prompt
        assert notes == []

    def test_removed_alias_parallel_no_auto_remap(self):
        """--parallel removed as alias; prompt is not silently rewritten."""
        prompt, notes = resolve_flags("analyze code --parallel")
        assert "--parallel" in prompt  # preserved verbatim
        assert "--delegate" not in prompt  # no hidden remap
        # Fuzzy may or may not suggest; either way, no silent rewrite occurred

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

    def test_multiple_valid_flags_pass_through(self):
        prompt, notes = resolve_flags("go --vs --delegate --seq")
        assert prompt == "go --vs --delegate --seq"
        assert notes == []

    def test_mixed_valid_and_unknown(self):
        prompt, notes = resolve_flags("run --delegate --xyzbogus --tavily")
        assert "--delegate" in prompt
        assert "--tavily" in prompt
        assert "--xyzbogus" in prompt  # unknown flag preserved

    # --- Edge cases ---

    def test_flag_with_value_preserved(self):
        prompt, notes = resolve_flags("run --concurrency 5 --seq")
        assert "--concurrency 5" in prompt
        assert notes == []

    def test_case_insensitive_flag_detection(self):
        """Valid flags in prompt are lowercased for matching."""
        prompt, notes = resolve_flags("run --Delegate")
        # --Delegate matches VALID_FLAGS via lowercase → passes through unchanged
        assert "--Delegate" in prompt
        assert notes == []

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
    }
    EXPECTED_BEHAVIORAL_MCPS = {
        "mcp/MCP_Serena.md",
        "mcp/MCP_Tavily.md",
    }

    def test_tool_mcp_gets_tier_0(self):
        """Tool MCPs (Context7, Playwright, etc.) should get Tier 0."""
        for mcp in self.EXPECTED_TOOL_MCPS:
            assert _get_injection_tier(mcp, verbose=False) == 0, (
                f"{mcp} should be Tier 0"
            )

    def test_behavioral_mcp_gets_tier_1(self):
        """Behavioral MCPs (Serena, Tavily) should get Tier 1."""
        for mcp in self.EXPECTED_BEHAVIORAL_MCPS:
            assert _get_injection_tier(mcp, verbose=False) == 1, (
                f"{mcp} should be Tier 1"
            )

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

    def test_tier_0_context7_mentions_query_docs(self):
        """Context7 Tier 0 hint should reference the correct tool name."""
        hint = TIER_0_MAP["mcp/MCP_Context7.md"]
        assert "query-docs" in hint, (
            "Context7 hint should reference query-docs (tool renamed from get-library-docs)"
        )

    def test_tier_0_devtools_mentions_lighthouse(self):
        """DevTools Tier 0 hint should reference Lighthouse capability."""
        hint = TIER_0_MAP["mcp/MCP_Chrome-DevTools.md"]
        assert "Lighthouse" in hint, "DevTools hint should mention Lighthouse audits"

    def test_tier_0_playwright_mentions_caps(self):
        """Playwright Tier 0 hint should reference capability system."""
        hint = TIER_0_MAP["mcp/MCP_Playwright.md"]
        assert "--caps" in hint or "caps" in hint, (
            "Playwright hint should mention capability system"
        )

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
        assert morphllm_key not in TIER_0_MAP, (
            "Morphllm should be removed from TIER_0_MAP"
        )
        assert morphllm_key not in INSTRUCTION_MAP, (
            "Morphllm should be removed from INSTRUCTION_MAP"
        )
        assert "morph" not in VALID_FLAGS, "morph should be removed from VALID_FLAGS"
        assert "morphllm" not in VALID_FLAGS, (
            "morphllm should be removed from VALID_FLAGS"
        )


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
                assert "Morphllm" not in path, (
                    f"Morphllm found in COMPOSITE_FLAGS[{flag}]: {path}"
                )

    def test_all_mcp_includes_6_servers(self):
        """--all-mcp should activate exactly 6 MCP docs (4 core + 2 plugin)."""
        all_mcp_paths = {p for p, _ in COMPOSITE_FLAGS["--all-mcp"]}
        assert len(all_mcp_paths) == 6, (
            f"Expected 6 MCP docs in --all-mcp, got {len(all_mcp_paths)}"
        )

    def test_frontend_verify_includes_3_servers(self):
        """--frontend-verify should activate Playwright + DevTools + Serena."""
        fv_paths = {p for p, _ in COMPOSITE_FLAGS["--frontend-verify"]}
        assert fv_paths == {
            "mcp/MCP_Playwright.md",
            "mcp/MCP_Chrome-DevTools.md",
            "mcp/MCP_Serena.md",
        }

    def test_trigger_map_mcp_count(self):
        """TRIGGER_MAP should have entries for exactly 6 MCP docs."""
        mcp_paths = {path for _, path, _ in TRIGGER_MAP if path.startswith("mcp/")}
        assert len(mcp_paths) == 6, (
            f"Expected 6 MCP trigger paths, got {len(mcp_paths)}: {mcp_paths}"
        )


class TestCoreLiteSplit:
    """Drift guards for the Phase 2-1 core-lite split: kernel token budget,
    module routing coverage, and full-injection tier of rule modules."""

    KERNEL_CHAR_BUDGET = 7600  # ~2k tokens at chars/3.8 — roadmap 2-1 ceiling

    SRC_CORE = Path(__file__).resolve().parents[2] / "src" / "superclaude" / "core"

    def _modules(self):
        return {
            f"core/rules/{p.name}"
            for p in (self.SRC_CORE / "rules").glob("*.md")
            if p.stem.upper() != "README"
        }

    def test_kernel_stays_within_token_budget(self):
        kernel = (self.SRC_CORE / "RULES.md").read_text(encoding="utf-8")
        assert len(kernel) <= self.KERNEL_CHAR_BUDGET, (
            f"RULES.md kernel {len(kernel)} chars exceeds {self.KERNEL_CHAR_BUDGET} "
            "(~2k tokens) — move detail into core/rules/ modules instead"
        )

    def test_every_rule_module_is_routed_by_trigger_map(self):
        routed = {
            path for _p, path, _pr in TRIGGER_MAP if path.startswith("core/rules/")
        }
        assert self._modules() == routed, (
            "core/rules/ modules and TRIGGER_MAP routing out of sync"
        )

    def test_rule_modules_inject_full_md(self):
        """Rule modules carry behavioral content — must stay Tier 2 (full .md),
        never silently downgraded to instruction-string tiers."""
        for path in self._modules():
            assert _get_injection_tier(path, verbose=False) == 2, (
                f"{path} not Tier 2 — remove it from INSTRUCTION_MAP/TIER_0_MAP"
            )

    def test_kernel_module_map_lists_every_module(self):
        """Kernel's on_demand_modules table is the discovery surface for
        explicit Reads — every shipped module must be listed."""
        kernel = (self.SRC_CORE / "RULES.md").read_text(encoding="utf-8")
        for module in self._modules():
            assert module in kernel, f"kernel module map missing {module}"


LOADER_SCRIPT = (
    Path(__file__).parent.parent.parent
    / "src"
    / "superclaude"
    / "scripts"
    / "context_loader.py"
)
CONTENT_ROOT = Path(__file__).parent.parent.parent / "src" / "superclaude"


def run_loader(
    prompt: str,
    project_dir: Path,
    session_id: str | None = None,
) -> str:
    """Invoke context_loader.py as Claude Code does; return its stdout.

    ``SUPERCLAUDE_PATH`` pins the content root so injection does not depend on
    what happens to be installed on the machine running the suite, and the
    ``.claude/superclaude`` marker under ``project_dir`` keeps ``claude_base()``
    — and therefore all hook state — inside the sandbox.
    """
    import os
    import subprocess
    import sys

    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    env["SUPERCLAUDE_PATH"] = str(CONTENT_ROOT)
    env["CLAUDE_SHOW_SKILLS"] = "0"
    payload: dict[str, str] = {"prompt": prompt}
    if session_id is not None:
        payload["session_id"] = session_id

    result = subprocess.run(
        [sys.executable, str(LOADER_SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"loader crashed: {result.stderr}"
    return result.stdout


class TestSessionScopedCache:
    """The dedup cache is per (project, session), not per project.

    Two Claude Code windows open on one repository are two sessions. Keying the
    cache on the project alone means the first one to trigger a context marks it
    loaded for both, and the second is silently starved (A3).
    """

    PROMPT = "analyze this --seq"

    @staticmethod
    def _project(tmp_path: Path) -> Path:
        (tmp_path / ".claude" / "superclaude").mkdir(parents=True, exist_ok=True)
        return tmp_path

    def _state_dir(self, project: Path) -> Path:
        return project / ".claude" / ".superclaude_hooks"

    def test_second_session_still_gets_context(self, tmp_path: Path):
        """Two sessions, one prompt: both must be injected into."""
        project = self._project(tmp_path)

        first = run_loader(self.PROMPT, project, session_id="session-A")
        second = run_loader(self.PROMPT, project, session_id="session-B")

        assert first.strip(), "session A received no injection"
        assert second.strip(), (
            "session B received no injection — the dedup cache is shared across "
            "sessions instead of being keyed to one"
        )

    def test_same_session_still_dedupes(self, tmp_path: Path):
        """Session keying must not cost the within-session dedup."""
        project = self._project(tmp_path)

        first = run_loader(self.PROMPT, project, session_id="session-A")
        repeat = run_loader(self.PROMPT, project, session_id="session-A")

        assert first.strip(), "first prompt of the session received no injection"
        assert not repeat.strip(), "the same context was injected twice in one session"

    def test_cache_file_is_named_for_the_session(self, tmp_path: Path):
        """The filename carries both keys, so the two sessions cannot collide."""
        project = self._project(tmp_path)

        run_loader(self.PROMPT, project, session_id="session-A")
        run_loader(self.PROMPT, project, session_id="session-B")

        names = sorted(
            p.name for p in self._state_dir(project).glob("claude_context_*")
        )
        assert len(names) == 2, f"expected one cache file per session, got {names}"
        assert all(n.endswith(("_session-A.txt", "_session-B.txt")) for n in names), (
            names
        )

    def test_missing_session_id_falls_back_to_project_key(self, tmp_path: Path):
        """Stdin without a session id still dedupes, under the project-only name."""
        from superclaude.utils import project_key

        project = self._project(tmp_path)

        first = run_loader(self.PROMPT, project)
        repeat = run_loader(self.PROMPT, project)

        assert first.strip(), "first prompt received no injection"
        assert not repeat.strip(), "fallback path lost its dedup"

        import os

        os.environ["CLAUDE_PROJECT_DIR"] = str(project)
        try:
            expected = f"claude_context_{project_key()}.txt"
        finally:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        assert (self._state_dir(project) / expected).exists()


class TestCommandNameResolution:
    """A mistyped or retired /sc: name must say so, not look like a real command.

    24 misspelled invocations and 25 uses of /sc:workflow — renamed to roadmap
    with no alias left behind — resolved to nothing and were answered in silence,
    while the loader still injected command context for them. A nonexistent
    command looked to the model exactly like a real one (A7c).
    """

    @staticmethod
    def _project(tmp_path: Path) -> Path:
        (tmp_path / ".claude" / "superclaude").mkdir(parents=True, exist_ok=True)
        return tmp_path

    def test_typo_names_the_command_it_meant(self, tmp_path: Path):
        out = run_loader("/sc:analayze this module", self._project(tmp_path), "s1")
        assert "analayze" in out and "/sc:analyze" in out

    def test_retired_name_names_its_replacement(self, tmp_path: Path):
        out = run_loader(
            "/sc:workflow for the auth rework", self._project(tmp_path), "s1"
        )
        assert "/sc:workflow" in out and "/sc:roadmap" in out

    def test_unresolvable_name_injects_no_command_context(self, tmp_path: Path):
        """Silence plus 1,469 bytes of context is the worst of both."""
        out = run_loader("/sc:zzzzzz now", self._project(tmp_path), "s1")
        assert "zzzzzz" in out, "an unknown command was answered in silence"
        assert "context-inject" not in out, (
            "command context was injected for a command that does not exist"
        )

    def test_real_command_stays_silent(self, tmp_path: Path):
        out = run_loader("/sc:analyze this module", self._project(tmp_path), "s1")
        assert "SuperClaude command:" not in out
        assert "context-inject" in out, "a real command lost its context"

    def test_one_notice_per_prompt(self, tmp_path: Path):
        out = run_loader(
            "/sc:analayze then /sc:analayze again", self._project(tmp_path), "s1"
        )
        assert out.count("SuperClaude command:") == 1


class TestRetiredFlagNotices:
    """Flags the framework removed must redirect, not vanish.

    --think (175 uses), --think-hard (145) and --parellel (159) were typed long
    after their targets were deleted, and produced nothing at all. --ultrathink
    and --effort are native Claude Code controls, so silence is correct for them
    (A7a, A7b, D5 — the flag is not restored, the notice carries the redirect).
    """

    @staticmethod
    def _project(tmp_path: Path) -> Path:
        (tmp_path / ".claude" / "superclaude").mkdir(parents=True, exist_ok=True)
        return tmp_path

    def test_retired_think_flag_redirects(self, tmp_path: Path):
        out = run_loader("--think-hard about this", self._project(tmp_path), "s1")
        assert out.count("SuperClaude flag:") == 1
        assert "--think-hard" in out and "effort" in out

    def test_typo_of_a_retired_flag_redirects(self, tmp_path: Path):
        """--parellel has no valid flag within edit distance 2, so it stayed silent."""
        out = run_loader("--parellel please", self._project(tmp_path), "s1")
        assert out.count("SuperClaude flag:") == 1
        assert "--delegate" in out or "--concurrency" in out

    def test_native_controls_stay_silent(self, tmp_path: Path):
        for prompt in ("--effort high", "--ultrathink about it"):
            out = run_loader(prompt, self._project(tmp_path), "s1")
            assert "SuperClaude flag:" not in out, f"{prompt} produced a notice"

    def test_valid_flag_typo_still_suggests(self, tmp_path: Path):
        """The existing fuzzy fallback must survive the retired-flag pass."""
        out = run_loader("--instrospect this", self._project(tmp_path), "s1")
        assert "--introspect" in out
