---
status: implemented
revised: 2026-04-11
source: docs/specs/superclaude-weakness-fixes-design-ajitta-2026-04-11.md
---

# W1 Agent Rule Reinforcement — Phase 1 Implementation Plan

**Goal:** Add `<gotchas>` sections to 5 high-judgment agents, reinforcing critical rules (R02, R13, R15, R18) at agent-level (Position 2) to counteract compaction drift in long sessions.

**Architecture:** Content-only change. Each agent gets 2 gotchas lines inserted between `<handoff>` and `<bounds>` (matching existing convention in backend-architect.md). No new files, no code changes, no new rules.

**Token Cost:** ~3 lines x 5 agents = 15 lines, ~400-500 tokens total. Per-session impact: ~3 lines for whichever agent is delegated to.

**Source Decision:** W1 in design spec was deferred with template ready. Phase 1 targets the 5 highest-judgment agents per spec recommendation. Phase 2 selective (5 high-value agents) implemented same session. Remaining 8 low-risk agents deferred.

---

## Pre-flight

- [x] Verify all 5 agents currently lack `<gotchas>`: `grep -l "<gotchas" src/superclaude/agents/{self-review,system-architect,refactoring-expert,project-manager,root-cause-analyst}.md` (expect: no output)
- [x] Confirm current gotchas count: `grep -rl "<gotchas" src/superclaude/agents/ | wc -l` (expect: 5)

---

### Task 1: self-review.md — R15 Verification + R06 Scope

**File:** Modify: `src/superclaude/agents/self-review.md`
**Location:** After L63 (`<handoff>`), before L65 (`<bounds>`)

- [x] Insert gotchas block:

```xml
  <gotchas>
  - verification-evidence: Cite actual test output, not claims. "42/42 pass" requires running the tests [R15]
  - scope-creep: Review only what changed — do not reopen entire task or flag pre-existing issues as new findings [R06]
  </gotchas>
```

- [x] Verify: `grep -c "gotchas" src/superclaude/agents/self-review.md` (expect: 2 — open + close tags)

---

### Task 2: system-architect.md — R18 Necessity Test + R06 Scope

**File:** Modify: `src/superclaude/agents/system-architect.md`
**Location:** After L102 (`<handoff>`), before L104 (`<bounds>`)

- [x] Insert gotchas block:

```xml
  <gotchas>
  - necessity-gate: Before proposing changes, answer "Is the system broken without this?" [R18]
  - scope-anchoring: Architecture advice addresses the user's question, not adjacent systems. "While we're here" is out of scope [R06]
  </gotchas>
```

- [x] Verify: `grep -c "gotchas" src/superclaude/agents/system-architect.md` (expect: 2)

---

### Task 3: refactoring-expert.md — R02 Status Check + R06 Scope

**File:** Modify: `src/superclaude/agents/refactoring-expert.md`
**Location:** After L66 (`<handoff>`), before L68 (`<bounds>`)

- [x] Insert gotchas block:

```xml
  <gotchas>
  - status-check: Before starting work, run 2-3 targeted searches to verify work isn't already complete [R02]
  - scope-discipline: Refactor only what's asked — changing file X does not grant permission to refactor X's imports, callers, or tests [R06]
  </gotchas>
```

- [x] Verify: `grep -c "gotchas" src/superclaude/agents/refactoring-expert.md` (expect: 2)

---

### Task 4: project-manager.md — R13 Intent Verification + R04 Planning

**File:** Modify: `src/superclaude/agents/project-manager.md`
**Location:** After L92 (`<handoff>`), before L94 (`<bounds>`)

- [x] Insert gotchas block:

```xml
  <gotchas>
  - intent-confirm: Restate user intent before non-trivial work, especially when task direction changes mid-conversation [R13]
  - delegation-check: Direct work for <3 steps or sequential deps. Sub-agents only for 3+ independent parallel streams [R04]
  </gotchas>
```

- [x] Verify: `grep -c "gotchas" src/superclaude/agents/project-manager.md` (expect: 2)

---

### Task 5: root-cause-analyst.md — R13 Intent Verification + R03 Diagnosis

**File:** Modify: `src/superclaude/agents/root-cause-analyst.md`
**Location:** After L74 (`<handoff>`), before L76 (`<bounds>`)

- [x] Insert gotchas block:

```xml
  <gotchas>
  - intent-confirm: Restate user intent before non-trivial work, especially when task direction changes mid-conversation [R13]
  - hypothesis-discipline: Generate 3+ hypotheses ranked by simplicity. Do not conclude with first plausible match — falsify before confirming [R03]
  </gotchas>
```

- [x] Verify: `grep -c "gotchas" src/superclaude/agents/root-cause-analyst.md` (expect: 2)

---

### Task 6: Verification

- [x] All agent tests pass: `uv run pytest tests/unit/test_agent_structure.py -v` — 720 pass, 1 pre-existing failure (frontend-architect skill ref)
- [x] Gotchas count increased: `grep -rl "<gotchas" src/superclaude/agents/ | wc -l` — 10 (up from 5)
- [x] No new files: `git status` shows only 5 modified files + 1 new plan file
- [x] Rule tag cross-check: `grep -r "\[R15\]" src/superclaude/agents/` includes self-review
- [x] Rule tag cross-check: `grep -r "\[R18\]" src/superclaude/agents/` includes system-architect
- [x] Rule tag cross-check: `grep -r "\[R02\]" src/superclaude/agents/` includes refactoring-expert
- [x] Rule tag cross-check: `grep -r "\[R13\]" src/superclaude/agents/` includes project-manager + root-cause-analyst

---

### Task 7: Commit

- [x] Stage 5 agent files: `git add src/superclaude/agents/{self-review,system-architect,refactoring-expert,project-manager,root-cause-analyst}.md`
- [x] Commit: `feat: add gotchas to 5 high-judgment agents for critical rule reinforcement (W1 Phase 1)` — d437f0d
- [x] Deploy: `make deploy` (propagates to ~/.claude/agents/)
- [x] Update design spec status: W1 updated from "Plan" to "Partial" — Phase 1 complete, Phase 2 deferred

---

## Rule-to-Agent Matrix (Phase 1 Summary)

| Agent | Primary Rule | Secondary Rule | Category |
|-------|-------------|----------------|----------|
| self-review | R15 Verification | R06 Scope | Reviewer |
| system-architect | R18 Necessity Test | R06 Scope | Proposer |
| refactoring-expert | R02 Status Check | R06 Scope | Implementer |
| project-manager | R13 Intent Verification | R04 Planning | Planner |
| root-cause-analyst | R13 Intent Verification | R03 Diagnosis | Planner |

## Phase 2 Selective — IMPLEMENTED (2026-04-11)

5 high-value agents from remaining pool. Educators (3) and executors (3) deferred as low-risk/procedural.

| Category | Agents | Gotcha Rule | Status |
|----------|--------|-------------|--------|
| Implementers | python-expert, devops-architect, performance-engineer | R02 Status Check + R06 Scope | **Done** |
| Proposers | requirements-analyst | R18 Necessity Test + R06 Scope | **Done** |
| Analysts | business-panel-experts | R13 Intent + R06 Scope | **Done** |
| Executors | git-workflow, repo-index, project-initializer | R02 Status Check | Deferred (procedural) |
| Educators | learning-guide, socratic-mentor, technical-writer | (low risk) | Deferred (low-judgment) |

## Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| 1 | 5 target agents have `<gotchas>` sections | grep count = 10 (up from 5) |
| 2 | Each gotcha references a specific [RXX] tag | grep `\[R\d+\]` in all 5 files |
| 3 | Gotchas placed after `<handoff>`, before `<bounds>` | Manual inspection |
| 4 | All agent structure tests pass | `uv run pytest tests/unit/test_agent_structure.py -v` |
| 5 | No new files created (except plan) | `git status` |
| 6 | Token cost per agent <= 3 lines | Line count of each `<gotchas>` block |
