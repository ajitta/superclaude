# SuperClaude Opus 4.6 Alignment — Design Spec

**Date:** 2026-03-15
**Branch:** `feature/content-framework-upgrade`
**Status:** Approved (brainstorming complete)

## Problem Statement

Anthropic's official guidance for Opus 4.6 states:

> "Prefer general instructions over prescriptive steps. A prompt like 'think thoroughly'
> often produces better reasoning than a hand-written step-by-step plan. Claude's reasoning
> frequently exceeds what a human would prescribe."
> — docs.anthropic.com, Prompting Best Practices

The `feature/content-framework-upgrade` branch ported 12 Superpowers (SP) v5.0.2 process
skills into SuperClaude. These skills contain 63+ "HOW to think" prescriptions and aggressive
enforcement language that conflicts with Opus 4.6's adaptive thinking. Additionally, master
already contains thinking prescriptions in core files (diagnosis rule, thinking_strategy).

## Research Evidence

| Source | Finding |
|--------|---------|
| Anthropic docs (prompting tips) | "Prefer general instructions over prescriptive steps" |
| Anthropic docs (adaptive thinking) | "large or complex system prompts" cause excessive thinking |
| Anthropic docs (migration) | "dial back aggressive language" — models may overtrigger |
| Anthropic docs (context engineering) | "hardcoding complex, brittle logic creates fragility" |
| Anthropic docs (right altitude) | "specific enough to guide, flexible enough for heuristics" |
| Wharton study (2025) | CoT benefits minimal (+2.9-3.1%) with reasoning models, adds 20-80% time |
| YouTube review (Feb 2026) | "opus 4.6 has closed that gap... frameworks getting less relevant" |
| SP skills analysis (Agent 2) | 63+ HOW prescriptions, 7 HARD GATES, 25+ behavioral mandates |

## Classification Framework: 3-Bucket Test

Every instruction is classified into one of three buckets:

### WHAT (Keep)
- **Test:** "Does this tell Claude what action to take or what outcome to produce?"
- **Examples:** "Run tests before claiming done", "Create feature branch", "Present 2-3 options"

### HOW (Remove or Generalize)
- **Test:** "Does this tell Claude how to structure its internal reasoning?"
- **Examples:** "Generate 3+ hypotheses", "Trace data flow backward", "Form single hypothesis"
- **Transform:** HOW → WHAT by stating the outcome, not the reasoning process
  - "Generate 3+ hypotheses ranked by simplicity" → "Investigate root cause before proposing fixes"

### WHAT-NOT (Keep, Soften Language)
- **Test:** "Does this prevent a known failure mode?"
- **Examples:** "Don't claim done without evidence", "Don't skip TDD for simple changes"
- **Soften:** Remove aggressive enforcement language per Anthropic migration guidance

## Coexistence Model Simplification

### Current: 3-Layer (overly complex)
1. Install-time dedup (skip overlapping skills when SP present)
2. Content-time harmonization (core files defer to SP)
3. Skill sync (skill content aligned with SP upstream)

### New: 1-Layer (minimal)
1. **Install-time dedup only** (unchanged `install_components.py` logic)

Rationale: SP installed → SP skills used. SP not installed → SC-native skills used. No runtime
content conflicts possible. SC core files own their behavior, no SP deference.

## Phase 1: Clean Rewrite (This Branch)

### Scope

#### Core File Fixes (uncommitted changes)

**RULES.md:**
- Revert `workflow_gates` to simple 4-stage: brainstorm → plan → execute → verify
- Remove `note="enforce progression (superpowers-compatible superset)"`
- Remove `skill_scope` section entirely (Right-Altitude principle covers this)
- Remove `skill_priority` numbered list (Opus 4.6 judges which skill applies)

**PRINCIPLES.md:**
- Remove `Invoke-Eagerly` line (conflicts with Right-Altitude and Restraint-First)

**FLAGS.md:**
- Remove SP deference block in model_routing (SC owns its routing)

#### 12 Skill Rewrites

Each skill is rewritten from scratch following the Opus 4.6-native template:

```markdown
---
name: skill-name
description: When to use this skill and what it does
---

## Purpose
One sentence.

## Workflow
3-7 numbered WHAT steps.

## Constraints
2-5 bullet WHAT-NOT rules.

## Completion
How to know you're done.

## Next
Handoff to next skill.
```

##### Per-Skill Specifications

**1. brainstorming (~60 lines)**
- KEEP: Explore context → ask questions → propose approaches → present design → write spec → review
- KEEP: Spec review loop (dispatch reviewer subagent)
- KEEP: Visual companion offer
- REMOVE: 9 thinking prescriptions (scope assessment methodology, complexity scaling, design thinking method)
- REMOVE: "HARD-GATE" and "MUST create a task for each" language

**2. writing-plans (~50 lines)**
- KEEP: File structure mapping, bite-sized task granularity (2-5 min), plan review loop
- REMOVE: Decomposition thinking, architectural reasoning, capacity reasoning, cohesion thinking
- REMOVE: "assume engineer has zero context and questionable taste"

**3. executing-plans (~40 lines)**
- KEEP: Load plan → mark progress → follow steps → stop on blocker → handoff
- REMOVE: Critical analysis stance prescription, escalation judgment prescription
- SIMPLIFY: Blocker handling to "stop and ask" instead of detailed decision framework

**4. test-driven-development (~60 lines)**
- KEEP: RED → GREEN → REFACTOR cycle, 3 exception categories (refactoring, legacy, config)
- REMOVE: 8 thinking prescriptions, rationalization prevention table (30 lines), cognitive bias framing
- REMOVE: "Delete it. Start over." mandatory reset, "VIOLATING LETTER = VIOLATING SPIRIT"
- SOFTEN: "NO PRODUCTION CODE WITHOUT FAILING TEST" → "Write a failing test before implementation"

**5. systematic-debugging (~50 lines)**
- KEEP: Reproduce → investigate → fix → verify cycle
- KEEP: "After 3+ failed fixes, reconsider your approach" (WHAT-NOT, not HOW)
- REMOVE: 10 thinking prescriptions (4-phase framework, backward tracing, hypothesis formulation)
- REMOVE: Red flag thought patterns list, "VIOLATING LETTER" language

**6. verification-before-completion (~35 lines)**
- KEEP: Run verification → read output → confirm before claiming
- REMOVE: 5-step cognitive gate function, red flag thought patterns
- REMOVE: "If you lie, you'll be replaced", "non-negotiable"
- SIMPLIFY: To "run the command, read the output, then make the claim"

**7. requesting-code-review (~40 lines)**
- KEEP: Get diff → dispatch reviewer → triage by severity → fix critical
- REMOVE: Context crafting reasoning, mental separation prescription

**8. receiving-code-review (~50 lines)**
- KEEP: Understand → verify technically → implement or push back → test
- REMOVE: 6 thinking prescriptions, cognitive verification method
- REMOVE: Forbidden phrases list ("Great point!", etc.) — trust Opus 4.6 judgment
- KEEP (soften): "Evaluate feedback technically before implementing" (WHAT-NOT)

**9. finishing-a-development-branch (~50 lines)**
- KEEP: Run tests → present 4 options (merge/PR/keep/discard) → execute → cleanup
- REMOVE: Branch topology reasoning prescription
- KEEP: Test gate ("tests must pass before proceeding")

**10. dispatching-parallel-agents (~45 lines)**
- KEEP: Identify independent tasks → dispatch per domain → review & integrate
- REMOVE: Categorization method, independence reasoning, debugging philosophy prescriptions

**11. using-git-worktrees (~45 lines)**
- KEEP: Check dirs → verify .gitignore → create worktree → setup → baseline test
- REMOVE: Directory selection reasoning method, safety reasoning prescription

**12. using-superclaude (~50 lines)**
- REWRITE as SC-native meta-skill (not SP complementary mode)
- KEEP: SC features overview, skill invocation method, /sc: command usage
- REMOVE: 11 forbidden thought patterns, "1% threshold", "NOT NEGOTIABLE", "ABSOLUTELY MUST"
- REMOVE: SP deference logic (handled at install-time only)
- ADD: Brief note that when SP is also installed, SP skills take precedence for overlapping names

### Language Policy

| SP Language | SC-Native Replacement |
|-------------|----------------------|
| `ABSOLUTELY MUST` | `should` |
| `IRON LAW` | `principle` or remove |
| `NOT NEGOTIABLE` | remove |
| `VIOLATING LETTER = VIOLATING SPIRIT` | remove |
| `If you lie, you'll be replaced` | remove |
| `HARD GATE` / `MANDATORY` | `recommended` or `before proceeding` |
| `You MUST create a task for each` | `Track progress with tasks` |
| `EXTREMELY_IMPORTANT` | remove |

### Test Impact

| Category | Impact | Action |
|----------|--------|--------|
| Frontmatter validation | No change | Keep |
| SP name compatibility | No change (names identical) | Keep |
| Body content length | Minimum threshold may need lowering | Adjust |
| FORK_CONTEXT_SKILLS | Review per skill | Check |
| **New: no aggressive language** | — | **Add test** |

New test: validate that no skill contains `ABSOLUTELY MUST`, `IRON LAW`, `NOT NEGOTIABLE`,
`VIOLATING LETTER`, or `EXTREMELY_IMPORTANT`.

### Token Budget Impact

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| 12 skills total lines | ~1,848 | ~575 | 69% reduction |
| Core files (branch additions) | +700B | ~+200B | 71% reduction |
| On-demand context per skill invocation | 100-253 lines | 30-80 lines | ~60% reduction |

## Phase 2: Master Thinking Prescription Fix (Separate Branch)

**Target:** `fix/opus46-core-alignment`

| File | Current (master) | Target |
|------|-----------------|--------|
| RULES.md L29 | `Diagnosis: generate 3+ hypotheses ranked by simplicity...` | `Diagnosis: investigate root cause before proposing fixes` |
| PRINCIPLES.md L16-21 | `<thinking_strategy>` section (5 lines) | Delete entirely |
| PRINCIPLES.md `<decisions>` | `Diagnosis: 3+ hypotheses \| environment before code...` | `Diagnosis: investigate thoroughly, verify assumptions` |

## Phase 3: Role Redefinition (Future Project)

**Vision:** SuperClaude transitions from "behavioral framework" to "context + integration layer."

| Layer | Role | Always Loaded? |
|-------|------|---------------|
| Workflow Router | Minimal WHAT gates (~500B) | Yes |
| Reference Skills | Detailed guides (on-demand, not forced) | No |
| Context Layer | MCP integration, memory, project state | Selective |

Phase 3 is a separate brainstorming session. Not in scope for this spec.

## Memory Updates Required

- `project_superpowers-coexistence.md`: Rewrite from 3-layer to 1-layer model
- `project_content-framework-upgrade.md`: Add Phase 1 Opus 4.6 alignment work

## Success Criteria

1. All 12 skills rewritten to Opus 4.6-native template (30-80 lines each)
2. No skill contains aggressive enforcement language (automated test)
3. Core file branch additions simplified (no SP deference, no thinking prescriptions)
4. All existing tests pass (1523+)
5. New aggressive-language-absence test passes
6. Total skill lines reduced by ~60%+
