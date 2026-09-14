---
status: ready_to_run
researched_at: 2026-08-22
---

# Opus 5 / Fable 5 반복 A/B 계획

## 목적

공개 자료가 답하지 못한 질문은 하나다. 같은 모델·effort·task에서 Sequential MCP가 native adaptive thinking보다 결과를 개선하는가?

## 실험 arm

| Arm | 구성 | 측정 목적 |
|---|---|---|
| A — native | Sequential 서버와 hint 없음 | 기준선 |
| B — available | 서버 등록, `--seq` hint 없음 | 모델의 자발적 선택과 schema 상주 비용 |
| C — current `--seq` | 서버 등록 + 현재 Tier 0 hint | 현 제품 플래그의 실제 효과 |
| D — decision record | 서버 없음 + 결정·가정·증거만 구조화하라는 짧은 지시 | 외부 관찰성의 더 안전한 대안 |

`effort`, `max_tokens`, 허용 도구, 시스템 prompt, fixture, timeout은 arm 사이에서 고정한다. Opus 5와 Fable 5는 별도 층으로 분석한다.

## task 묶음

1. 다중 원인 debug: 서로 모순되는 로그와 테스트 결과를 순차 제공한다.
2. architecture trade-off: 중간에 핵심 제약을 바꾸어 revision이 필요한 상황을 만든다.
3. policy-heavy action chain: 각 도구 결과가 다음 허용 행동을 바꾸며 규칙 위반을 자동 채점한다.
4. 연구 synthesis: 출처 간 충돌과 정보 공백을 판정하게 한다.
5. negative control: 단일 파일 수정, 단순 lookup, 문서 요약처럼 Sequential이 필요 없어야 하는 작업을 둔다.

각 task는 정답·불변조건·금지 행동을 기계적으로 채점할 수 있어야 한다. “더 깊어 보인다” 같은 주관 평가는 주 지표에서 제외한다.

## 수집 지표

- task pass/fail과 critical error 수
- 테스트·정책·인용 정확도
- input, output, thinking token과 추정 비용
- wall time, model turn 수, MCP call 수
- `isRevision`, `branchFromThought`, `branchId` 실제 사용률
- 최종 답변의 중복·길이
- Fable 5의 `stop_reason: refusal`, `reasoning_extraction`, fallback 모델
- Opus 5의 불필요한 재검증 횟수

## 반복 수

먼저 모델·arm·task당 5회 pilot을 실행해 분산과 비용을 본다. 신호가 있으면 최소 20회로 늘리고 paired bootstrap confidence interval을 보고한다. n=1 결과는 호환성 smoke test일 뿐 효능 판정에 쓰지 않는다.

## 사전 결정 규칙

기본 off를 뒤집으려면 다음을 만족해야 한다.

- 적어도 하나의 사전 지정 복합 task군에서 성공률 또는 critical error가 실질적으로 개선된다.
- 개선이 단순 task의 비용·지연 폭증으로 상쇄되지 않는다.
- 95% confidence interval 또는 반복 분포가 “차이 없음”과 구별된다.
- Fable 5 거부·fallback이 증가하지 않는다.
- branch/revision이 실제 문제 수정에 쓰이고 단순히 thought 수만 늘리지 않는다.

정확한 허용 비용 배수는 pilot 전에 제품 예산으로 고정해야 한다. 결과를 본 뒤 기준을 바꾸면 선택 편향이 생긴다.

## 재현 메타데이터

각 결과에는 다음을 저장한다.

```yaml
model:
effort:
max_tokens:
package_version:
server_reported_version:
repository_commit:
fixture_commit:
arm:
run_index:
tokens:
duration_ms:
mcp_calls:
refusal:
fallback_model:
checks:
```

기존 `evals/run_eval.py`는 격리·transcript·토큰 수집 기반으로 재사용할 수 있지만, MCP 구성 arm과 Sequential 전용 task/check를 추가해야 한다. 이 변경은 본 조사 문서 범위에 포함하지 않았다.

