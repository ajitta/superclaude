# Context Engineering Improvements — Implementation Plan

**Goal:** Implement 8 improvements from the context engineering spec, addressing all 5 critical panel findings, across 4 sprints in risk-ascending order (content first, code second).
**Architecture:** Content changes to core/*.md + commands/*.md (Sprints 1, 3), Python changes to context_loader.py (Sprint 2), integration tests (Sprint 2).
**Tech Stack:** Python 3.10+, pytest, markdown, XML components
**Spec:** `docs/specs/2026-03-22-context-engineering-improvements-design-chosh1179.md`
**Panel findings:** F2 (merge tier maps), N1 (budget overflow warning), N2 (Serena/Tavily → Tier 1), A1 (missing examples), C2 (regression tests)
**Status:** All 4 sprints COMPLETE — delivered 2026-03-22

### Delivery Summary

| Metric | Baseline | Final | Change |
|--------|----------|-------|--------|
| brainstorm+serena+tavily | 11,993 chars (~2,998t) | 3,705 chars (~926t) | **-69%** |
| --all-mcp (8 MCPs) | 29,459 chars (~7,365t) | 2,052 chars (~513t) | **-93%** |
| research+seq | 5,819 chars (~1,455t) | 2,446 chars (~612t) | **-58%** |
| Tests | 1,687 passed | 1,694 passed (+7) | 0 regressions |
| Panel findings | 5 critical | 5 resolved | 100% |

---

## Sprint 0: Baseline Measurement

### Task 0.1: Measure current token output baseline
**Files:** N/A (measurement only)
- [x] Run `echo "--brainstorm --serena --tavily" | python src/superclaude/scripts/context_loader.py` and count output chars
- [x] Run `echo "--all-mcp" | python src/superclaude/scripts/context_loader.py` and count output chars
- [x] Run `echo "--research --seq" | python src/superclaude/scripts/context_loader.py` and count output chars
- [x] Record baseline: `{3-flag: Xt, all-mcp: Yt, research: Zt}` as comment in plan
- [x] Run `uv run pytest` — record baseline pass count

---

## Sprint 1: Content-First (zero code risk) — Improvements #2, #3

### Task 1.1: Add examples to RULES.md core_rules section
**Files:** Modify: `src/superclaude/core/RULES.md:26-43`
- [x] Add `<examples>` block after line 43 (end of core_rules section, before `</core_rules>`)
- [x] Include 7 rows: Status Check, Diagnosis, Scope, Clarification, Verification, **Intent Verification** [A1], **Correction Capture** [A1]
- [x] Add 1 borderline row for Status Check showing judgment call [A2]
- [x] Verify XML is well-formed (no unclosed tags)
- [x] Run `uv run pytest tests/unit/test_content_structure.py -v`

**Example content for the 7+1 rows:**
```xml
<examples note="Representative scenarios — examples teach better than rules for Opus 4.6">
| Scenario | Wrong (❌) | Right (✅) | Rule |
|----------|-----------|-----------|------|
| User: "fix login bug" | Refactors auth + adds tests + updates docs | Fixes the specific bug, nothing else | Scope 🟡 |
| Before implementing feature | Starts coding immediately | `git log --oneline -5` + `grep -r "feature_name"` first | Status Check 🔴 |
| API endpoint returning 500 | Assumes code bug, reads source | Checks: port in use? DB running? env vars set? | Diagnosis 🔴 |
| User: "improve the dashboard" | Picks "add charts" as most likely | Asks: "Performance, UX, or data accuracy?" | Clarification 🟡 |
| 42/42 tests pass | "All tests pass" | "42/42 pass (baseline: 40, +2 new)" | Verification 🔴 |
| User: "let's restructure the auth module" | Starts moving files | "To confirm: reorganize file structure of src/auth/, not rewrite logic. Correct?" | Intent Verification 🔴 |
| User corrects: "no, the API routes" | Switches files silently | Saves memory: {trigger: 'restructure auth', misread: middleware, actual: API routes, prevention: 'restructure' can mean structure or logic} | Correction Capture 🟡 |
| User: "add validation to the form" (1 file, explicit path) | Runs git log + grep first | Edits the file directly — skip Status Check for single explicit-path tasks | Status Check (borderline) |
</examples>
```

### Task 1.2: Add examples to RULES.md anti_over_engineering section
**Files:** Modify: `src/superclaude/core/RULES.md:54-65`
- [x] Add `<examples>` block after line 65 (end of anti_over_engineering, before `</anti_over_engineering>`)
- [x] Include 3 rows showing over-engineered vs right-sized responses
- [x] Run `uv run pytest tests/unit/test_content_structure.py -v`

### Task 1.3: Add examples to PRINCIPLES.md philosophy section
**Files:** Modify: `src/superclaude/core/PRINCIPLES.md:7-14`
- [x] Add `<examples>` block after line 14 (end of philosophy, before `</philosophy>`)
- [x] Include 4 rows: Restraint-First, Right-Altitude, Evidence-Based, Parallel-Thinking
- [x] Run `uv run pytest tests/unit/test_content_structure.py -v`

### Task 1.4: Expand INSTRUCTION_MAP to 9 entries
**Files:** Modify: `src/superclaude/scripts/context_loader.py:146-153`
- [x] Replace INSTRUCTION_MAP dict with 9 entries (1 core + 8 MCP)
- [x] Classify MCPs: **behavioral** (Serena, Tavily) get longer instructions (~4 lines); **tool** MCPs (Context7, Sequential, Playwright, DevTools, Magic, Morphllm) get shorter (~2 lines)
- [x] Serena instruction must include: initialization sequence, symbolic workflow, decision rule (when Serena vs native), memory conventions
- [x] Tavily instruction must include: 5 tools, use cases, fallback to WebSearch
- [x] Run: `echo "--serena" | python src/superclaude/scripts/context_loader.py` — verify short instruction emitted, NOT full .md
- [x] Run: `echo "--brainstorm" | python src/superclaude/scripts/context_loader.py` — verify mode still injects full .md (modes not in INSTRUCTION_MAP)
- [x] Run `uv run pytest tests/unit/test_context_loader.py -v`

### Task 1.5: Add budget overflow warning [N1]
**Files:** Modify: `src/superclaude/scripts/context_loader.py:420-427`
- [x] Update the skipped_files summary to be visible (not just HTML comment): change `<!-- Skipped (budget):` to `<!-- ⚠️ Budget exceeded: skipped`
- [x] Include file names without priority notation for readability
- [x] Run `uv run pytest tests/unit/test_context_loader.py -v`

### Task 1.6: Add --verbose-context flag as safety valve [N3]
**Files:** Modify: `src/superclaude/scripts/context_loader.py:156,178-186` | Modify: `src/superclaude/core/FLAGS.md`
- [x] Add `"verbose-context"` to VALID_FLAGS set
- [x] In `output_inject_mode()`, check `--verbose-context` in prompt: if present, skip INSTRUCTION_MAP lookups (force full .md injection)
- [x] Add `--verbose-context` to FLAGS.md execution section: "Force full .md injection for all triggered contexts. Use when short instructions cause incorrect behavior."
- [x] Run `uv run pytest tests/unit/test_context_loader.py -v`

### Task 1.7: Sprint 1 verification
- [x] Run `uv run pytest` — full suite, compare to baseline pass count
- [x] Run 3-flag baseline measurement again — verify token reduction for MCP flags
- [x] Spot-check: `echo "--serena --tavily --c7" | python src/superclaude/scripts/context_loader.py` — should emit instructions, not full .md

---

## Sprint 2: Tiered Disclosure + Sub-Agent Framework — Improvements #1, #4

### Task 2.1: Implement TIER_0_MAP for 1-line MCP summaries
**Files:** Modify: `src/superclaude/scripts/context_loader.py` (add after INSTRUCTION_MAP)
- [x] Add `TIER_0_MAP` dict with 7 entries (6 tool MCPs + 1 core): one-line summaries (~15 tokens each)
- [x] Behavioral MCPs (Serena, Tavily): NOT in TIER_0 — they skip to INSTRUCTION_MAP (Tier 1) [N2]
- [x] Tool MCPs (Context7, Sequential, Playwright, DevTools, Magic, Morphllm): in TIER_0
- [x] Core (BUSINESS_SYMBOLS): in TIER_0

### Task 2.2: Implement tier selection logic
**Files:** Modify: `src/superclaude/scripts/context_loader.py:364-427`
- [x] Add `get_injection_tier(context_file: str, prompt: str) -> int` function
- [x] Logic: `--verbose-context` → always Tier 2 | behavioral MCP (serena, tavily) → Tier 1 (INSTRUCTION_MAP) | tool MCP → Tier 0 (TIER_0_MAP) | mode → Tier 2 (full .md) | core → Tier 0 or INSTRUCTION_MAP
- [x] Update `output_inject_mode()` to call `get_injection_tier()` before deciding injection method
- [x] Tier 0: emit `<sc-context-hint src="...">one-line</sc-context-hint>`
- [x] Tier 1: emit existing `<sc-context>instruction</sc-context>`
- [x] Tier 2: emit existing `<context-inject>full .md</context-inject>`
- [x] Ensure modes ALWAYS get Tier 2 (full .md) — modes define behavioral shifts, not tool references
- [x] Run `uv run pytest tests/unit/test_context_loader.py -v`

### Task 2.3: Add sub-agent decision framework to RULES.md
**Files:** Modify: `src/superclaude/core/RULES.md` (add after `</agent_orchestration>`, ~line 24)
- [x] Add `<sub_agent_decision>` section with Direct/Sub-agent/Never criteria
- [x] Add 5 example rows (task → decision → why) per spec
- [x] Add 1 borderline row [A2]
- [x] Run `uv run pytest tests/unit/test_content_structure.py -v`

### Task 2.4: Add integration tests for tiered injection [C2]
**Files:** Modify: `tests/unit/test_context_loader.py`
- [x] Add `TestTieredInjection` class
- [x] Test: `--c7` flag → verify TIER_0 content emitted (1-line, not full .md)
- [x] Test: `--serena` flag → verify INSTRUCTION_MAP content emitted (Tier 1, not Tier 0)
- [x] Test: `--verbose-context --c7` → verify full .md content emitted (Tier 2)
- [x] Test: `--brainstorm` mode → verify full .md content emitted (modes always Tier 2)
- [x] Test: budget overflow → verify `⚠️ Budget exceeded` warning in output
- [x] Test: TIER_0_MAP and INSTRUCTION_MAP have no overlapping keys with conflicting content [F2]
- [x] Run `uv run pytest tests/unit/test_context_loader.py -v` — all new tests pass

### Task 2.5: Sprint 2 verification
- [x] Run `uv run pytest` — full suite green
- [x] Re-measure 3 flag combinations — compare to Sprint 0 baseline
- [x] Expected: tool MCP flags (--c7, --magic, etc.) → ~80% token reduction; behavioral MCP flags (--serena, --tavily) → ~60% reduction; modes → no change

---

## Sprint 3: Documentation + Tracking — Improvements #5, #6, #7, #8

### Task 3.1: Add command scope map to help.md
**Files:** Modify: `src/superclaude/commands/help.md`
- [x] Add `<scope_map>` section with 6 clusters (analysis, PM, implementation, documentation, discovery, advisory)
- [x] Each entry: command name + 1-line scope differentiator
- [x] Run `uv run pytest tests/unit/test_command_structure.py -v`

### Task 3.2: Add session goal framing to load.md and save.md
**Files:** Modify: `src/superclaude/commands/load.md` | Modify: `src/superclaude/commands/save.md`
- [x] load.md: Add step to flow: "Session Goal (optional): If user provides a goal, record as 1-line objective"
- [x] save.md: Add step to flow: "Evaluate session goal completion status"
- [x] Run `uv run pytest tests/unit/test_command_structure.py -v`

### Task 3.3: Add rule IDs to RULES.md core_rules
**Files:** Modify: `src/superclaude/core/RULES.md:27-42`
- [x] Prefix each rule with `[R01]`–`[R16]` identifiers (16 rules, not 17 — corrected from initial estimate)
- [x] Update Correction Capture rule (R14) to include `violated_rule` field in format
- [x] Run `uv run pytest tests/unit/test_content_structure.py -v` — 105/105 pass

### Task 3.4: Add compaction strategy to save.md
**Files:** Modify: `src/superclaude/commands/save.md`
- [x] Add `<compaction_strategy>` section with preserve/discard/format guidance
- [x] Run `uv run pytest tests/unit/test_command_structure.py -v`

### Task 3.5: Sprint 3 verification
- [x] Run `uv run pytest` — full suite green
- [x] Verify: `uv run pytest tests/unit/test_content_structure.py tests/unit/test_command_structure.py -v`

---

## Sprint 4: Final Validation

### Task 4.1: Re-measure token output
- [x] Run same 3 flag combinations as Sprint 0
- [x] Record: `{3-flag: X'tokens, all-mcp: Y'tokens, research: Z'tokens}`
- [x] Compare: calculate actual % reduction vs baseline
- [x] Update spec status from "Draft" to "Delivered" with measured results

### Task 4.2: Update spec with delivery status
**Files:** Modify: `docs/specs/2026-03-22-context-engineering-improvements-design-chosh1179.md`
- [x] Change status from "Draft — awaiting user review" to "Delivered"
- [x] Add delivery summary table with actual token measurements
- [x] Mark all sprint checkboxes in spec

### Task 4.3: Deploy and verify
- [x] Run `make deploy`
- [x] Verify in fresh session: `--serena` emits instruction, not full .md
- [x] Verify in fresh session: `--brainstorm` still emits full .md
- [x] Verify: budget overflow warning visible

---

## File Change Summary

| File | Sprint | Changes |
|------|--------|---------|
| `src/superclaude/core/RULES.md` | 1, 2, 3 | +examples (×2 blocks), +sub_agent_decision, +rule IDs |
| `src/superclaude/core/PRINCIPLES.md` | 1 | +examples (×1 block) |
| `src/superclaude/scripts/context_loader.py` | 1, 2 | +8 INSTRUCTION_MAP entries, +TIER_0_MAP, +tier logic, +overflow warning, +verbose-context |
| `src/superclaude/core/FLAGS.md` | 1 | +verbose-context flag |
| `src/superclaude/commands/help.md` | 3 | +scope_map section |
| `src/superclaude/commands/load.md` | 3 | +session goal step |
| `src/superclaude/commands/save.md` | 3 | +goal evaluation, +compaction_strategy |
| `tests/unit/test_context_loader.py` | 2 | +TestTieredInjection class (7 tests) |
| `docs/specs/2026-03-22-*` | 4 | Status update + measurements |

**Total: 9 files across 4 sprints. No new files created.**

---

## Panel Finding Resolution Map

| Finding | ID | Resolution | Sprint | Task |
|---------|-----|-----------|--------|------|
| Merge tier maps (3 representations) | F2 | TIER_0 for 1-liners, INSTRUCTION_MAP for Tier 1, full .md for Tier 2 — no TIER_1_MAP | 2 | 2.1-2.2 |
| Budget overflow warning | N1 | `⚠️ Budget exceeded: skipped [files]` visible comment | 1 | 1.5 |
| Serena/Tavily default Tier 1 | N2 | Behavioral MCPs skip TIER_0, go to INSTRUCTION_MAP | 2 | 2.1-2.2 |
| Missing Intent Verification + Correction Capture examples | A1 | Added as rows 6-7 in Task 1.1 | 1 | 1.1 |
| Regression tests for context_loader.py | C2 | 7 integration tests in TestTieredInjection | 2 | 2.4 |
