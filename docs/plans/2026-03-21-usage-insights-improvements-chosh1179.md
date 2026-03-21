# Usage Insights Improvements — Implementation Plan

**Goal:** Ship data-driven improvements to SuperClaude based on deep analysis of 640 sessions / 3.6M tokens of usage data
**Architecture:** context_loader.py flag processing pipeline + FLAGS.md documentation + analyze.md workflow handoff
**Tech Stack:** Python (context_loader.py), Markdown (commands, core), pytest
**Spec:** [docs/specs/2026-03-21-usage-insights-improvement-design-chosh1179.md](../specs/2026-03-21-usage-insights-improvement-design-chosh1179.md)
**Analysis:** [docs/analysis/2026-03-21-claude-code-insights-deep-analysis-chosh1179.md](../analysis/2026-03-21-claude-code-insights-deep-analysis-chosh1179.md)

---

## Implementation Summary

| Improvement | Spec # | Status | Sprint |
|-------------|--------|--------|--------|
| Flag alias/fuzzy matching | #2 (P1) | **DONE** | 1 (`74d24ba`) |
| Workflow reconnection (analyze→plan) | #3 (P1) | **DONE** | 1 (`74d24ba`) |
| Serena-first directive | #5 (P2) | **DONE** | 1 (`74d24ba`) |
| FLAGS.md alias documentation | — | **DONE** | 2 (`f37ddaf`) |
| Observer session phase-out | #1 (P0) | USER ACTION | — |
| oasis_editor test conventions | #4 (P2) | OUT OF SCOPE | — |
| Unused command audit | #6 (P3) | INFORMATIONAL | — |

---

## Sprint 1: Commit & Deploy Already-Implemented Improvements

### Task 1: Commit all changes
**Files:**
- Modify: `src/superclaude/scripts/context_loader.py` (+85 lines)
- Modify: `src/superclaude/commands/analyze.md` (+1 line)
- Modify: `tests/unit/test_context_loader.py` (+118 lines)
- Create: `docs/analysis/2026-03-21-claude-code-insights-deep-analysis-chosh1179.md`
- Create: `docs/specs/2026-03-21-usage-insights-improvement-design-chosh1179.md`
- Create: `docs/plans/2026-03-21-usage-insights-improvements-chosh1179.md`

- [x] Stage all files
- [x] Commit: `feat: add flag alias/fuzzy matching, Serena-first directive, and usage insights analysis` → `74d24ba`
- [x] Verify: `git log --oneline -1`

### Task 2: Deploy
- [x] Run `make deploy` → `superclaude v4.3.0+ajitta` deployed as global editable tool
- [x] Verify: alias + fuzzy match E2E confirmed

---

## Sprint 2: FLAGS.md Alias Documentation

### Task 3: Document alias system in FLAGS.md
**Files:** Modify: `src/superclaude/core/FLAGS.md`

- [x] Add `<aliases>` section after `<execution>` documenting all 12 aliases + fuzzy-match rules
- [x] Add `--serena` directive note in `<mcp>` section
- [x] Verify: tests pass

### Task 4: Final commit + deploy
- [x] Commit: `docs: add flag alias system and Serena directive documentation to FLAGS.md` → `f37ddaf`
- [x] Run `make deploy`
- [x] Verify: installed FLAGS.md matches source

---

## Out-of-Scope Items (documented for future action)

### Observer Session Phase-Out (P0 — user process change)
**Not a code change.** Observer sessions are launched externally by claude-mem skill.
**Action for user:**
1. Stop launching observer sessions alongside primary sessions
2. Use `/sc:save` at session end instead (already captures: session progress, corrections, architectural decisions)
3. Track token consumption in next report period — target: observer tokens → 0

### oasis_editor Test Conventions (P2 — different project)
**Action for user:** Add Vitest mock hoisting guide to oasis_editor project's CLAUDE.md:
```
## Testing (Vitest)
- vi.mock() at file top (hoisting)
- vi.clearAllMocks() in beforeEach()
- Read 2-3 existing tests before writing new ones
```

### Unused Command Audit (P3 — informational)
13/32 commands with 0 usage. No action needed — commands don't cost tokens unless invoked.
Consider: consolidate or rename underused commands based on next report period data.

---

## Verification

| Check | Command | Expected |
|-------|---------|----------|
| Unit tests | `uv run pytest tests/unit/test_context_loader.py -v` | 21 pass |
| Structure tests | `uv run pytest tests/unit/test_agent_structure.py tests/unit/test_command_structure.py -v` | 1088+ pass |
| Alias smoke test | `echo '{"prompt":"--ultrathink --loo"}' \| uv run python -m superclaude.scripts.context_loader` | Auto-corrected notifications |
| Serena directive | `echo '{"prompt":"--serena"}' \| uv run python -m superclaude.scripts.context_loader` | `<sc-directive flag="--serena">` |
| Fuzzy match | `echo '{"prompt":"--seqq"}' \| uv run python -m superclaude.scripts.context_loader` | "Did you mean: --seq?" |
