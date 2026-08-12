# Agent Runtime Architecture

이 문서는 prompt, context, tools, permissions, state, multi-agent delegation, checkpoint, evaluation을 production runtime으로 배치합니다.

**[Framework]**

```text
Agent quality
=
Model
+ Task Contract
+ Runtime Context
+ Tools
+ Harness
+ Security
+ Evaluation
```

## 표시 규칙

- **[Confirmed]**: Anthropic 공개 자료와 직접 일치
- **[Framework]**: 이 문서의 reference architecture
- **[Heuristic]**: 실제 workload에서 검증할 운영 가설

공식 참고:

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)

---

# 1. Reference Architecture

```text
┌─────────────────────────────────────────────────────┐
│ APPLICATION                                         │
│ UI / API / Scheduler / User workflow                │
└──────────────────────────┬──────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────┐
│ TASK ADMISSION                                      │
│ task type / risk / routing / authorization          │
└──────────────────────────┬──────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────┐
│ PROMPT ARCHITECT                                    │
│ raw intent → normalized task contract               │
└──────────────────────────┬──────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────┐
│ ORCHESTRATOR / AGENT RUNTIME                        │
│ goal / state / tools / loop / delegation / finish   │
└──────────────┬─────────────────┬────────────────────┘
               ▼                 ▼
       ┌──────────────┐   ┌──────────────┐
       │ SUBAGENTS    │   │ TOOL GATE    │
       │ isolated ctx │   │ permissions  │
       └──────┬───────┘   └──────┬───────┘
              └──────────┬────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│ STATE / MEMORY / CHECKPOINT                         │
│ canonical state / artifacts / audit / recovery      │
└──────────────────────────┬──────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────┐
│ EVALUATION                                          │
│ deterministic / executable / structural / human     │
└─────────────────────────────────────────────────────┘
```

---

# 2. Prompt와 Harness의 책임

## Prompt에 적합한 policy

```text
Intent
Priorities
Scope
Decision policy
Uncertainty behavior
Success criteria
Escalation semantics
```

## Harness가 enforce할 mechanism

```text
Tool availability
Filesystem boundary
Network boundary
Credentials
Permissions
Budget
Timeout
Retry
Rate limit
Idempotency
Session persistence
Cancellation
Checkpoint
Audit log
Recovery
```

**[Framework]**

```text
Prompt = policy
Harness = mechanism
```

예:

```text
Prompt:
Do not perform destructive production mutations.

Harness:
Production database tool = read-only.
Delete endpoint = unavailable.
```

중요한 invariant를 모델의 기억과 순응성에만 맡기지 않습니다.

---

# 3. Task Admission

Agent loop 전에 분류합니다.

```text
Task type
Risk level
Required tools
Expected runtime
External side effects
Permission requirements
Data sensitivity
```

## Risk Tier

```text
R0 — Read-only
search, inspect files, analyze logs

R1 — Reversible local mutation
edit isolated workspace, generate files, run tests

R2 — External reversible mutation
create draft, update staging, open issue

R3 — Consequential / difficult to reverse
production deploy, delete data, send external message,
financial action, publish, rotate credentials
```

**[Framework]** admission 결과 예:

```text
Task:
"production server performance를 개선해."

Allowed now:
read-only investigation
local reproduction
candidate patch
benchmark in isolated environment

Requires separate authority:
production deploy
production configuration change
database mutation
```

---

# 4. Runtime Context 5계층

**[Confirmed]** Context는 단순 저장 공간이 아니라 모델의 현재 작업 메모리입니다.

**[Framework]**

```text
1. IMMUTABLE CONTEXT
   stable rules and contracts

2. TASK STATE
   goal and current execution state

3. WORKING CONTEXT
   information needed for the next decision

4. EXTERNAL MEMORY
   durable information retrievable later

5. EPHEMERAL TRACE
   temporary logs, tool outputs, failed paths
```

## Immutable Context

```text
System policy
Project invariants
Tool contracts
Security rules
Architecture conventions
```

## Task State

```text
Goal
Hard constraints
Current hypothesis
Confirmed facts
Completed work
Current work
Remaining work
Blockers
Validation
```

## Working Context

```text
Relevant files
Current diff
Recent errors
Decision-driving evidence
Immediate next action
```

## External Memory

```text
Design decisions
Evidence ledger
Progress file
Artifacts
Issue references
Persistent notes
```

## Ephemeral Trace

```text
Repeated logs
Superseded search results
Temporary commands
Failed searches with no future value
Conversational filler
```

---

# 5. Transcript와 State 분리

Transcript:

```text
User asked...
Agent tried...
Tool returned...
Test failed...
Agent revised...
```

State:

```text
Goal
Confirmed facts
Current hypothesis
Completed
Remaining
Constraints
Blockers
Validation
```

**[Framework]**

```text
Long-running usefulness:
State > Transcript
```

세션 기록은 감사·복구를 위해 저장할 수 있지만, 모델의 active context에는 필요한 상태만 다시 넣습니다.

---

# 6. Canonical State

장기 작업은 하나의 권위 있는 상태 객체를 둡니다.

```yaml
task_id: payment-idempotency
goal: Prevent duplicate payments on retries

hard_constraints:
  - preserve public API
  - do not weaken valid tests

confirmed_facts:
  - race occurs between existence check and insert

current_hypothesis:
  - atomic unique guard is required at transaction boundary

completed:
  - reproduced concurrent duplicate
  - traced payment creation path

current_work:
  - implement atomic idempotency guard

remaining:
  - concurrency regression test
  - billing integration suite
  - final diff review

blockers: []

validation:
  passed:
    - targeted sequential retry test
  pending:
    - concurrency test

next_action:
  - add concurrency regression test before final integration run
```

## 상태 불변식

Compaction, handoff, merge 시 절대 바꾸지 않습니다.

```text
assumption → fact
planned → completed
attempted → validated
weak evidence → strong evidence
blocked → complete
```

---

# 7. Compaction, Trimming, Reset

**[Confirmed]** Anthropic은 장기 agent의 핵심 기법으로 compaction, structured note-taking, subagent isolation을 설명합니다.

## Compaction

```text
Large trace
→ high-fidelity state summary
→ shorter active context
→ continue
```

좋은 compaction이 보존할 것:

```text
Goal
Hard constraints
Architecture decisions
Confirmed facts
Unresolved bugs
Files changed
Validation
Remaining work
Exact next action
```

삭제 후보:

```text
Repeated tool results
Superseded outputs
Conversational filler
Dead-end details with no future value
```

## Trimming

가장 안전한 첫 단계는 오래된 raw tool result를 제거하고, 그 결과에서 파생된 현재 사실만 유지하는 것입니다.

## Context Reset

**[Confirmed]** Anthropic의 장기 application harness 연구는 일부 상황에서 compaction만으로 충분하지 않으며, 구조화된 handoff와 깨끗한 새 context가 도움이 될 수 있음을 보여줍니다.

Reset 비용:

```text
+ clean attention
+ context anxiety 감소 가능

- handoff 정보 손실 위험
- orchestration complexity
- token/latency overhead
```

**[Heuristic]** 다음이면 reset을 고려합니다.

```text
같은 실패가 반복
오래된 가정에 계속 끌림
compaction 후에도 상태 혼동
모델이 context 길이 때문에 조기 종료
명확한 milestone handoff 가능
```

---

# 8. Checkpoint와 Handoff

```text
# Checkpoint

Objective:
[현재 목표]

Confirmed state:
[실제로 확인된 사실]

Completed:
[관찰 가능한 완료 작업]

Validation:
[실행한 검사와 결과]

Remaining:
[남은 작업]

Blocker:
[없으면 None]

Rejected paths:
[경로와 이유]

Exact next action:
[다음 실행 한 단계]
```

**[Confirmed]** 장기 agent 연구에서는 progress artifact와 version history를 다음 세션이 상태를 빠르게 복구하는 수단으로 사용했습니다.

---

# 9. Agent Loop

```text
while not complete:
    load task contract
    load canonical state
    select smallest useful next action
    request tool
    pass through permission gate
    execute
    observe actual result
    update canonical state
    checkpoint when state materially changes
    evaluate pause/completion conditions
```

**[Framework]** Progress는 다음으로 입증합니다.

```text
changed observable state
test result
new decision-driving evidence
resolved blocker
completed artifact
```

다음은 progress 증거가 아닙니다.

```text
많이 생각함
많은 tool call
긴 답변
오래 실행됨
context가 거의 참
```

---

# 10. Multi-Agent / Delegation

**[Confirmed]** Anthropic의 multi-agent research system은 orchestrator-worker 패턴과 분리된 context window, 병렬 탐색, 압축된 결과 반환을 사용합니다. 동시에 coordination complexity와 과도한 agent 생성이 실패 원인이 될 수 있다고 설명합니다.

기본값:

```text
Single capable agent
```

Delegate if:

```text
1. Work can proceed independently.
2. The branch produces a compact useful artifact.
3. The branch requires substantial context/tool use.
4. The manager does not need every intermediate step.
```

Don't delegate if:

```text
- next step depends strongly on the previous result;
- branches must coordinate continuously;
- the task is small;
- output cannot be safely compressed;
- the manager needs nearly all raw evidence.
```

## 유용성 기준

```text
Delegation value
=
Context isolation
+ Parallel speedup
+ Specialization benefit
- Coordination cost
- Integration risk
- Token/latency cost
```

## Dependency Density

```text
Low dependency:
US regulation research
Korea regulation research
→ parallelizable

High dependency:
find root cause
design fix based on root cause
→ sequential
```

## Manager 책임

```text
Goal ownership
Decomposition
Task boundaries
Shared constraints
Budget
Integration
Conflict resolution
Completion decision
```

## Subagent contract

```text
Objective:
[one bounded task]

Context:
[only what this branch needs]

Constraints:
[shared and branch-specific]

Tools:
[allowed tools]

Stop condition:
[when the branch is done]

Return:
1. Conclusion
2. Evidence
3. Counterevidence
4. Confidence
5. Unknowns
6. Parent-task implication
```

전체 trace를 manager context로 반환하지 않습니다.

---

# 11. Shared State와 Merge

좋은 구조:

```text
Manager owns:
- canonical goal
- constraints
- shared decisions
- task graph
- completion

Worker owns:
- branch-local exploration
- branch artifact
- evidence and uncertainty
```

Merge policy:

```text
1. Normalize outputs to the same schema.
2. Detect contradictions.
3. Prefer direct evidence over confidence.
4. Preserve unresolved disagreement.
5. Update canonical state only after integration.
```

공유 codebase에서 병렬 agent를 쓰면 별도 branch/worktree와 명시적 ownership을 사용합니다.

```text
Agent A → payments/*
Agent B → regression tests
Agent C → API compatibility audit
```

**[Heuristic]** 동일 파일을 여러 agent가 동시에 수정하는 구조는 coordination 이득보다 conflict 비용이 커지기 쉽습니다.

---

# 12. Tool Design

좋은 tool은:

```text
명확한 이름
좁은 책임
정확한 schema
예측 가능한 error
최소 권한
구조화된 output
idempotency semantics
```

나쁜 tool:

```text
do_everything(input: string)
```

더 나은 tool:

```text
read_customer(customer_id)
create_draft_invoice(customer_id, items)
publish_invoice(draft_id, approval_token)
```

**[Framework]** 결정과 실행 사이에 gate를 만들기 위해 read/plan/write/publish 능력을 분리합니다.

---

# 13. Permissions Engine

```text
Tool request
    ↓
Identity / task / risk / scope
    ↓
Policy evaluation
    ├── allow
    ├── deny
    ├── require approval
    └── transform to safer capability
```

정책 입력:

```text
task risk tier
tool
resource
operation
environment
data classification
reversibility
credential scope
user authorization
```

예:

```text
read production logs
→ allow with audit

edit local branch
→ allow

write staging
→ allow if task scope matches

deploy production
→ explicit authorization

delete production data
→ unavailable by default
```

---

# 14. Budget, Retry, Idempotency

Prompt:

```text
비용이 과도해지면 중단한다.
```

Harness:

```yaml
max_wall_time: 45m
max_tool_calls: 80
max_cost: 25
max_concurrent_workers: 4
retry:
  transient_errors: 2
  backoff: exponential
```

Idempotency:

```text
Every external mutation should have:
- a unique operation id;
- duplicate detection;
- safe retry behavior;
- observable result;
- audit record.
```

모델이 같은 tool call을 반복해도 외부 상태가 중복 생성되지 않게 합니다.

---

# 15. Observability

최소 로그:

```text
Task contract version
Model and settings
Prompt version
Tool request and result metadata
Permission decision
State transition
Checkpoint
Cost / tokens / latency
Validation
Final outcome
```

민감정보는 로그에 그대로 남기지 않습니다.

Metrics:

```text
Task success
Constraint violations
False completion
Escalation rate
Approval rate
Tool error rate
Retry rate
Context reset count
Cost
Latency
Security incidents
```

---

# 16. Recovery와 Cancellation

```text
Cancellation:
- stop issuing new tool calls;
- wait or terminate safe in-flight work;
- persist current state;
- report partial observable result.

Recovery:
- load last valid checkpoint;
- reconcile external state;
- detect whether previous mutation committed;
- resume idempotently;
- never assume an interrupted tool failed.
```

중요:

```text
No response
≠
No side effect
```

외부 mutation 후 timeout이면 재실행 전에 실제 상태를 확인합니다.

---

# 17. Model Profile Adaptation

## Claude Opus 5

**[Confirmed]** 2026-07-24 출시. 모델 ID `claude-opus-5`. $5 / $25 per MTok.

**[Heuristic]** 아래 조정은 workload eval 전까지 가설입니다.

```text
- compact but complete upfront specification
- high method autonomy
- fewer prompt-level verification loops
- rely on real tests and state checks
- simplify harness only after eval shows native capability
```

## Claude Fable 5

**[Confirmed]** 2026-06-09 출시. 모델 ID `claude-fable-5`. $10 / $50 per MTok.
Mythos 5와 동일 모델이며 차이는 안전장치입니다. 고위험 사이버·생물·화학 요청에서는 **Opus 4.8로 폴백**하므로,
장기 실행 harness는 이 폴백을 런타임 동작으로 가정하고 설계해야 합니다.
2026-06-12~06-30 수출통제로 접근이 중단된 이력이 있습니다 — 기반 모델 가용성 자체를 harness의 실패 모드로
다루고 대체 모델 경로를 확보하세요.

**[Framework]** Fable 5는 매우 강한 장기·복잡 작업 모델이지만, 능력이 높을수록 containment와 명확한 권한 경계의 필요가 줄어드는 것은 아닙니다.

```text
- canonical state
- evidence-grounded progress
- checkpoint and recovery
- compaction/reset policy
- explicit pause conditions
- capability containment
- workload-scaled delegation
```

---

# 18. Reference Repository Layout

```text
agent-system/
├── prompts/
│   ├── architect.md
│   ├── decision.md
│   ├── research.md
│   ├── coding.md
│   └── critic.md
├── contracts/
│   ├── task.schema.json
│   ├── checkpoint.schema.json
│   └── evidence.schema.json
├── runtime/
│   ├── admission/
│   ├── context/
│   ├── permissions/
│   ├── budgets/
│   ├── checkpoints/
│   └── recovery/
├── tools/
│   ├── read/
│   ├── local_write/
│   └── external_write/
├── evals/
│   ├── golden_tasks/
│   ├── graders/
│   ├── slices/
│   └── reports/
├── policies/
│   ├── risk_tiers.yaml
│   ├── tool_permissions.yaml
│   └── data_classification.yaml
└── README.md
```

---

# 19. 운영 체크리스트

```text
[ ] Task admission이 agent loop보다 먼저 실행되는가?
[ ] Prompt policy와 harness mechanism이 구분됐는가?
[ ] Canonical state가 하나인가?
[ ] Compaction이 사실의 강도를 왜곡하지 않는가?
[ ] 오래된 tool output을 active context에서 제거하는가?
[ ] Handoff가 exact next action을 남기는가?
[ ] Delegation이 context isolation/parallelism에 실제 이득이 있는가?
[ ] Tool은 최소 권한과 구조화된 output을 갖는가?
[ ] 외부 mutation은 idempotent한가?
[ ] Timeout 뒤 실제 상태를 reconcile하는가?
[ ] Completion claim을 actual state와 대조하는가?
[ ] 모델별 prompt/harness 변화가 eval로 gate되는가?
```

