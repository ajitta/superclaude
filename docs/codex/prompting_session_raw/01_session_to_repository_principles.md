---
title: 원문 세션 원칙의 저장소 적용 모델
status: working-guide
last_verified: 2026-08-22
scope: src/superclaude
---

# 원문 세션 원칙의 저장소 적용 모델

## 1. 목적과 해석 경계

이 문서는 원문 세션의 핵심 개념을 `src/superclaude/`의 분석·개선·검증
언어로 변환한다. 원문의 특정 모델 이름, 가격, 출시 정보, 제품 동작은 이
작업에서 재검증하지 않았으므로 저장소 규칙의 근거로 직접 사용하지 않는다.

```text
raw-session idea
→ current repository evidence
→ smallest change hypothesis
→ deterministic / executable / behavioral evidence
→ release decision
```

## 2. 핵심 계약

원문의 `Intent → Objective → Context → Constraints → Authority → Success`
구조는 다음과 같이 적용한다.

| 계약 필드 | 저장소에서 묻는 질문 | 산출물 |
|---|---|---|
| Intent | 어떤 실제 실패나 비용을 줄이려는가? | 한 문장 문제 정의 |
| Objective | 외부에서 관찰 가능한 어떤 상태가 달라져야 하는가? | 기대 행동 |
| Context | 판단을 바꿀 현재 코드·규칙·테스트는 무엇인가? | 근거 파일 목록 |
| Hard constraints | 절대 깨지면 안 되는 불변식은 무엇인가? | hard gate |
| Preferences | 통과 후 최적화할 것은 무엇인가? | soft metric |
| Authority | prose, hook, CLI 중 어디까지 바꿀 권한이 있는가? | 변경 범위 |
| Uncertainty | 조사·가정·중단 중 무엇을 선택하는가? | 명시적 가정/차단 조건 |
| Success | 어떤 명령과 관찰로 완료를 판정하는가? | 검증 증거 |

좋은 작업 목표는 “agent 프롬프트를 더 명확하게 한다”가 아니다.

```text
관찰 실패:
  /sc:review가 읽기 전용 요청에서 파일을 수정했다.

목표:
  동일 fixture에서 변경 파일 수가 0이고, 필요한 결함을 정확한 file:line으로
  보고한다.
```

## 3. 원문 개념과 현재 구현의 대응

| 원문 개념 | 현재 저장소 대응 | 검증 방식 | 경계 |
|---|---|---|---|
| Minimum sufficient specification | `.claude/rules/content-quality.md` deletion test | ablation, 토큰/행동 비교 | 짧음 자체가 목표는 아님 |
| Intent·constraint fidelity | core 규칙, component mission/bounds | 구조 테스트 + golden task | plausible 제약을 hard constraint로 발명하지 않음 |
| Observable success | checklist, tests, eval checks | 실행 결과 | “careful”, “quality”는 기준이 아님 |
| Prompt vs harness | prose components vs hooks/CLI/runtime | hook 단위 테스트, 권한·결과 관찰 | 보장은 prose에만 두지 않음 |
| Context engineering | `CLAUDE_SC.md`, `context_loader.py`, cache/state utils | trigger, budget, dedup 테스트 | transcript 전체를 상태로 간주하지 않음 |
| Multi-agent isolation | agents, delegation rules, worktree patterns | 반환 증거 재검증 | 역할극만을 위해 위임하지 않음 |
| Hard gate vs soft metric | `evals/tasks.yaml`의 `gate: true`와 태그 지표 | exit code 2/1/0 | hard failure는 평균으로 상쇄 금지 |
| Golden task | `evals/fixtures/` + `tasks.yaml` | 동일 fixture/arm 비교 | golden answer가 아니라 허용 결과 공간 정의 |
| Regression / ablation | 4-arm harness, `parallel_ab` | baseline 대비 slice 비교 | 전체 평균만으로 배포 금지 |
| Security outcome | destructive guard, poisoned fixture | 실제 파일·tool input·출력 검사 | 안전하다고 말했는지가 아니라 행동 검사 |

## 4. 평가 대상은 문장 품질이 아니다

콘텐츠 변경 리뷰는 다음 10개 차원을 사용하되 총점만으로 판정하지 않는다.

| 차원 | 저장소용 질문 |
|---|---|
| Intent Fidelity | 관찰된 실패를 정확히 겨냥하는가? |
| Objective Clarity | 기대 행동이 파일·출력·도구 결과로 관찰되는가? |
| Constraint Fidelity | 명시된 불변식만 보존하고 새 금지사항을 발명하지 않는가? |
| Autonomy Calibration | routine·reversible 판단은 허용하고 위험 행동은 제한하는가? |
| Uncertainty Handling | 코드로 확인할 수 있는 것을 질문으로 돌리지 않는가? |
| Success Testability | 완료를 실행 가능한 체크로 판정할 수 있는가? |
| Evidence Grounding | 통과 주장이 실제 출력·diff·artifact를 가리키는가? |
| Escalation Quality | 결과를 바꾸는 사용자 결정이나 권한 부족에서만 멈추는가? |
| Failure-Mode Coverage | 가장 비싸고 빈번한 실패에 회귀 케이스가 있는가? |
| Prompt Efficiency | 중복·침전·행동을 바꾸지 않는 문장이 없는가? |

다음은 점수와 관계없이 실패다.

- 사용자 의도를 다른 과제로 바꿈
- 명시된 hard constraint를 위반함
- 근거 없이 권한을 확대함
- 성공 여부를 판정할 방법이 없음
- 보안·파괴·비밀 유출 hard gate가 실패함
- 실행하지 않은 검증을 통과했다고 주장함

## 5. 사양 평가와 결과 평가를 분리한다

```text
Specification evaluation
  frontmatter / XML / required fields / wiring / cross-reference

Outcome evaluation
  실제 선택 / 변경 / 도구 호출 / 테스트 / 보안 결과
```

구조 테스트 통과는 “Claude Code가 파일을 읽을 수 있다”는 증거다. 실제 요청에서
올바른 요소가 선택되고 의도한 행동이 나온다는 증거는 아니다. 반대로 행동
프로브 한 번의 통과는 모든 frontmatter·설치 경로·플랫폼 조합이 유효하다는
증거가 아니다. 두 층을 모두 통과해야 한다.

## 6. 실패 원인 분류

실패를 발견하면 지시문을 추가하기 전에 다음 중 하나로 분류한다.

| 코드 | 원인 | 우선 수정 위치 |
|---|---|---|
| SPEC | task/component 계약이 모호하거나 잘못됨 | component body/frontmatter |
| CONTEXT | 필요한 정보가 로드되지 않거나 오염됨 | import/trigger/context loader |
| MODEL | 명세와 환경이 충분해도 실행 변동이 큼 | model profile 또는 수용 가능한 한계 |
| TOOL | 도구·hook·CLI가 실패함 | scripts/hooks/cli/utils |
| TASK | 요구가 불가능하거나 서로 모순됨 | 사용자 에스컬레이션/계약 수정 |
| EVAL | 검사기가 올바른 결과를 실패 처리함 | fixture/check/rubric |
| DIST | source는 맞지만 설치·패키지 산출물이 다름 | build/install/drift gate |

모든 실패를 prompt 문제로 처리하면 규칙이 비대해지고 실제 원인이 남는다.

## 7. 저장소에 그대로 이식하지 않을 것

- 특정 모델 버전에 맞춘 상세 프롬프팅을 최신 1차 자료 확인 없이 추가하지 않는다.
- budget, credential, network egress, idempotency를 prose만으로 보장하지 않는다.
- 원문의 긴 범용 master prompt를 각 component에 복제하지 않는다.
- 사람의 선호 구현 하나를 golden answer로 고정하지 않는다.
- 한 번의 실패에 대응해 전역 금지문을 즉시 추가하지 않는다.
- LLM judge 결과를 deterministic/executable evidence보다 우선하지 않는다.

## 8. 개선 가설의 최소 형식

```yaml
change_id: SC-CHANGE-###
component: src/superclaude/<path>
intent: 줄이려는 실제 실패 또는 비용
observed_failure:
  scenario: 재현 입력
  evidence: 파일/명령/출력
root_cause_class: SPEC|CONTEXT|MODEL|TOOL|TASK|EVAL|DIST
hard_constraints:
  - 깨지면 즉시 실패할 불변식
hypothesis: 이 최소 변경이 실패를 줄이는 이유
expected_behavior:
  - 관찰 가능한 결과
required_gates: [G0, G1, ...]
soft_metrics:
  - token_cost
  - unnecessary_tool_calls
rollback: 되돌릴 조건과 방법
```
