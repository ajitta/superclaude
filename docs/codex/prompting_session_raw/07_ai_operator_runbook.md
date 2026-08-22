---
title: Claude/Codex용 개선 실행 런북
status: working-guide
last_verified: 2026-08-22
scope: repository change execution
---

# Claude/Codex용 개선 실행 런북

## 1. 운영 계약

이 런북을 읽은 agent는 “좋아 보이는 개선”을 제안하는 역할이 아니다. 관찰된
실패를 가장 작은 안전한 변경으로 해결하고, 실행 증거로 완료를 판정하는 역할을
맡는다.

```text
inspect before edit
root cause before wording
narrow evidence before broad validation
hard gates before soft metrics
observed state before completion claim
```

## 2. 입력

작업 시작 시 다음을 채운다. 빈 항목을 의식적으로 N/A로 판단할 수는 있지만
암묵적으로 건너뛰지 않는다.

```yaml
intent:
objective:
observed_failure:
affected_component:
delivery_path:
hard_constraints:
preferences:
authority:
success_evidence:
escalation_condition:
```

## 3. Step 1 — 저장소 상태와 규칙 확인

1. `git status --short`로 사용자 변경을 확인한다.
2. root와 변경 경로의 `AGENTS.md`를 읽는다.
3. `src/superclaude/ARCHITECTURE.md`에서 component 역할과 delivery를 확인한다.
4. 콘텐츠면 해당 `.claude/rules/*-authoring.md`와
   `xml-prose-format.md`, `content-quality.md`를 읽는다.
5. hook/CLI면 `.claude/rules/gotchas/hooks.md`와 관련 테스트를 읽는다.
6. 동일 basename, rule, trigger, threshold의 모든 사본을 검색한다.

Subagent `*.output` 파일을 직접 읽지 않는다. 반환 요약은 advisory이며, 인용한
file:line과 명령을 main agent가 다시 확인한다.

## 4. Step 2 — 문제를 재현하고 분류

```yaml
reproduction:
  input:
  initial_state:
  command_or_probe:
  observed_result:
  expected_result:
failure:
  system_class: SPEC|CONTEXT|MODEL|TOOL|TASK|EVAL|DIST
  behavior_class: B01-B15|null
confidence: high|medium|low
unknowns:
  - 결과를 바꿀 수 있지만 아직 확인되지 않은 것
```

가설을 먼저 세우고, 그 가설을 반증할 가장 좁은 증거를 찾는다. 증상이 prompt
문제처럼 보여도 loader, installer, tool, evaluator를 먼저 배제한다.

## 5. Step 3 — 변경 표면 결정

```text
same rule already exists?
  yes → pointer/repair/delete

delivery failure?
  yes → loader/installer/hook/build

behavioral spec failure?
  yes → smallest relevant component body/description

deterministic invariant?
  yes → code/hook/permission gate

runtime outside repository ownership?
  yes → document boundary or escalate; do not simulate enforcement in prose
```

관련 없는 refactor, 새 taxonomy, 새 공통 추상화는 관찰 실패가 요구하지 않으면
범위 밖이다.

## 6. Step 4 — 실패를 먼저 고정

가능한 순서:

1. deterministic unit test
2. integration fixture
3. behavioral golden task/canary
4. manual reproduction record

테스트 자체가 false pass/false fail을 만들지 않는지 anti-case를 추가한다. Prompt
행동 변경이면 candidate를 작성하기 전에 baseline 결과를 보존한다.

## 7. Step 5 — 최소 변경

- 하나의 원인에 하나의 의도적 delta를 만든다.
- SSOT를 수정하고 복제본은 pointer로 바꾼다.
- prose를 추가하기 전에 기존 문장을 수정·삭제할 수 있는지 본다.
- component type의 역할 경계를 넘지 않는다.
- 설치 파일을 직접 고치지 않고 source와 installer를 고친다.
- user change와 겹치면 보존하고 불가피할 때만 방향을 요청한다.

## 8. Step 6 — narrow → broad gate

```text
G0 contract
→ G1 structure
→ G2 graph/wiring
→ G3 affected unit
→ G4 integration/scope
→ G5 behavior/security
→ G6 clean distribution
→ G7 full regression/evidence
```

`05_quality_gate_catalog.md`의 matrix에서 required gate를 고른다. 실행하지 않은
gate는 NOT RUN으로 기록한다.

## 9. Step 7 — 결과 판정

다음 중 하나라도 참이면 완료가 아니다.

- required hard gate 실패
- baseline보다 critical slice 하락
- 테스트를 실행하지 않았는데 통과했다고 표현
- source만 확인하고 artifact/install path는 미확인
- evaluator 신뢰성이 불분명
- blocker가 실제로 남아 있음
- 변경 이유와 회귀 case가 연결되지 않음

## 10. Evidence packet

여러 agent가 읽기 분석을 나눴다면 각 결과는 다음 형식으로 합친다.

```yaml
question:
conclusion:
supporting_evidence:
  - path:line + 관찰
counterevidence:
  - 반대 신호 또는 null
commands_run:
  - command + result
confidence:
unknowns:
parent_task_implication:
residual_risk:
```

Manager는 global intent, hard constraint, canonical state, conflict resolution,
최종 completion을 소유한다. 독립 분석은 병렬화할 수 있지만 같은 파일의 write는
single-writer를 기본으로 한다.

## 11. Canonical state

장기 작업은 대화 transcript 대신 다음 상태를 유지한다.

```yaml
goal:
hard_constraints:
confirmed_facts:
assumptions:
current_hypothesis:
completed_work:
validated_work:
remaining_work:
blockers:
rejected_paths:
next_action:
```

요약·handoff·compaction 시 강도를 올리지 않는다.

```text
assumption ≠ fact
planned ≠ completed
attempted ≠ validated
weak evidence ≠ strong evidence
blocked ≠ complete
```

## 12. 중단·에스컬레이션

다음에서만 사용자 또는 더 높은 권한으로 돌린다.

- 결과를 materially 바꾸는 제품·전략 선택이 필요함
- 중요한 정보가 사용자에게만 있음
- irreversible/high-impact external action이 필요함
- scope나 권한을 materially 확대해야 함
- hard constraint가 서로 모순됨

context나 안전한 read-only 도구로 해소할 수 있으면 먼저 조사한다. low-impact,
reversible uncertainty는 명시적 가정으로 처리한다.

## 13. 최종 보고 형식

```markdown
## Outcome
[무엇이 실제로 달라졌는지]

## Changed
- [file]: [reason]

## Validation
- PASS — [command]: [result]
- NOT RUN — [gate]: [reason]

## Current findings
- [새로 발견했지만 범위 밖인 사실]

## Residual risk
- [남은 불확실성 또는 없음]
```

계획한 작업을 완료로 표현하지 않고, 로그를 길게 복사하는 대신 판정에 필요한
실제 증거만 남긴다.
