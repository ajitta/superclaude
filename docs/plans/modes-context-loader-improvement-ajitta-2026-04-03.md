---
status: draft
revised: 2026-04-03
---

# Modes & context_loader Improvement — Implementation Plan

**Goal:** Fix mode-authoring rule violations (procedural content in 3 modes, redundancy in 1), add `--research` composite flag, add path validation to context_loader.py
**Architecture:** Content-only changes to 4 mode .md files + 2 functional changes to context_loader.py
**Spec:** `docs/specs/modes-context-loader-improvement-discovery-ajitta-2026-04-03.md`

## Task 1: MODE_DeepResearch.md — Remove agent-style content

**Files:** Modify: `src/superclaude/modes/MODE_DeepResearch.md`

- [ ] Remove `<integration>` section (lines 24-29)
- [ ] Remove `## Extended Thinking` section (lines 31-34)
- [ ] Add to `<behaviors>`: `Tool-Integrated: leverage search + reasoning tools as natural extensions of systematic investigation`
- [ ] Verify: 4 axes present, no procedures remain, `<outcomes>` preserved

## Task 2: MODE_Task_Management.md — Remove procedures

**Files:** Modify: `src/superclaude/modes/MODE_Task_Management.md`

- [ ] Remove `## Memory Operations` section (lines 24-27)
- [ ] Remove `## Execution Flow` section (line 30)
- [ ] Replace `Memory-Backed` behavior with: `State-Aware: orient to current position (load context, identify phase, resume) before acting`
- [ ] Add behavior: `Checkpoint-Disciplined: persist state at natural phase transitions, not arbitrary intervals`
- [ ] Verify: 4 axes present, no procedures remain

## Task 3: MODE_Orchestration.md — Remove procedures + fix axis duplication

**Files:** Modify: `src/superclaude/modes/MODE_Orchestration.md`

- [ ] Remove `## Tool Selection Principles` (lines 24-27)
- [ ] Remove `## Infra Validation` (lines 29-32)
- [ ] Remove `## Parallel Rules` (line 35)
- [ ] Add behavior: `Verification-First: consult official docs before infra/config changes — never assume`
- [ ] Deduplicate axes — differentiate `<thinking>` (WHY) from `<behaviors>` (WHAT):
  - `<thinking>`: keep as cognitive reasoning principles
  - `<behaviors>`: rewrite as observable action patterns (avoid repeating thinking items)
- [ ] Verify: 4 axes present, no procedures, thinking ≠ behaviors

## Task 4: MODE_Introspection.md — Fix redundancy

**Files:** Modify: `src/superclaude/modes/MODE_Introspection.md`

- [ ] Remove marker list `(thinking|target|action|metrics|insight)` from `<behaviors>` Transparency item
- [ ] Rephrase: `Transparency: expose reasoning chains and decision logic, not just conclusions`
- [ ] Keep marker list only in `<communication>` (presentation format, not behavior)
- [ ] Verify: no duplicate content between axes

## ~~Task 5: CUT~~ (composite flag — YAGNI, simplicity review)

## Task 6: test — TRIGGER_MAP path validation

**Files:** Modify: `tests/unit/test_context_loader.py`

- [ ] Add single test: assert all TRIGGER_MAP + COMPOSITE_FLAGS paths resolve to existing files
- [ ] No runtime validation function — existing structural tests + this test suffice

## Task 7: Verification

- [ ] `uv run python -m pytest tests/unit/test_mode_structure.py -v` — 84/84 pass
- [ ] `uv run python -m pytest tests/unit/test_context_loader.py -v` — all pass
- [ ] `uv run python -m pytest` — baseline maintained (~1694 passing)

## Parallelization

Tasks 1-4 are independent (separate mode files) — **parallel**.
Task 6 (test only) after modes. Task 7 last.

```
[T1] [T2] [T3] [T4]   ← parallel (4 mode files)
         |
        [T6]            ← test addition
         |
        [T7]            ← verification
```
