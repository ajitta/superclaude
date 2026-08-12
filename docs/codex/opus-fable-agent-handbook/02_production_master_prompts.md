# Production Master Prompts

복사해 사용할 수 있는 Decision, Research, Coding, Long-running Agent 템플릿입니다. 대괄호의 placeholder를 실제 값으로 교체하고, 필요 없는 블록은 삭제하세요.

> 모델 표기: `Claude Opus 5`(2026-07-24 출시)와 `Claude Fable 5`(2026-06-09 출시)는 **둘 다 공개 확인된 모델**입니다.
> 아래의 모델별 “조정” 블록은 여전히 `[Heuristic]`입니다 — 모델의 존재는 확인됐지만 조정의 효과는 workload eval로 확인해야 합니다.

## 0. 공통 Task Contract

**[Framework]** 복합 작업의 공통 kernel:

```text
<intent>
[이 결과가 어떤 실제 결정이나 행동을 가능하게 해야 하는가]
</intent>

<objective>
[완료 후 관찰 가능한 무엇이 달라져 있어야 하는가]
</objective>

<context>
[판단을 바꾸는 현재 상태, 사실, 자원, 환경, 시간 범위]
</context>

<constraints>
<hard>
- [절대 위반하면 안 되는 조건]
</hard>

<preferences>
- [충돌하지 않을 때 최적화할 조건]
</preferences>
</constraints>

<priorities>
충돌 시:
1. [우선순위]
2. [우선순위]
3. [우선순위]
</priorities>

<authority>
[모델이 스스로 수행할 수 있는 조사·결정·변경]
[사용자 승인 또는 escalation이 필요한 행동]
</authority>

<uncertainty>
확인 가능한 것은 context/tools로 조사한다.
영향이 작고 되돌릴 수 있는 것은 합리적으로 가정한다.
결론을 크게 바꾸는 가정은 명시한다.
영향이 크거나 비가역적인 행동은 질문한다.
</uncertainty>

<success_criteria>
- [실제 상태로 판정 가능한 완료 조건]
</success_criteria>

<output>
[사용할 결과 형식]
</output>
```

---

# 1. Decision Master Prompt

**[Framework]** 의사결정은 멋진 분석이 아니라 더 나은 선택을 만드는 작업입니다.

```text
<intent>
This analysis exists to help [DECISION MAKER]
decide whether/how to [REAL DECISION].

The goal is not to produce an impressive analysis.
The goal is to improve the quality of the decision.
</intent>

<decision>
The decision to make is:

[EXACT DECISION]

Possible outcomes, if applicable:
- [OPTION A]
- [OPTION B]
- [OPTION C]
</decision>

<context>
Relevant situation:

[CURRENT FACTS]
[CURRENT STATE]
[AVAILABLE RESOURCES]
[TIME HORIZON]
[KNOWN RISKS]
</context>

<constraints>
<hard>
- [NON-NEGOTIABLE CONSTRAINT]
- [NON-NEGOTIABLE CONSTRAINT]
</hard>

<preferences>
When compatible with the hard constraints:
- [PREFERENCE]
- [PREFERENCE]
</preferences>
</constraints>

<priorities>
When objectives conflict, prioritize:

1. [PRIORITY]
2. [PRIORITY]
3. [PRIORITY]
</priorities>

<authority>
Choose the analytical method and order of investigation.

Resolve questions independently when the supplied context or
available tools can answer them.

Do not take consequential external action unless explicitly
authorized.
</authority>

<uncertainty>
Distinguish:
- confirmed facts;
- reasonable inferences;
- assumptions;
- material unknowns.

Do not convert uncertainty into false precision.
Raise missing information only when it could materially change
the decision.
</uncertainty>

<evidence>
For each decision-driving claim, provide:
- the evidence;
- the source or observable basis;
- confidence;
- the strongest relevant counterevidence.
</evidence>

<success_criteria>
A successful result:
- reaches a clear recommendation when evidence permits;
- identifies the strongest support and counterargument;
- exposes assumptions that materially affect the conclusion;
- states what would change the recommendation;
- distinguishes reversible from difficult-to-reverse choices;
- recommends the cheapest useful next step when more evidence
  has meaningful decision value.
</success_criteria>

<output>
## Recommendation
[GO / CONDITIONAL GO / NO-GO or the appropriate choice]

## Why
[decision-driving reasoning]

## Strongest counterargument
[best case against the recommendation]

## Critical assumptions and unknowns
[items that materially affect the result]

## What would change the recommendation
[specific evidence or threshold]

## Next action
[smallest high-value action]
</output>
```

## Decision용 최소 버전

```text
Help [ACTOR] decide [DECISION] within [TIME HORIZON].

Context:
[DECISION-RELEVANT FACTS]

Hard constraints:
- [CONSTRAINT]

Distinguish facts, inferences, assumptions, and unknowns.
Give a recommendation, the strongest evidence for it, the
strongest counterargument, what would change the decision,
and the next action.
```

## Claude Opus 5 조정

**[Heuristic]**

```text
- complete decision specification upfront
- no forced step-by-step analysis
- no default second-agent verifier
- retain source checks and observable outcome checks
```

## Claude Fable 5 조정

**[Framework]**

```text
Add when the task may run for a long time:

<runtime>
Maintain a canonical decision state containing:
- current recommendation;
- confirmed facts;
- unresolved material questions;
- completed research;
- remaining work;
- evidence that changed the decision.

Do not claim completion because the context is long.
Stop when the decision criteria are met, not when every possible
source has been searched.
</runtime>
```

---

# 2. Research Master Prompt

**[Framework]** Research는 자료의 양이 아니라 decision-relevant uncertainty reduction을 최적화합니다.

```text
<intent>
This research exists to help [ACTOR] decide [DECISION].

Its purpose is to reduce the uncertainties most likely to change
that decision, not to produce a comprehensive industry overview.
</intent>

<research_objective>
Determine:

1. [CRITICAL QUESTION]
2. [CRITICAL QUESTION]
3. [CRITICAL QUESTION]
4. [FALSIFIER: evidence that would invalidate the working thesis]
</research_objective>

<known_context>
[KNOWN FACTS]
[CURRENT HYPOTHESES]
[EXISTING EVIDENCE]
[TIME / GEOGRAPHY / PRODUCT SCOPE]
</known_context>

<constraints>
<hard>
- Do not present unsupported estimates as facts.
- Do not mix incompatible markets, dates, cohorts, or definitions.
- Preserve the user's stated scope.
- [TASK-SPECIFIC CONSTRAINT]
</hard>

<preferences>
- Prefer primary and authoritative sources.
- Prefer recent sources when the fact is time-sensitive.
- Prefer decision relevance over breadth.
</preferences>
</constraints>

<source_policy>
Use sources in this order when applicable:

1. primary records, official documentation, laws, filings, datasets;
2. direct company or institutional publications;
3. high-quality independent analysis;
4. secondary summaries for discovery or triangulation.

Do not use a secondary source as the sole support for a material
claim when a primary source is available.
</source_policy>

<evidence_policy>
For every material claim record:

Claim:
Evidence:
Source:
Date:
Confidence:
Limits:
Decision implication:
</evidence_policy>

<contradictions>
When sources disagree:
- verify that they use the same definition, period, geography,
  population, and methodology;
- preserve the disagreement when it cannot be resolved;
- explain which source is more decision-relevant and why.
</contradictions>

<unknowns>
Distinguish:
- not yet researched;
- searched but no reliable evidence found;
- inherently uncertain;
- unavailable within the current access boundary.
</unknowns>

<stop_condition>
Stop when:
- every critical question has enough evidence for a calibrated
  conclusion or has been marked as an explicit unknown;
- additional search is unlikely to change the decision;
- contradictions that matter have been resolved or surfaced;
- the requested deliverable can be produced without pretending
  to know more than the evidence supports.
</stop_condition>

<output>
## Executive answer
[decision-relevant synthesis]

## Findings by critical question
[claim → evidence → source → confidence]

## Contradictions and weak evidence
[unresolved conflicts]

## Material unknowns
[what remains uncertain and why]

## Decision implications
[how the evidence affects the real decision]

## Next research action
[only if it has meaningful information value]
</output>
```

## Evidence Ledger

```text
| ID | Claim | Evidence | Source | Date | Confidence | Limits | Decision impact |
|---|---|---|---|---|---|---|---|
| E1 | ... | ... | ... | ... | high/med/low | ... | ... |
```

## Research branch용 subagent contract

```text
Objective:
[one independent research question]

Boundaries:
[what is in scope and explicitly out of scope]

Source requirements:
[primary/official/recency constraints]

Return only:
1. Conclusion
2. Key evidence with sources
3. Strongest counterevidence
4. Confidence
5. Unknowns
6. Implication for the parent decision

Do not return the full search trace unless requested.
```

## Claude Opus 5 조정

**[Heuristic]**

```text
- provide all critical questions and source constraints upfront
- let the model choose search order
- avoid "verify every claim three times"
- use traceable citations and contradiction checks instead
```

## Claude Fable 5 조정

**[Framework]**

```text
<progress>
Maintain a compact research state:
- critical questions;
- evidence collected;
- contradictions;
- material unknowns;
- remaining work;
- current stop-condition assessment.

Ground progress claims in recorded evidence, not in the amount
of searching performed.
</progress>
```

---

# 3. Coding Agent Master Prompt

**[Framework]** Coding prompt는 구현 설명보다 repository operating contract에 가깝습니다.

```text
<intent>
Prevent [REAL USER OR BUSINESS FAILURE].

Preserve [IMPORTANT EXISTING BEHAVIOR / CONTRACT].
</intent>

<task>
Achieve the following observable behavior:

Given:
[INPUT / TRIGGER / INITIAL STATE]

When:
[EVENT]

Then:
- [REQUIRED BEHAVIOR]
- [REQUIRED BEHAVIOR]
- [INVARIANT]
</task>

<scope>
You may inspect and modify code directly related to:
- [AREA]
- [AREA]
- relevant tests and documentation.

Do not perform unrelated refactors.

If the actual root cause lies outside the expected area, expand
scope only as far as needed to fix the defect correctly.
</scope>

<repository_invariants>
- [PUBLIC API / SCHEMA / MIGRATION RULE]
- [SECURITY OR DATA INTEGRITY RULE]
- [ARCHITECTURAL CONVENTION]
- [SUPPORTED PLATFORM / VERSION]
</repository_invariants>

<constraints>
<hard>
- [NON-NEGOTIABLE]
- Do not weaken, delete, or bypass a valid test to make the suite pass.
- Do not claim completion without observable validation.
</hard>

<preferences>
- Prefer the smallest coherent change.
- Reuse existing abstractions when they fit.
- Avoid a new dependency unless it materially improves the solution.
</preferences>
</constraints>

<authority>
Within scope, independently:
- inspect the repository;
- trace the real execution path;
- choose the implementation;
- edit relevant files;
- run relevant checks;
- fix regressions caused by the change.

Ask before:
- changing a public contract not authorized by the task;
- performing destructive or production actions;
- making a product decision with materially different behavior;
- using credentials or access outside the supplied environment.
</authority>

<ambiguity>
If repository evidence can resolve ambiguity, investigate it.

For low-impact reversible choices, make a reasonable choice and
record it briefly.

Escalate only when materially different outcomes remain possible
and the user is the only reliable source of the decision.
</ambiguity>

<execution>
1. Understand the current behavior and reproduce or trace the issue.
2. Identify the root cause.
3. Implement the smallest coherent fix.
4. Validate the changed behavior and relevant invariants.
5. Inspect the final diff for unintended scope.

These steps define required coverage, not a requirement to expose
private chain-of-thought.
</execution>

<validation>
Use the strongest applicable evidence:
- deterministic checks;
- targeted regression tests;
- existing relevant tests;
- compilation / type checking / linting;
- schema or API compatibility checks;
- observable runtime behavior.

If a validation cannot run, state exactly what was not run and why.
</validation>

<definition_of_done>
The task is complete only when:
- the requested behavior is achieved;
- the root cause, not only the symptom, is addressed;
- hard constraints and repository invariants are preserved;
- relevant validation passes, or remaining failures are accurately
  explained and outside the change;
- the final change contains no unrelated edits.
</definition_of_done>

<final_response>
Report:
1. Outcome
2. Files or behavior changed
3. Validation performed and results
4. Assumptions
5. Remaining risk or blocker, if any
</final_response>
```

## Coding 예시: duplicate payment

```text
<intent>
Prevent customers from being charged twice when a payment request
is retried. Preserve the current public API and successful
single-charge behavior.
</intent>

<task>
When requests with the same idempotency key arrive sequentially or
concurrently:
- create at most one logical payment;
- return the same logical result;
- do not disable safe retry behavior.
</task>

<constraints>
<hard>
- public API unchanged
- existing migrations immutable
- valid tests must not be weakened
</hard>
</constraints>

<definition_of_done>
- a concurrency regression test demonstrates no duplicate payment;
- relevant billing tests pass;
- API compatibility is preserved.
</definition_of_done>
```

## Claude Opus 5 조정

**[Heuristic]**

```text
Keep:
- behavior contract
- invariants
- scope
- executable validation
- completion evidence

Remove by default:
- repeated "think carefully"
- forced self-critique loops
- verifier-agent ceremony without measured benefit
```

## Claude Fable 5 조정

**[Framework]**

```text
Add for long-running implementation:

<checkpoint_policy>
At meaningful milestones, update canonical state with:
- goal and hard constraints;
- confirmed root cause;
- files changed;
- validation already passed;
- remaining work;
- blocker;
- exact next action.

Before declaring completion, compare the task contract against the
actual repository and test state.
</checkpoint_policy>
```

---

# 4. Long-running Agent Master Prompt

**[Framework]**

```text
<goal>
[LONG-HORIZON OUTCOME]
</goal>

<scope>
In scope:
- [AREA]

Out of scope:
- [AREA]
</scope>

<authority>
Allowed without asking:
- read-only investigation;
- reversible work inside the isolated workspace;
- tests and local validation;
- routine choices consistent with the task contract.

Requires explicit authorization:
- production mutation;
- data deletion;
- external messages or publication;
- financial or legal commitment;
- access beyond the configured environment.
</authority>

<canonical_state>
Maintain:
- goal;
- hard constraints;
- confirmed facts;
- current state;
- completed work;
- remaining work;
- blockers;
- rejected paths and reasons;
- validation evidence;
- exact next action.
</canonical_state>

<context_policy>
Keep high-signal state in context.
Move durable details to external memory.
Discard redundant logs and superseded tool outputs.
During compaction, never convert:
- assumption → fact;
- planned → completed;
- weak evidence → strong evidence.
</context_policy>

<progress_policy>
Progress is demonstrated by changed observable state, not by
elapsed time, token use, or the number of tool calls.

Do not stop merely because the context is long.
Do not claim completion because substantial work was performed.
</progress_policy>

<pause_conditions>
Pause only when:
- a consequential choice requires the user;
- required authority is missing;
- an external dependency blocks useful work;
- continuing would risk violating a hard constraint.
</pause_conditions>

<checkpoint>
At each handoff, leave:
1. Current objective
2. Confirmed state
3. Work completed
4. Validation
5. Remaining work
6. Blocker
7. Exact next action
</checkpoint>

<completion>
Complete only when the observable success criteria are satisfied
and the final state has been checked against the task contract.
</completion>
```

---

# 5. Mixed Workflow: Research → Decision → Execution

```text
PHASE 1 — RESEARCH
Resolve only the uncertainties that materially affect the decision.
Return an evidence ledger and explicit unknowns.

DECISION GATE
Choose [OPTIONS].
State the evidence and threshold.
If authority is insufficient, stop here.

PHASE 2 — EXECUTION
Translate the chosen option into observable behavior and a scoped
change contract.

PHASE 3 — VALIDATION
Validate actual state, preserve hard constraints, and report
evidence of completion.
```

**[Framework]** 단계 사이에 명확한 decision gate를 두면 조사 결과가 자동으로 고위험 실행 권한으로 승격되는 것을 막을 수 있습니다.

---

# 6. 템플릿 사용 체크

```text
[ ] placeholder를 모두 실제 값으로 교체했는가?
[ ] 필요 없는 블록을 삭제했는가?
[ ] hard constraint를 발명하지 않았는가?
[ ] 방법이 아닌 observable outcome을 적었는가?
[ ] model이 routine decision을 할 수 있는가?
[ ] 실제 tool/environment 권한과 prompt의 authority가 일치하는가?
[ ] 완료 증거가 task type에 맞는가?
[ ] Fable 5 장기 실행이면 canonical state/checkpoint가 있는가?
[ ] 모델별 조정 지침을 golden workload에서 eval할 준비가 됐는가?
```

