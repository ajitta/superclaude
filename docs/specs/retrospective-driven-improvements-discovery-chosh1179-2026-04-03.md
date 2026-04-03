---
status: implemented
revised: 2026-04-03
---

# SuperClaude Retrospective-Driven Improvements — Discovery Spec

**Source**: `2026-04-03-superclaude-session-retrospective-chosh1179.md` (Bulk Delete Hardening session)
**Method**: Sequential thinking (8 steps) + Verbalized sampling (5 perspectives, VS-CoT)

---

## Problem Statement

A real-world session revealed 7 systemic issues where SuperClaude's existing gates and rules failed to prevent:
1. Fabricated justification (scenarios constructed to support pre-made conclusions)
2. Simplicity-coach applied post-hoc instead of pre-gate
3. Action bias ("adjust" treated as "change" instead of "review")
4. Real problems missed (code-focus over infra/UX concerns)
5. Flag overload (8 flags for a discussion session)
6. Unverified numbers (estimates presented as facts)
7. Sequential thinking loops (same conclusion repeated 3×)

**Key insight**: SuperClaude has the right tools (simplicity-coach, confidence-check, [R18], [R13]) but they fire at the wrong time. **Gate timing > Gate existence.**

---

## Gap Analysis

| Existing Gate | Current Scope | Gap |
|--------------|---------------|-----|
| [R13] Intent Verification | >3 steps, ambiguous scope | Missing ambiguous verb vocabulary |
| [R18] Necessity Test | "before designing a component" | Too narrow — doesn't cover ad-hoc proposals in discussion |
| Confidence-check skill | User-triggered only | Not wired as automatic pre-gate |
| Simplicity-coach | Post-implementation review | Should be pre-implementation gate |
| FLAGS.md | Lists all flags | No session-type recommendations |
| (none) | — | No evidence-source attribution rule |

---

## Proposed Improvements (4 changes)

### P1. Expand [R13] Intent Verification — Add Ambiguous Verb List

**File**: `src/superclaude/core/RULES.md`
**Type**: Rule expansion
**Addresses**: Issue #3 (Action bias)

Current:
```
[R13] Intent Verification 🔴: before non-trivial work (>3 steps, ambiguous scope, 
or new task direction), restate user's intent in 1-2 sentences and confirm. 
Skip for: single-file edits, explicit file paths, continuation of confirmed plan.
```

Proposed addition:
```
Ambiguous verbs requiring intent confirmation: adjust/재조정, improve, optimize, 
strengthen, refactor, clean up, modernize — these may mean "review" not "change."
```

**Rationale**: The retrospective showed "재조정" (readjust) was interpreted as "change the value" when the user meant "review whether the value is appropriate." A vocabulary trigger list prevents this class of misinterpretation.

---

### P2. Expand [R18] Necessity Test — Broaden Scope + Promote Priority

**File**: `src/superclaude/core/RULES.md`
**Type**: Rule expansion
**Addresses**: Issues #2 (simplicity-coach timing), #4 (missed real problems)

Current:
```
[R18] Necessity Test 🟡: before designing a component, answer "Is the system broken 
without this?" — "safer/better" alone is insufficient.
```

Proposed change:
```
[R18] Necessity Test 🔴: before proposing any code change, answer "Is the system 
broken without this?" — "safer/better" alone is insufficient. Require: specific failure 
scenario, quantitative evidence, or user-facing impact. Check infra/config/settings 
before code. "Deferred to post-MVP review" is a valid design decision.
Skip for: explicit code-change requests with specific file paths, confirmed plan items.
```

**Key changes**:
- Scope: "designing a component" → "proposing any code change"
- Priority: 🟡 → 🔴
- Added: "Check infra/config/settings before code" (infra-before-code principle absorbed here)
- Added skip conditions to prevent friction on explicit requests

**Rationale**: [R18] was too narrowly scoped to "component design" — it didn't apply during analysis sessions where ad-hoc code changes were proposed. The infra-before-code check absorbs what would otherwise be a separate [R20] rule, keeping rule count minimal.

---

### P3. New Rule [R19] Evidence-First

**File**: `src/superclaude/core/RULES.md`
**Type**: New rule
**Addresses**: Issues #1 (fabricated justification), #6 (unverified numbers)

```
[R19] Evidence-First 🔴: numbers and metrics must cite source (code line, config value, 
measurement, or doc). Estimates prefixed with "~" or "약/approx". Never construct 
hypothetical failure scenarios to justify a pre-existing recommendation — evidence 
must precede proposals, not follow them.
Skip for: well-known framework defaults, official documentation quotes.
```

**Rationale**: The retrospective showed two manifestations of missing evidence discipline:
1. "10000개 삭제 → 8000개 drop" — a fabricated scenario to justify a batch-size reduction
2. "drain rate ≈ 150 items/2s" — an estimate presented as a definitive number

This rule attacks the root: conclusions must follow evidence, not the reverse.

---

### P4. Session-Type Flag Profiles in FLAGS.md

**File**: `src/superclaude/core/FLAGS.md`
**Type**: New section
**Addresses**: Issue #5 (flag overload)

```xml
<session_profiles note="Recommended flag sets — avoid loading execution flags in analysis sessions">
| Session Type | Recommended | Avoid | Rationale |
|-------------|-------------|-------|-----------|
| Analysis/Discussion | --seq --tavily --c7 | --delegate --loop --parallel | Sequential dialogue, no parallel work |
| Implementation | --delegate --serena --loop | (none) | Parallel execution, code-centric |
| Debug/Troubleshoot | --seq --serena --c7 | --delegate --loop | Sequential diagnosis, symbolic exploration |
| Research | --tavily --c7 --seq | --delegate --serena | Web-centric, no code changes |
| Review/Audit | --serena --seq | --delegate --loop | Read-only, systematic |
</session_profiles>
```

**Rationale**: The retrospective session used 8 flags including `--delegate auto`, `--loop`, `--parallel` for what was fundamentally an analysis/discussion session. This table provides quick guidance without being prescriptive.

---

## Deferred (Not Proposed)

| Idea | Why Deferred |
|------|-------------|
| [R20] Infra-Before-Code as separate rule | Absorbed into expanded [R18] — one rule, not two |
| Simplicity pre-gate in implement.md | [R18] expansion covers this; flow changes are higher risk |
| Sequential thinking loop detection | Too tool-specific for a framework rule; add as gotcha if pattern recurs |
| Auto-flag recommendation in context_loader.py | Requires Python code changes; session-type table is sufficient for now |
| "Default to SKIP" meta-principle | Too abstract to enforce; [R18] expansion is the concrete version |
| confidence-check auto-trigger | Requires hook infrastructure; user-triggered is sufficient |

---

## Verbalized Sampling Summary

| # | Perspective | Probability | Changes | Coverage |
|---|-----------|-------------|---------|----------|
| 1 | Minimalist | p=0.30 | 3 edits, 0 new rules | 3/7 issues |
| 2 | Rule Architect | p=0.25 | 2 edits + 2 new rules | 7/7 issues |
| 3 | Workflow Engineer | p=0.20 | 4 command flow edits | 4/7 issues |
| 4 | Context Engineer | p=0.15 | Python code changes | 1/7 issues |
| 5 | Radical Simplifier | p=0.10 | 1 new principle | 7/7 (theoretical) |

**Selected blend**: P1 (expand existing) + selective P2 (one new rule, not two)
→ 2 rule expansions + 1 new rule + 1 new FLAGS section = **4 changes, all 7 issues addressed**

---

## Implementation Estimate

- **Files changed**: 2 (`RULES.md`, `FLAGS.md`)
- **Lines added**: ~25
- **Lines modified**: ~10
- **Test risk**: Zero (docs-change-safe)
- **RULES.md size impact**: 124 → ~140 lines (+13%)

---

## Validation Plan

1. Review expanded [R13] and [R18] for skip-condition adequacy (no false positives on explicit requests)
2. Verify [R19] wording prevents fabrication without blocking legitimate estimation
3. Check session-type table covers common SuperClaude usage patterns
4. Run `uv run pytest` to confirm no test impact
5. Apply improvements in a real session and compare against retrospective failure patterns

---

## Decision Required

**User to select implementation scope:**

#### [1] Full (recommended) ★
All 4 proposals: P1 + P2 + P3 + P4

#### [2] Conservative
P1 + P2 only (expand existing rules, no new rules)

#### [3] Minimal
P4 only (session-type flag profiles — zero rule changes)

#### [4] Custom
Select specific proposals: P1, P2, P3, P4

select: 1, 2, 3, 4, or type your own

---

## Spec Panel Review (6 experts, 10-step sequential analysis)

### Expert Verdicts

| Expert | Focus | P1 | P2 | P3 | P4 | Key Issue |
|--------|-------|----|----|----|----|-----------|
| **Hickey** | Essential complexity | ✅ | ⚠️ | ⚠️ | ✅ | P1+P2+P3 attack same root cause — consider merging |
| **Beck** | Testability | ✅ | ⚠️ | ❌ | ✅ | P3 anti-fabrication clause is untestable |
| **Osmani** | AI executability | ✅ | ⚠️ | ⚠️ | ✅ | P2 scope too broad → gate fatigue; P3 dual-clause |
| **Fowler** | Separation of concerns | ⚠️ | ⚠️ | ⚠️ | ✅ | Overlapping triggers, duplicated skip conditions |
| **Nygard** | Failure modes | ✅ | ⚠️ | ❌ | ✅ | P2+P3 risk compliance theater |
| **Majors** | Observability | ⚠️ | ⚠️ | ⚠️ | ✅ | Zero observability for rule compliance |

### Consensus Findings

**P1 (R13 verb list)** — ✅ Ship as-is. Unanimous approval. Testable, LLM-parseable, low-risk.

**P4 (session profiles)** — ✅ Ship as-is. Orthogonal, self-documenting, graceful degradation.

**P2 (R18 expansion)** — ⚠️ Revise scope before shipping:
- **Problem**: "before proposing any code change" is too broad. Every code response triggers the gate → gate fatigue → compliance theater (Osmani, Nygard)
- **Fix**: Narrow to "any *unsolicited* code change" (changes the model proposes, not ones the user explicitly requests)
- **Add**: Execution order: R13 (intent) → R18 (necessity) → R19 (evidence). Rationale: can't assess necessity before understanding intent (Fowler)

**P3 (R19 Evidence-First)** — ❌ Revise significantly:
- **Problem 1**: "Never construct hypothetical failure scenarios" is untestable (Beck) and unenforceable (Nygard). The model doesn't know when it's fabricating.
- **Problem 2**: Two unrelated clauses in one rule — source citation + anti-fabrication (Osmani)
- **Fix**: Split. Keep the testable half as the rule: "Numbers/metrics must cite source type [code|config|measurement|doc|estimate]." Move anti-fabrication to a gotcha/example: "Anti-pattern: constructing scenarios to justify a pre-existing recommendation."

**Coverage gap**: Issue #7 (sequential thinking loops) is not addressed by any proposal:
- **Add P5**: seq-loop gotcha to --seq-using commands (brainstorm, analyze, troubleshoot)
- Text: "seq-loop: Same conclusion reached twice on same question → terminate that analysis branch and proceed."

### Revised Proposals (post-panel)

#### P1 (unchanged)
```
[R13] ... Ambiguous verbs requiring intent confirmation: adjust/재조정, improve, 
optimize, strengthen, refactor, clean up, modernize — may mean "review" not "change."
```

#### P2 (revised — scope narrowed)
```
[R18] Necessity Test 🔴: before proposing any unsolicited code change, answer "Is the 
system broken without this?" — "safer/better" alone is insufficient. Require: specific 
failure scenario, quantitative evidence, or user-facing impact. Check infra/config/settings 
before code. "Deferred to post-MVP review" is a valid design decision.
Unsolicited = model-initiated, not user-requested. Skip for: explicit change requests, 
confirmed plan items. Execution order: R13 → R18 → R19.
```

#### P3 (revised — split into rule + gotcha)

Rule:
```
[R19] Evidence-First 🔴: numbers and metrics must cite source type 
[code|config|measurement|doc|estimate]. Estimates prefixed with "~" or "약/approx".
Skip for: well-known framework defaults, official documentation quotes.
```

Gotcha (add to relevant commands):
```
evidence-fabrication: Do not construct hypothetical failure scenarios to justify a 
pre-existing recommendation. Evidence must precede proposals, not follow them.
```

#### P4 (unchanged)
Session-type flag profiles table in FLAGS.md.

#### P5 (new — from coverage gap)
Gotcha for --seq-using commands:
```
seq-loop: If sequential thinking reaches the same conclusion twice on the same question, 
terminate that analysis branch and move to next topic.
```

### Final Scorecard

| Proposal | Status | Issues Addressed | Risk |
|----------|--------|-----------------|------|
| P1 R13 verb list | Ship | #3 | Low |
| P2 R18 narrowed scope | Ship (revised) | #2, #4 | Low (was Medium) |
| P3 R19 format req + gotcha | Ship (revised) | #1, #6 | Low (was High) |
| P4 Session profiles | Ship | #5 | Low |
| P5 seq-loop gotcha | Ship (new) | #7 | Low |

**Coverage**: 7/7 issues addressed (up from 6/7)
**Files**: RULES.md, FLAGS.md + gotcha edits to 3 commands
**RULES.md growth**: ~12 lines (+10%)
**Loop iterations**: 1 (self-eval caught Issue #7 gap)
