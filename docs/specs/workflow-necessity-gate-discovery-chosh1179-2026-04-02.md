---
status: draft
revised: 2026-04-02
source: /Users/chosh/Repos/fitfuns/oasis/oasis-nakama-dev/docs/analysis/2026-04-02-bulk-asset-delete-retrospective-chosh1179.md
---

# Workflow Necessity Gate — SuperClaude Over-Engineering Prevention

## 1. Problem Statement

A real-world project (bulk asset delete, oasis-nakama-dev) exposed systematic failures in the SuperClaude spec-design-plan-implement-review workflow:

| Metric | Value |
|--------|-------|
| Design spec size | 44KB |
| Components designed | 7 |
| Components scrapped post-review | 4 (57%) |
| Code written then deleted | ~462 lines (-30%) |
| Token waste | ~90K (~45% of session) |
| Runtime bugs discoverable at design time | 2 of 3 |
| simplicity-coach usage | Never invoked |
| simplicity-guide usage | Only at final review (too late) |

## 2. Root Cause Analysis

| # | Root Cause | Evidence | Severity |
|---|-----------|----------|----------|
| RC1 | simplicity-coach not triggered | workflow_gates has no simplicity checkpoint; tool is opt-in | Critical |
| RC2 | simplicity-guide invoked too late | Used only after all 10 commits; review was shathu (post-hoc) | Critical |
| RC3 | No design budget/proportionality | 44KB spec for "move S3 deletes to worker pool"; no constraint on spec detail | High |
| RC4 | No phase-by-phase validation | All phases implemented before first test run; 3 runtime bugs found on first execution | High |
| RC5 | No operational parameter checklist | `outgoing_queue_size: 64` and DB connection limits not checked at design time | Medium |

### Current workflow_gates (RULES.md)

```
/sc:brainstorm -> /sc:plan: User approves spec before planning
/sc:plan -> /sc:implement --plan: Plan document committed to repo
/sc:implement -> /sc:test: Implementation complete
/sc:test -> done: Test pass evidence required
```

**Gap**: /sc:design is not in the chain. No simplicity checkpoint exists anywhere.

## 3. Proposed Improvements — Three Layers

### Layer 1: Necessity Gate in /sc:design (Prevents over-design)

**What**: Add 3 mechanisms to design.md `<flow>` after component identification, before detailed design.

#### Mechanism 1: 3-Question Necessity Test

For each proposed component:

| # | Question | Pass Criteria |
|---|----------|--------------|
| Q1 | Is the system **broken** without this? | Must answer "Yes" with specific failure scenario |
| Q2 | Does an existing mechanism **already solve** this? | Must answer "No" with evidence |
| Q3 | Is there **quantitative evidence** this is needed? | Must cite numbers (throughput, latency, capacity) |

- All 3 "No" = classify as "deferred to post-MVP review" — skip detailed design
- Any "Yes" required with evidence to proceed to detailed design

**Retrospective application**:

| Component | Q1 Broken? | Q2 Already solved? | Q3 Quantitative? | Result |
|-----------|-----------|-------------------|------------------|--------|
| Circuit breaker | No (queue+retry sufficient) | Yes (bounded queue is self-regulating) | No | **Defer** |
| Orphan persistence | No (S3 orphan invisible to user) | Yes (Storage=SoT, already deleted) | No | **Defer** |
| Backpressure | No (system functional without) | Yes (batch opcode reduces 1000->5 msgs) | No | **Defer** |
| Worker pool | Yes (S3 blocking = match freeze) | No (no existing async path) | Yes (2000 assets, 3s/asset) | **Design** |
| Batch opcode (Op7) | Yes (Op6*N overflows WS queue) | No | Yes (outgoing_queue_size: 64) | **Design** |
| Dialog system | Yes (UX requires progress feedback) | No | N/A (UX requirement) | **Design** |

Result: 3 of 7 components filtered out at design time. 44KB -> ~15KB estimated.

#### Mechanism 2: Principle Consequence Step

After stating each design principle, mandatory reverse question:

> "If this principle is true, which proposed components become **unnecessary**?"

**Retrospective application**:
- Principle: "Storage = Source of Truth"
- Consequence: If Storage deletion is source of truth, S3 orphans are invisible to users -> orphan persistence unnecessary
- Result: Orphan persistence eliminated at principle level

#### Mechanism 3: Operational Constraints Section

Before architecture decisions, document runtime parameters that constrain design:

```
## Operational Constraints
- WebSocket outgoing_queue_size: 64 (Nakama default)
- DB max_connections: 100 (PostgreSQL)
- S3 DeleteObjects: max 1000 keys per call
- Goroutine pool: recommend bounded (100-500)
```

**Retrospective application**: If `outgoing_queue_size: 64` was documented, "Op6*N broadcast for 1900 assets" would be flagged as impossible at design time.

### Layer 2: Phase Validation in /sc:implement (Catches issues early)

**What**: Add phase boundary validation loop to implement.md `<flow>`.

```
After each Phase completion:
  1. Build: Compile/start, verify basic functionality
  2. Run: Execute with representative data if possible
  3. Validate: "Does this Phase's result already solve the next Phase's problem?"
  4. Decide: If next Phase is redundant, mark as skipped with reason
  5. Checkpoint: Present results to user, confirm proceeding
```

**Retrospective application**:
- Phase 1 (worker pool) complete -> build+run -> "Queue+retry self-regulates. Circuit breaker needed?" -> Skip Phase 3a
- Phase 2 (batch opcode) complete -> first run -> outgoing_queue_size exceeded -> immediate fix (Op7 broadcast)
- Phase 2 complete -> "Batch reduces 1000->5 messages. Backpressure needed?" -> Skip Phase 3b

### Layer 3: Workflow Gate Updates (Process enforcement)

**What**: Update RULES.md workflow_gates to include /sc:design and simplicity checkpoints.

```
Proposed workflow_gates:
  /sc:brainstorm -> /sc:design: User approves discovery spec before designing
  /sc:design -> necessity-check: Each component passes 3-question test
  /sc:design -> /sc:plan: Design spec committed (core decisions only)
  /sc:plan -> /sc:implement --plan: Plan document committed to repo
  /sc:implement -> phase-validate: Each phase: build -> run -> validate -> decide next
  /sc:implement -> /sc:test: Implementation complete
  /sc:test -> done: Test pass evidence required (actual output, not claims)
```

**Additional changes**:
- Add `--scope phase` to /sc:review for mid-implementation review capability
- Update design.md `<handoff>` to include simplicity-coach as suggested next step
- Update simplicity-coach description to include "design spec 작성 후 과잉 설계 필터링" keyword

## 4. New Rule: [R18] Necessity Test

```
[R18] Necessity Test 🟡: before designing a component, answer: "Is the system broken without this?"
  — "Safer/better" alone is insufficient justification for detailed design
  — Require: specific failure scenario, or quantitative evidence, or user-facing impact
  — "Deferred to post-MVP review" is a valid design decision
```

**Examples for RULES.md**:

| Scenario | Wrong | Right | Rule |
|----------|-------|-------|------|
| Designing circuit breaker for in-process worker | "Good practice for resilience" | "Queue(500)+retry(3) already self-regulates. Defer." | Necessity Test 🟡 |
| Adding orphan cleanup when source-of-truth already deleted | "Data might be inconsistent" | "Principle says Storage=SoT. Orphans invisible. Defer." | Necessity Test 🟡 |
| Adding backpressure when batch already reduces load 200x | "Defense in depth" | "1000->5 messages. Threshold=5 would never trigger. Defer." | Necessity Test 🟡 |

## 5. Files to Change

| File | Change | Priority |
|------|--------|----------|
| `src/superclaude/commands/design.md` | Add Necessity Gate (3Q test), Principle Consequence step, Operational Constraints section to `<flow>` | P1 |
| `src/superclaude/core/RULES.md` | Add [R18] Necessity Test rule + examples; update workflow_gates | P1 |
| `src/superclaude/commands/implement.md` | Add Phase Validation Loop to `<flow>` | P2 |
| `src/superclaude/commands/review.md` | Add `--scope phase` to `<syntax>` and examples | P2 |
| `src/superclaude/commands/design.md` | Update `<handoff>` to include simplicity-coach | P3 |
| `src/superclaude/skills/simplicity-coach/SKILL.md` | Add "design 후 과잉 설계 필터링" to description keywords | P3 |

## 6. Expected Impact

| Metric | Before | After (estimated) |
|--------|--------|-------------------|
| Design spec bloat | 44KB (57% waste) | ~15KB (core only) |
| Token waste on over-design | ~90K | ~10K (necessity test + constraints check) |
| Runtime bugs from missing constraints | 2/3 discoverable | 0 (operational constraints section) |
| Phase skip opportunity | None (all-or-nothing) | Per-phase decide (skip when solved) |
| simplicity-coach discoverability | Zero (never invoked) | Suggested in design handoff |

## 7. Implementation Phases

### Phase 1: design.md + RULES.md (highest ROI)
- Add 3 mechanisms to design.md flow
- Add [R18] to RULES.md core_rules
- Update workflow_gates to include /sc:design
- **Verification**: Review design.md flow for completeness; run test_command_structure.py

### Phase 2: implement.md + review.md (feedback loop)
- Add Phase Validation Loop to implement.md
- Add `--scope phase` to review.md
- **Verification**: Run test_command_structure.py

### Phase 3: Discoverability (simplicity-coach)
- Update design.md handoff
- Update simplicity-coach description keywords
- **Verification**: Deploy and test keyword matching

## 8. Risks

| Risk | Mitigation |
|------|-----------|
| Necessity Gate adds friction to small projects | Keep as soft guidance ("recommended for >3 components"), not hard block |
| Phase Validation slows implementation | Only triggers at phase boundaries; skip for single-phase work |
| False negatives (gate passes something that should be deferred) | simplicity-guide at review remains as safety net |
| Rule [R18] too vague | Concrete examples in RULES.md teach better than abstract rules |

## 9. Retrospective Origin

This spec is derived from a real-world retrospective (`oasis-nakama-dev/bulk-asset-delete`). Every proposed improvement maps directly to an observed failure. No speculative additions.

| Improvement | Observed Failure | Section |
|-------------|-----------------|---------|
| 3-Question Necessity Test | 4/7 components scrapped | Retro §2-1, 2-2, 2-3 |
| Principle Consequence | "Storage=SoT" principle contradicted orphan design | Retro §4 Lesson 3 |
| Operational Constraints | outgoing_queue_size not checked | Retro §4 Lesson 2 |
| Phase Validation | 3 runtime bugs on first run | Retro §4 Lesson 4 |
| Workflow gate update | simplicity-coach never invoked | Retro §7 |
| Design budget guidance | 44KB spec, 57% waste | Retro §4 Lesson 5 |
