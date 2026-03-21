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
| Flag alias/fuzzy matching | #2 (P1) | **DONE** | 1 |
| Workflow reconnection (analyze→plan) | #3 (P1) | **DONE** | 1 |
| Serena-first directive | #5 (P2) | **DONE** | 1 |
| FLAGS.md alias documentation | — | TODO | 2 |
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

- [ ] Stage all files
- [ ] Commit: `feat: add flag alias/fuzzy matching, Serena-first directive, and analyze→plan handoff`
- [ ] Verify: `git log --oneline -1`

### Task 2: Deploy
- [ ] Run `make deploy`
- [ ] Verify: `echo '{"prompt":"--ultrathink"}' | python -m superclaude.scripts.context_loader` shows alias correction

---

## Sprint 2: FLAGS.md Alias Documentation

### Task 3: Document alias system in FLAGS.md
**Files:** Modify: `src/superclaude/core/FLAGS.md`

- [ ] Add `<aliases>` section after `<execution>` documenting:
  - `--ultrathink` → `--seq`
  - `--think` / `--think-hard` → `--seq`
  - `--parallel` / `--parellel` → `--delegate`
  - Fuzzy matching behavior (auto-suggest for typos)
- [ ] Add `--serena` directive note in `<mcp>` section
- [ ] Verify: `uv run pytest tests/unit/test_content_structure.py -v -k flags`

### Task 4: Final commit + deploy
- [ ] Commit: `docs: add flag alias system documentation to FLAGS.md`
- [ ] Run `make deploy`
- [ ] Verify: installed FLAGS.md matches source

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
