---
status: draft
revised: 2026-04-03
---

# Discovery: Modes Validation & Content Improvement + context_loader.py

## Problem Statement

7 mode files pass structural tests (84/84) but contain content that violates mode-authoring rules. `context_loader.py` has an orphaned config file and no path validation. This spec addresses rule compliance and loader robustness.

## Decisions (User-Confirmed)

| # | Decision | Choice |
|---|----------|--------|
| 1 | RESEARCH_CONFIG.md | **1a**: Keep, make `--research` a composite flag (DeepResearch + config) |
| 2 | Procedural content in modes | **2c**: Condense into `<behaviors>` as principles, remove procedures |
| 3 | Tiered mode injection | **No**: Marginal gain (~90 tokens/mode), skip |
| 4 | Path validation in context_loader | **Yes**: Warning-level, not crash |
| 5 | Scope | **5a**: Existing 7 modes + loader fixes only |

## Scope

### In-Scope

- Fix 4 red rule violations in 3 mode files
- Fix 2 yellow quality gaps in 2 mode files
- Add `--research` composite flag in context_loader.py
- Add TRIGGER_MAP path validation in context_loader.py

### Out-of-Scope

- Adding/removing modes
- Tiered injection (INSTRUCTION_MAP for modes)
- Session cache cleanup
- Richer examples in modes

## Changes

### 1. MODE_DeepResearch.md — Remove agent-style content

**Remove:**
- `<integration>` section (lines 24-29) — agent-style integration spec, not cognitive overlay
- `## Extended Thinking` section (lines 31-34) — operational guidance, not mindset

**Condense into `<behaviors>`:**
- "Tool-Integrated: leverage search + reasoning tools as natural extensions of investigation" (replaces `<integration>`)

### 2. MODE_Task_Management.md — Remove procedures

**Remove:**
- `## Memory Operations` (lines 24-27) — step-by-step procedure
- `## Execution Flow` (line 30) — step-by-step procedure

**Condense into `<behaviors>`:**
- "State-Aware: orient to current position (load context → identify phase → resume) before acting" (replaces Memory Operations)
- "Checkpoint-Disciplined: persist state at phase transitions, not arbitrary intervals" (already partially in `<thinking>`, reinforce in behaviors)

### 3. MODE_Orchestration.md — Remove procedures

**Remove:**
- `## Tool Selection Principles` (lines 24-27) — procedural
- `## Infra Validation` (lines 29-32) — procedural checklist
- `## Parallel Rules` (line 35) — procedural

**Condense into `<behaviors>`:**
- "Verification-First: consult official docs before infra/config changes — never assume" (replaces Infra Validation)
- Existing behaviors already cover tool selection and parallel — just remove redundant ## sections

**Fix axis duplication:**
- `<thinking>` and `<behaviors>` currently overlap heavily. Differentiate:
  - `<thinking>` = cognitive principles (WHY to think this way)
  - `<behaviors>` = observable patterns (WHAT you do differently)

### 4. MODE_Introspection.md — Fix redundancy

**Fix:**
- Remove marker list `(thinking|target|action|metrics|insight)` from `<behaviors>` — keep only in `<communication>` where it's the presentation style
- Rephrase behavior to focus on the action pattern, not the output format

### 5. context_loader.py — Add `--research` composite

**Add to COMPOSITE_FLAGS:**
```python
"--research": [
    ("modes/MODE_DeepResearch.md", 1),
    ("modes/RESEARCH_CONFIG.md", 2),
],
```

**Update TRIGGER_MAP:**
- Remove `--research` from the standard TRIGGER_MAP entry (it's now handled by COMPOSITE_FLAGS)
- Keep non-flag triggers (`deep.?research`, `systematic.?investigation`, `/sc:research`) pointing to MODE_DeepResearch.md only

### 6. context_loader.py — Add path validation

**Add startup validation function:**
```python
def _validate_trigger_paths() -> None:
    """Warn about TRIGGER_MAP entries pointing to non-existent files."""
    for _, path, _ in TRIGGER_MAP:
        if not (BASE_PATH / path).exists():
            print(f"<!-- warning: context file not found: {path} -->", file=sys.stderr)
```

**Call location:** After `BASE_PATH` is set, before `TRIGGER_MAP` compilation.
Also validate COMPOSITE_FLAGS paths.

## Files Changed

| File | Change Type |
|------|-------------|
| `src/superclaude/modes/MODE_DeepResearch.md` | Content cleanup |
| `src/superclaude/modes/MODE_Task_Management.md` | Content cleanup |
| `src/superclaude/modes/MODE_Orchestration.md` | Content cleanup + axis dedup |
| `src/superclaude/modes/MODE_Introspection.md` | Redundancy fix |
| `src/superclaude/scripts/context_loader.py` | Composite flag + path validation |

## Verification

```bash
# All mode tests must still pass
uv run python -m pytest tests/unit/test_mode_structure.py -v

# context_loader integration
uv run python -m pytest tests/ -k "context_loader" -v

# Full suite baseline: 1787 collected, ~1694 passing
uv run python -m pytest
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Behavior regression from content removal | Low | Medium | Content condensed into behaviors, not deleted |
| Test failures from structural changes | Low | Low | 4-axis structure preserved, only inner content changes |
| Composite flag interaction with existing triggers | Low | Low | Remove `--research` from TRIGGER_MAP to avoid double-load |
