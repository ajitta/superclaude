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

| Source | Finding | Reference |
|--------|---------|-----------|
| Anthropic docs (prompting tips) | "Prefer general instructions over prescriptive steps" | platform.claude.com/docs/en/.../claude-prompting-best-practices |
| Anthropic docs (adaptive thinking) | "large or complex system prompts" cause excessive thinking | platform.claude.com/docs/en/.../adaptive-thinking |
| Anthropic docs (migration) | "dial back aggressive language" — models may overtrigger | platform.claude.com/docs/en/.../claude-prompting-best-practices |
| Anthropic docs (context engineering) | "hardcoding complex, brittle logic creates fragility" | anthropic.com/engineering/effective-context-engineering |
| Anthropic docs (right altitude) | "specific enough to guide, flexible enough for heuristics" | anthropic.com/engineering/effective-context-engineering |
| Wharton study (2025) | CoT benefits minimal (+2.9-3.1%) with reasoning models | Meincke et al., "Prompting Science Report 1" (March 2025) |
| SP skills analysis (local) | 63+ HOW prescriptions, 7 HARD GATES, 25+ behavioral mandates | Analysis of ~/.claude/plugins/.../superpowers/5.0.2/skills/ |

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
- Remove the entire SP conditional block in model_routing (lines 41-45: "When superpowers
  workflow active..." through "SC model_routing applies only to /sc: commands"). Leave only
  the SC-native routing table (opus/sonnet/haiku assignments). SC owns all routing.

#### 12 Skill Rewrites

Each skill is rewritten from scratch following the Opus 4.6-native template.

**Format decision:** The 12 SP-ported skills use plain markdown (not the XML `<component>`
convention from `.claude/rules/skill-authoring.md`). This is intentional — these skills are
Claude Code skills loaded via the skills system, not SC agent/command definitions. The
skill-authoring.md XML convention applies to SC-native skills that use `<component type="skill">`;
the SP-ported skills follow the simpler agentskills.io markdown format which Claude Code
natively supports. Both formats are valid per Claude Code's skill loading mechanism.

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
- KEEP: Instruction priority list (User > Superpowers > SuperClaude > Default) — this is a
  WHAT instruction about authority, not a HOW thinking prescription
- REMOVE: 11 forbidden thought patterns table, "1% threshold", "NOT NEGOTIABLE", "ABSOLUTELY MUST"
- REMOVE: SP deference logic in body (coexistence handled at install-time only)
- REMOVE: Red flags rationalization table
- ADD: Brief note that when SP is also installed, SP skills take precedence for overlapping names
- NOTE: The extensive shared skill tables and coexistence documentation (current lines 41-137)
  are replaced by a single line about install-time precedence

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

**Note:** The underlying WHAT-NOT rule may still be valid even when aggressive language is
removed. E.g., "Do not implement before design is approved" is a valid WHAT-NOT constraint;
only the "HARD-GATE" wrapper and "MUST" enforcement are softened.

### Path Conventions

Skills that reference `docs/superpowers/` paths (brainstorming saves specs to
`docs/superpowers/specs/`, writing-plans saves to `docs/superpowers/plans/`) retain these
paths. Changing them would break SP compatibility for users who switch between SP and SC.
This is a documentation path, not a behavioral dependency.

### Test Impact

| Category | Impact | Action |
|----------|--------|--------|
| Frontmatter validation | No change | Keep |
| SP name compatibility | No change (names identical) | Keep |
| Body content length (>200 chars) | Skills will be shorter but still >200 chars at 30-80 lines | Verify, adjust if needed |
| FORK_CONTEXT_SKILLS | `requesting-code-review` stays in set (still uses context: fork) | No change |
| `test_rules_has_skill_priority` | Will FAIL — `skill_priority` section is being removed | **Update test: remove this assertion** |
| `test_rules_has_workflow_gates` | May need updating — workflow_gates is simplified | **Update test: check for simplified gates** |
| `test_workflow_gates_mention_key_skills` | May need updating — fewer skills referenced in gates | **Update test** |
| **New: no aggressive language** | — | **Add test** |

New test: validate that no skill contains `ABSOLUTELY MUST`, `IRON LAW`, `NOT NEGOTIABLE`,
`VIOLATING LETTER`, or `EXTREMELY_IMPORTANT`.

### Token Budget Impact

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| 12 skills total lines | 2,089 | ~575 | 72% reduction |
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
