---
status: proposed
researched_at: 2026-08-22
---

# SuperClaude 저장소 권고안

이 문서는 변경을 적용하지 않고 권고만 제시한다.

## P0 — 문서와 런타임 계약 정정

1. README에서 Sequential의 `30-50% fewer tokens` 주장을 삭제한다. 이를 뒷받침하는 비교가 없다.
2. `--seq`, `--all-mcp`, `--no-mcp`가 서버를 turn 단위로 켜고 끈다는 표현을 고친다. 현재는 context hint의 선택이며 실제 MCP 등록 상태를 바꾸지 않는다.
3. `src/superclaude/mcp/README.md`의 Sequential 버전을 `2026.7.4`로 갱신하고 검증일을 분명히 한다.
4. “서버 실행 가능”과 “최신 모델 품질 개선”을 별도 상태로 표시한다.

## P0 — 기본 경로에서 제외

1. `install_mcp.py`의 Sequential 분류를 `core` 자동 제안에서 experimental/legacy opt-in으로 내린다.
2. `commands/recommend.md`에서 일반 debug, security, API 설계, Python 작업에 `--seq`를 붙이는 규칙을 제거한다.
3. `FLAGS.md`의 “analysis/discussion에는 `--seq --tavily --c7`” 기본 예시에서 `--seq`를 제거한다.
4. `--all-mcp`가 Sequential을 암묵적으로 권하는 경로도 재검토한다.

이 단계는 플래그 삭제가 아니다. 기존 사용자 호환성을 위해 명시적 `--seq`는 남기되 기본·자동 추천 경로에서만 뺀다.

## P1 — 보존 시 안전한 기본값

- 설치 명령에 검증 버전을 고정한다.
- `DISABLE_THOUGHT_LOGGING=true`를 정적 환경 변수로 등록한다.
- `MCP_Sequential.md`를 “더 깊게 생각하기”가 아니라 “외부 decision scratchpad”로 정확히 기술한다.
- Fable 5에서는 reasoning transcript를 만들지 말고 결정·가정·증거·미해결 쟁점만 기록하도록 제한한다.
- 고정 thought 수 예시와 “만족할 때까지 반복 검증” 지시를 제거한다. Opus 5의 over-verification과 Fable 5의 과처방 위험을 줄이기 위해서다.

## P1 — 근거가 생긴 좁은 사용 사례만 재승격

다음 조건을 모두 만족할 때만 특정 command에 `--seq` 자동 추천을 복원한다.

1. Opus 5 또는 Fable 5의 반복 A/B에서 native 대비 의미 있는 성공률 또는 중대 오류 감소가 있다.
2. 단순·중간 작업 negative control에서 비용과 지연만 늘리지 않는다.
3. branch·revision 기능이 실제로 사용되며 단순 선형 장황화가 아니다.
4. Fable 5의 `reasoning_extraction` 거부와 Opus 4.8 fallback이 증가하지 않는다.
5. 결과가 모델 ID, effort, package version, fixture commit과 함께 재현 가능하다.

## 모델·작업별 운영표

| 모델·작업 | 기본값 | 우선 대안 | Seq 사용 조건 |
|---|---|---|---|
| Opus 5 일반 코딩·debug | off | native thinking, 명확한 성공 기준, 실제 테스트 | native가 반복 실패한 fixture가 있을 때만 |
| Opus 5 정책 집약형 연속 도구 작업 | off | `effort` sweep, interleaved thinking | A/B에서 중대 정책 위반 감소 시 |
| Fable 5 모든 일반 작업 | off | minimal prompt, 이유와 경계 제공 | 거부율을 포함한 별도 실험 통과 시 |
| 약한 비추론 모델 | optional | plan/checklist | 모델별 측정 이득이 있을 때 |
| 사람이 읽는 감사 산출물 | off | decision record: 결정·근거·승인·결과 | 자유형 thought trace 대신 구조화 record 사용 |

## 최종 제품 판정

현재 증거로는 `--seq`를 SuperClaude의 대표 “complex reasoning” 기능으로 계속 마케팅할 수 없다. 가장 안전한 전환은 **호환성은 유지하되 기본값과 추천에서 내리고, 실험으로 입증된 작업만 다시 올리는 것**이다.

