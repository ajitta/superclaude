---
title: SuperClaude 개선·검증 가이드
status: verified-guide
last_verified: 2026-08-22
scope: src/superclaude
---

# SuperClaude 개선·검증 가이드

이 디렉터리는 원문 세션의 프롬프트·에이전트 엔지니어링 원칙을 현재
`src/superclaude/` 구조에 맞게 변환한 작업용 문서 묶음이다. 목적은
“문장이 좋아 보이는가”를 평가하는 것이 아니라, 각 변경이 실제 전달 경로에서
의도한 행동을 만들고 회귀를 일으키지 않는지 증명하는 것이다.

원문은 [`00_raw_session_verbatim.md`](00_raw_session_verbatim.md)에 그대로 보존한다.
이 문서들은 원문을 권위 있는 사양으로 간주하지 않는다. 현재 저장소의 코드,
테스트, 저작 규칙을 먼저 따르고 원문에서 가져온 개념은 운영 프레임워크 또는
검증할 가설로 표시한다.

## 문서 지도

| 문서 | 읽는 시점 | 답하는 질문 |
|---|---|---|
| [`01_session_to_repository_principles.md`](01_session_to_repository_principles.md) | 처음 | 원문 원칙을 이 저장소에 어떻게 해석하는가? |
| [`02_component_and_delivery_map.md`](02_component_and_delivery_map.md) | 변경 범위 탐색 전 | 각 요소의 역할, 전달 경로, 강제 경계는 무엇인가? |
| [`03_content_component_playbook.md`](03_content_component_playbook.md) | core/agent/command/mode/skill/MCP 수정 전 | 콘텐츠 요소를 어떻게 분석하고 최소 변경하는가? |
| [`04_runtime_and_distribution_playbook.md`](04_runtime_and_distribution_playbook.md) | cli/hooks/scripts/utils/templates 수정 전 | 런타임·설치·배포 요소를 어떻게 개선하고 검증하는가? |
| [`05_quality_gate_catalog.md`](05_quality_gate_catalog.md) | 계획·리뷰·릴리스 시 | 어떤 게이트를 어떤 순서로 통과해야 하는가? |
| [`06_behavioral_eval_playbook.md`](06_behavioral_eval_playbook.md) | 프롬프트 행동 변경 시 | golden task, hard gate, A/B, canary를 어떻게 운영하는가? |
| [`07_ai_operator_runbook.md`](07_ai_operator_runbook.md) | Claude/Codex가 실제 변경할 때 | 한 번의 개선 작업을 어떤 계약과 증거로 수행하는가? |
| [`08_current_findings_and_backlog.md`](08_current_findings_and_backlog.md) | 우선순위 결정 시 | 현재 확인된 사각지대와 다음 개선 후보는 무엇인가? |
| [`09_VERIFICATION.md`](09_VERIFICATION.md) | 문서 신뢰도 확인 시 | 이 문서 묶음을 무엇과 대조했고 어떤 gap을 수정했는가? |

## 추천 읽기 경로

- 새 에이전트: `01 → 02 → 07 → 변경 대상별 03 또는 04 → 05`
- 콘텐츠 저작자: `02 → 03 → 05 → 06`
- 런타임·설치 개발자: `02 → 04 → 05 → 08`
- 리뷰어·릴리스 담당자: `05 → 06 → 08 → 09`

## 증거 등급

모든 판단은 다음 등급을 사용한다.

| 등급 | 의미 | 허용되는 근거 |
|---|---|---|
| `[REPO]` | 현재 저장소에서 직접 확인됨 | 소스, 테스트, 명령 출력, 생성 아티팩트 |
| `[FRAMEWORK]` | 원문을 저장소 운영 방식으로 재구성함 | 설계 규칙; 적용 전 현행 코드와 대조 필요 |
| `[HYPOTHESIS]` | 실제 workload 검증이 필요한 개선 가설 | A/B, ablation, canary 결과가 필요 |
| `[EXTERNAL]` | 외부 제품·모델·표준에 관한 주장 | 최신 1차 문서를 별도로 확인해야 함 |

`00_raw_session_verbatim.md`의 인용 표식이나 `[Confirmed]` 표현만으로
`[REPO]` 또는 `[EXTERNAL]` 판정을 내리지 않는다.

## 공통 판정

이 문서 묶음은 다음 네 결론을 전제로 한다.

1. 콘텐츠 형식 검증과 실제 행동 검증은 서로 대체할 수 없다.
2. 치명적 실패는 평균 점수로 상쇄하지 않고 hard gate로 차단한다.
3. 프롬프트는 정책을 표현하고, 보장이 필요한 제약은 hook·권한·코드가 강제한다.
4. 관찰된 실패와 회귀 케이스 없이 지시문을 추가하지 않는다.

## 문서 갱신 규칙

- 구성요소 수와 테스트 명령은 스냅샷이다. 변경 시 소스에서 다시 계산한다.
- 새 규칙은 기존 단일 진실 공급원(SSOT)을 대체하지 않는다. 이 디렉터리에는
  원문 규칙을 복사하지 않고 링크, 게이트, 작업 순서만 둔다.
- 현재 발견이 수정되면 `08_current_findings_and_backlog.md`에서 상태와 검증
  증거를 함께 갱신한다.
- 행동 기본값을 바꾸면 `evals/`에 회귀 케이스를 먼저 또는 동시에 추가한다.
