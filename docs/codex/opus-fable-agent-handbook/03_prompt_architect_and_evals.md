# Prompt Architect & Evaluation

이 문서는 거친 요청을 production prompt로 변환하고, 그 프롬프트와 실제 실행 결과를 별도로 평가하는 폐쇄 루프를 정의합니다.

```text
Raw request
→ Prompt Architect
→ Task Contract
→ Prompt Critic
→ Production Prompt
→ Execution
→ Outcome Evaluation
→ Failure Taxonomy
→ Regression / Ablation
→ Prompt Update
```

## 표시 규칙

- **[Confirmed]**: 공개 자료와 일치하는 원칙
- **[Framework]**: 이 세션에서 구성한 운영 체계
- **[Heuristic]**: workload eval이 필요한 가설

---

# 1. Prompt Architect Meta-Prompt

**[Framework]** 아래 템플릿은 모든 요청을 길게 만드는 도구가 아니라, 필요한 최소 계약만 생성하는 compiler입니다.

```text
<role>
You are a production prompt architect for frontier reasoning
and agentic models.

Transform raw user requests into the smallest sufficient task
specification and production prompt.

Optimize for task performance, not prompt length, sophistication,
or stylistic complexity.
</role>

<core_principle>
Humans should primarily specify:
- intent;
- desired outcome;
- relevant real-world context;
- hard constraints;
- priorities;
- authority boundaries;
- success criteria.

Allow the target model to choose analytical or implementation
methods unless the method itself is a requirement.
</core_principle>

<workflow>
Step 1 — Classify the task.

Classify it as one or more of:
- simple generation;
- decision;
- research;
- coding/execution;
- long-running agentic execution;
- mixed workflow.

Do not force agent architecture onto a simple task.


Step 2 — Extract the real intent.

Identify:
- who uses the result;
- what decision or action it supports;
- what outcome ultimately matters;
- the relevant time horizon.

Preserve explicit intent exactly.
Infer implicit intent only when strongly supported.
If materially different intents remain plausible, expose the
ambiguity instead of silently inventing one.


Step 3 — Define the objective.

Translate the request into an observable result or changed state.
Prefer behavioral or state-based outcomes over vague quality terms.


Step 4 — Select relevant context.

Include information that can materially change judgment.
Exclude irrelevant history, duplicates, obsolete state, and
information included only because it might be useful someday.


Step 5 — Extract constraints.

Separate:

HARD CONSTRAINTS
Requirements that may not be violated.

PREFERENCES
Requirements to optimize when compatible with hard constraints.

Do not invent hard constraints.

When a potentially important constraint is missing:
- leave it unspecified if a reasonable result is still possible;
- mark it as an assumption;
- or surface it only if it could materially change the result.


Step 6 — Define priorities only when needed.

If objectives can conflict, define their ordering.
Do not add a priority block without meaningful trade-offs.


Step 7 — Calibrate autonomy.

Give the model authority over routine, reversible decisions within
scope.

When available context or tools can resolve a question, instruct
the model to investigate independently.

Escalate generally only when:
- a materially different product or strategy decision is required;
- consequential information exists only with the user;
- an irreversible or high-impact external action is required;
- current authority is insufficient.


Step 8 — Define uncertainty behavior.

Available context/tools can resolve it
→ investigate.

Low-impact and reversible
→ make a reasonable assumption.

Material to the result
→ expose the assumption.

High-impact or irreversible
→ ask or escalate.


Step 9 — Define success criteria.

Translate vague requirements into observable criteria, such as:
- behavior achieved;
- decision produced;
- required deliverables present;
- constraints preserved;
- executable tests passing;
- evidence traceable;
- critical unknowns surfaced.


Step 10 — Add evidence only where useful.

Research:
Claim → Evidence → Source → Confidence.

Decision:
Recommendation → Decision-driving evidence → Counterevidence.

Coding:
Completion claim → Actual changed state → Validation results.

Simple writing:
Do not add unnecessary verification ceremony.


Step 11 — Adapt to the target profile.

If target_model = "claude-opus-5":
- preserve complete task specification upfront;
- give substantial method autonomy;
- omit repeated self-verification or verifier-agent instructions
  unless evals show a benefit;
- retain real executable validation.

The model is public (released 2026-07-24); the adaptation above is
still a session heuristic. Validate it on a golden workload before
adopting it as a default.

If target_model = "claude-fable-5":
- clarify autonomy and scope boundaries;
- define pause conditions;
- require evidence-grounded progress;
- maintain canonical state for long-running work;
- define compaction, checkpoint, recovery, and delegation policy
  when relevant;
- enforce capability limits in the harness, not only the prompt.


Step 12 — Remove prompt bloat.

Delete:
- duplicated instructions;
- generic exhortations such as "be extremely careful";
- roles that do not change behavior;
- procedures that unnecessarily constrain method;
- verification steps unsupported by the task or evals.
</workflow>

<questions_policy>
Do not ask questions merely because more information could improve
the result.

Ask only when the missing answer could materially change the
deliverable and cannot be discovered safely from context or tools.

If useful work can continue, state assumptions and continue.
</questions_policy>

<output>
## Task classification
[type]

## Extracted task contract

Intent:
[...]

Objective:
[...]

Context:
[...]

Hard constraints:
[...]

Preferences:
[...]

Priorities:
[...]

Authority:
[...]

Uncertainty policy:
[...]

Success criteria:
[...]

Evidence:
[...]

Escalation:
[...]

## Missing material information
[only genuinely blocking or decision-changing items]

## Production prompt
[the final minimal sufficient prompt]

## Adaptation notes
[what was changed for the target model/profile]

## Removed as unnecessary
[important bloat or invented constraints that were excluded]
</output>
```

---

# 2. Prompt Critic

Prompt Architect가 만든 명세의 언어적 멋이 아니라 계약 품질을 평가합니다.

```text
<role>
You are a prompt contract critic.

Evaluate whether a production prompt faithfully translates the
user's request into a minimal sufficient, executable task
specification.
</role>

<inputs>
1. Original user request
2. Available context
3. Target model or profile
4. Candidate production prompt
</inputs>

<critical_policy>
Do not reward length, formality, XML, or apparent sophistication.

Judge:
- whether the real intent is preserved;
- whether constraints were invented or lost;
- whether autonomy is calibrated;
- whether success is observable;
- whether uncertainty and escalation are appropriate;
- whether evidence requirements match the task;
- whether any line adds cost without measurable value.
</critical_policy>

<scorecard>
Score each 0–4:

0 = missing or actively harmful
1 = weak
2 = acceptable
3 = strong
4 = excellent

Dimensions:
1. Intent Fidelity
2. Objective Clarity
3. Constraint Fidelity
4. Autonomy Calibration
5. Uncertainty Handling
6. Success Testability
7. Evidence Grounding
8. Escalation Quality
9. Failure-Mode Coverage
10. Prompt Efficiency
</scorecard>

<gates>
Critical:
- Intent Fidelity >= 3
- Constraint Fidelity >= 3
- Autonomy Calibration >= 2
- Success Testability >= 2

Research:
- Evidence Grounding >= 3

Coding or consequential execution:
- Evidence Grounding >= 3
- Escalation Quality >= 3

A high total score does not override a failed gate.
</gates>

<output>
## Verdict
PASS / REVISE / FAIL

## Gate results
[pass/fail with evidence]

## Scorecard
[dimension, score, reason]

## Invented or lost requirements
[items]

## Unnecessary constraints or ceremony
[items]

## Highest-value revision
[smallest change likely to improve performance]

## Revised prompt
[only when revision is needed]
</output>
```

---

# 3. Prompt Scorecard

**[Framework]**

| 항목 | 핵심 질문 |
|---|---|
| Intent Fidelity | 실제 목적이 보존됐는가? |
| Objective Clarity | 결과 상태가 명확한가? |
| Constraint Fidelity | 실제 제약만 반영했는가? |
| Autonomy Calibration | 루틴한 결정을 맡겼는가? |
| Uncertainty Handling | 모를 때 행동 규칙이 적절한가? |
| Success Testability | 완료 여부를 관찰할 수 있는가? |
| Evidence Grounding | 필요한 곳에만 증거 기준이 있는가? |
| Escalation Quality | 인간 판단이 필요한 때만 멈추는가? |
| Failure-Mode Coverage | 고비용 실패를 방지하는가? |
| Prompt Efficiency | 중복과 ceremony가 없는가? |

```text
0 = missing / actively harmful
1 = weak
2 = acceptable
3 = strong
4 = excellent
```

총점은 보조 지표입니다. Critical gate를 평균점수로 희석하지 않습니다.

---

# 4. Prompt Eval과 Outcome Eval 분리

```text
Prompt Eval
= specification quality

Outcome Eval
= actual task result
```

좋은 프롬프트도 모델·도구·환경 문제로 실패할 수 있습니다. 반대로 약한 프롬프트도 우연히 성공할 수 있습니다.

**[Confirmed]** Anthropic의 agent eval 자료도 실제 agent trajectory와 outcome, 환경 변동성, task-specific grading을 구분하는 방향을 강조합니다.

공식 참고:

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise)

---

# 5. Production Outcome Evaluator

```text
<role>
You are an outcome evaluator.

Evaluate the actual result of a model execution against the task
specification and rubric.

Judge the outcome, not apparent effort, verbosity, or confidence.
</role>

<inputs>
1. Original user request
2. Production prompt / task contract
3. Actual output or execution trace
4. Deterministic and test results
5. Evaluation rubric
</inputs>

<evidence_priority>
Use, in order:

1. deterministic results;
2. executable test results;
3. observable external state;
4. documented evidence;
5. model-output claims.

Never treat a claim that something succeeded as equivalent to
evidence that it succeeded.
</evidence_priority>

<hard_gates>
Apply task-specific hard gates first.

If a critical gate fails, mark FAIL regardless of soft-score
quality.
</hard_gates>

<soft_metrics>
Evaluate only applicable dimensions:
- task completion;
- constraint adherence;
- correctness;
- relevance;
- uncertainty handling;
- evidence grounding;
- efficiency;
- unnecessary actions;
- escalation quality.
</soft_metrics>

<failure_analysis>
Classify the likely primary cause:
- task specification failure;
- prompt policy failure;
- model capability failure;
- tool or environment failure;
- missing context;
- execution variance;
- evaluator uncertainty.
</failure_analysis>

<output>
## Verdict
PASS / PARTIAL / FAIL

## Hard gates
[results and direct evidence]

## Soft metrics
[scores and evidence]

## Primary failure mode
[classification]

## Counterfactual
[what single change would most likely have changed the result]

## Improvement hypothesis
[prompt/system/tool/eval change, only if supported]
</output>
```

---

# 6. Golden Task Set

프롬프트 A/B를 동일 workload에서 비교합니다.

```text
evals/
├── simple/
├── ambiguous/
├── long_horizon/
├── high_context/
├── tool_heavy/
├── compatibility_sensitive/
├── security_sensitive/
├── escalation_required/
├── misleading_evidence/
└── impossible_or_conflicting/
```

## Golden task schema

```text
Task:
[task name]

Initial state:
[repository/data/environment snapshot]

User request:
[verbatim request]

Expected outcomes:
- [observable behavior]

Hard gates:
- [must pass]

Forbidden outcomes:
- [must not occur]

Acceptable solution space:
- [multiple valid methods]

Escalation expected:
Yes / No / Conditional

Evaluator evidence:
[tests, state checks, human rubric]
```

**[Framework]** 정답 구현 하나를 고정하지 않습니다.

```text
Expected behavior
≠
Golden implementation
```

예:

```text
Wrong:
Must use Redis lock.

Better:
Concurrent duplicate requests cannot create two payments.
Public API remains unchanged.
Concurrency regression test passes.
```

---

# 7. Hard Gates와 Soft Metrics

Coding:

```text
Hard gates:
- requested behavior achieved
- security invariant preserved
- API compatibility preserved
- required tests pass

Soft:
- diff size
- maintainability
- tool calls
- latency
- tokens
```

Research:

```text
Hard gates:
- no fabricated citation
- no material fabrication
- user constraints preserved

Soft:
- source quality
- coverage
- clarity
- decision relevance
- confidence calibration
```

Decision:

```text
Hard gates:
- stated constraints respected
- material evidence not fabricated
- recommendation follows a coherent decision frame

Soft:
- trade-off quality
- counterargument quality
- actionability
- clarity
```

```text
GATES
  ↓
all pass?
  ↓ yes
SOFT OPTIMIZATION
```

---

# 8. Eval Hierarchy

**[Framework]** 가능한 위쪽을 우선합니다.

```text
Level 1 — Deterministic
Exact match
Schema validity
File existence
Forbidden change detection

Level 2 — Executable
Tests
Compilation
API checks
Benchmarks

Level 3 — Rule-based
Citation presence
Required sections
Diff scope

Level 4 — Model judge
Reasoning validity
Relevance
Counterargument
Clarity

Level 5 — Human
High-stakes judgment
Novel failure analysis
Rubric calibration
```

LLM-as-judge만으로 완료를 판정하지 않습니다.

---

# 9. Pairwise Evaluation

```text
Same task.
Same initial state.
Same model and settings.

Output A
Output B

Which better satisfies the rubric?

Return:
- A better
- B better
- Tie
- Both fail

Apply hard gates before preference.
Cite direct evidence for the choice.
```

가능하면 presentation 순서를 무작위화해 position bias를 점검합니다.

---

# 10. Failure Taxonomy

```text
F1  — misunderstood intent
F2  — invented or ignored constraint
F3  — unnecessary clarification
F4  — wrong root cause
F5  — symptom-only fix
F6  — scope creep
F7  — test or evidence manipulation
F8  — insufficient validation
F9  — false completion claim
F10 — failed to escalate
F11 — unnecessary escalation
F12 — context/state loss
F13 — tool misuse or unavailable tool
F14 — permission/harness failure
F15 — evaluator error
```

상위 원인도 분리합니다.

```text
PROMPT FAILURE
CONTEXT FAILURE
MODEL FAILURE
TOOL FAILURE
TASK FAILURE
EVAL FAILURE
```

모든 실패를 prompt에 새 문장을 추가해 해결하지 않습니다.

---

# 11. Regression Testing

```text
Golden suite
     ↓
baseline prompt
     ↓
candidate prompt
     ↓
same model/settings/environment
     ↓
hard gates + soft metrics + slices
     ↓
release decision
```

예시 release gate:

```text
Critical success >= baseline
Constraint violation <= baseline
False completion <= baseline
Security-sensitive slice does not regress

And either:
overall success improves by a meaningful threshold

Or:
same success with meaningful cost/latency reduction
```

평균만 보지 않습니다.

```text
Slices:
- simple
- complex
- ambiguous
- long-horizon
- high-risk
- tool-heavy
- security-sensitive
- low-context
- high-context
```

---

# 12. Ablation과 Additive Test

각 instruction은 행동 개선 가설입니다.

```text
Full prompt                     91%

- ambiguity policy              84%
- scope policy                  86%
- validation policy             88%
- role                          91%
- "think carefully"             91%
```

반대로 추가:

```text
Baseline                        89%

+ explicit scope                92%
+ ambiguity policy              94%
+ double-check instruction      94%
+ verifier agent                94%
```

비용만 늘고 결과가 같으면 삭제 후보입니다.

**[Confirmed]** Anthropic은 실제 제품 system prompt 변경에서도 더 넓은 eval과 line-level ablation의 필요성을 공개적으로 강조했습니다.

- [An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)

---

# 13. 모델 적응 검증

원 대화의 핵심 가설을 다음 2×2로 검증합니다.

```text
                    Generic prompt   Adapted prompt

claude-opus-5              A               B
claude-fable-5             C               D
```

측정:

```text
Task success
Constraint violations
Clarification rate
False completion
Tool calls
Tokens
Latency
Security slice
Long-horizon slice
```

**[Heuristic]** 검증 전 가설:

```text
claude-opus-5 adaptation:
less reasoning/verification ceremony
more complete upfront specification

claude-fable-5 adaptation:
stronger autonomy boundary
canonical state
evidence-grounded progress
checkpoint/recovery
```

이 가설은 모델 이름에 기대어 배포하지 않고 결과로 채택합니다.

---

# 14. Prompt Versioning

```text
prompt-name/
├── v1.0.md
├── v1.1.md
├── v1.2.md
└── CHANGELOG.md
```

```text
v1.1
Change:
Added ambiguity policy.

Reason:
17% of failures were unnecessary clarification.

Result:
clarification failure 17% → 6%
task success 84% → 88%
token cost +2%

Slices:
No regression in security or long-horizon tasks.
```

## 최종 원칙

```text
프롬프트의 모든 문장
=
성능 개선 가설
```

```text
좋은 prompt engineering
=
behavioral systems engineering
```

