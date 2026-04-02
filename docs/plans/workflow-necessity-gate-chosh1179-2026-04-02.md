---
status: draft
revised: 2026-04-02
spec: docs/specs/workflow-necessity-gate-discovery-chosh1179-2026-04-02.md
---

# Workflow Necessity Gate — Implementation Plan

**Goal:** Embed over-engineering prevention into /sc:design, /sc:implement, and RULES.md workflow gates.
**Architecture:** Three markdown files modified — no code changes. Necessity Gate (3-question test) in design.md flow, Phase Validation in implement.md flow, [R18] rule + updated workflow_gates in RULES.md.
**Tech Stack:** Markdown-only (docs-change-safe — zero test risk)

## Simplicity Filter Applied

Before planning, each proposed change was tested with the Necessity Gate itself:

| Change | Q1 Broken? | Q2 Already solved? | Q3 Evidence? | Decision |
|--------|-----------|-------------------|-------------|----------|
| design.md Necessity Gate | Yes (57% waste) | No | Yes (44KB→15KB) | **Proceed** |
| RULES.md [R18] + gates | Partial | Partial ([R06]) | Yes | **Proceed** |
| implement.md Phase Validation | Yes (3 runtime bugs) | No | Yes | **Proceed** |
| review.md --scope phase | No | Partial (--scope diff works) | Weak | **Deferred** |
| simplicity-coach description | No | No | Weak (1 case) | **Deferred** |

Result: 6 files → 3 files. 2 changes deferred as nice-to-have.

---

## Task 1: design.md — Necessity Gate, Constraints, Principle Consequence

**Files:** Modify: `src/superclaude/commands/design.md:13-19,70`

- [ ] Step 1: Replace `<flow>` section (lines 13-19) with expanded 8-step flow:
```xml
  <flow>
    1. Analyze: Requirements + existing context
    2. Plan: Design approach + structure
    3. Design: Comprehensive specs + best practices (see outputs)
    4. Constraints: Document operational parameters that constrain design — queue/buffer sizes, connection pool limits, external API batch limits, timeout values
    5. Necessity: For each proposed component, apply 3-question test:
       Q1: "Is the system broken without this?" (requires specific failure scenario)
       Q2: "Does an existing mechanism already solve this?" (requires evidence)
       Q3: "Is there quantitative evidence this is needed?" (requires numbers)
       All 3 fail = defer to post-MVP review — skip detailed design for this component
    6. Principle Consequence: For each stated design principle, ask: "If this principle is true, which components become unnecessary?" — eliminate contradictions
    7. Validate: Requirements coverage ≥90%, maintainability check
    8. Document: Save design spec to docs/specs/<topic>-design-<username>-YYYY-MM-DD.md (with frontmatter: status: draft, revised: <today>) + diagrams
  </flow>
```

- [ ] Step 2: Replace `<handoff>` (line 70) to add /sc:plan as first next step:
```xml
  <handoff next="/sc:plan /sc:implement /sc:workflow"/>
```

- [ ] Step 3: Verify — `uv run pytest tests/unit/test_command_structure.py -k design -v`

---

## Task 2: RULES.md — [R18] Necessity Test + Workflow Gates Update

**Files:** Modify: `src/superclaude/core/RULES.md:43,44-58,119-124`

- [ ] Step 1: Insert [R18] after line 43 ([R17]), before `<examples>`:
```
[R18] Necessity Test 🟡: before designing a component, answer "Is the system broken without this?" — "safer/better" alone is insufficient. Require: specific failure scenario, quantitative evidence, or user-facing impact. "Deferred to post-MVP review" is a valid design decision
```

- [ ] Step 2: Add [R18] example row to the examples table (after existing rows, before `</examples>`):
```
  | Designing component "just in case" | "Good practice for resilience" | "Queue+retry self-regulates. No failure scenario without it. Defer." | Necessity Test 🟡 |
```

- [ ] Step 3: Replace `<workflow_gates>` section (lines 119-124) with expanded chain:
```xml
  <workflow_gates note="Recommended workflow chain">
    /sc:brainstorm -> /sc:design: User approves discovery spec before designing
    /sc:design -> necessity-check: Each component passes 3-question test (Q1: broken without? Q2: already solved? Q3: quantitative evidence?)
    /sc:design -> /sc:plan: Design spec committed (core decisions only, deferred items marked)
    /sc:plan -> /sc:implement --plan: Plan document committed to repo
    /sc:implement -> phase-validate: Each phase: build -> run -> "does this solve the next phase's problem?"
    /sc:implement -> /sc:test: Implementation complete
    /sc:test -> done: Test pass evidence required (actual output, not claims)
  </workflow_gates>
```

- [ ] Step 4: Verify — file reads cleanly, no broken XML nesting

---

## Task 3: implement.md — Phase Validation Loop

**Files:** Modify: `src/superclaude/commands/implement.md:13-20`

- [ ] Step 1: Replace `<flow>` section (lines 13-20) with expanded 7-step flow:
```xml
  <flow>
    1. Load: If --plan provided, read plan document and extract tasks; otherwise analyze requirements + tech context
    2. Plan: Approach + activate personas; for plan mode, follow task order exactly
    3. Checkpoint: If changes affect >3 files → present numbered plan → wait for user approval before editing
    4. Execute: Code + framework best practices; for plan mode, mark tasks complete as you go
    5. Phase Gate: After each phase/task group — build + run if possible, then ask: "Does this phase's result already solve the next phase's problem?" If yes → skip next phase with reason. Present results to user before continuing
    6. Validate: Security + quality checks; run verification command per task
    7. Integrate: Docs + testing recs; report any blockers encountered
  </flow>
```

- [ ] Step 2: Verify — `uv run pytest tests/unit/test_command_structure.py -k implement -v`

---

## Verification Checklist

- [ ] All 3 files pass `test_command_structure.py` (design, implement validated; RULES.md has no structure test)
- [ ] design.md: flow has 8 numbered steps, handoff updated
- [ ] RULES.md: [R18] present, examples table has new row, workflow_gates includes /sc:design
- [ ] implement.md: flow has 7 numbered steps with Phase Gate
- [ ] `make deploy` — install to ~/.claude/

## Commit

```
feat: add necessity gate to design workflow — prevent over-engineering at source

Based on bulk-asset-delete retrospective (57% design waste, 90K token loss):
- design.md: 3-question necessity test, operational constraints, principle consequence
- implement.md: phase validation loop (build→run→decide next)
- RULES.md: [R18] Necessity Test rule, expanded workflow_gates with /sc:design

Spec: docs/specs/workflow-necessity-gate-discovery-chosh1179-2026-04-02.md
```
