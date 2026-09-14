---
status: recommendation_ready
researched_at: 2026-08-22
repository_commit: d44a058a2d3a5950a157047778a3707c214599cd
verdict: default_off_narrow_opt_in
confidence: medium_high
---

# `--seq` / Sequential Thinking MCP 유효성 검증

## 결론

`--seq`는 **기술적으로 동작하지만, Claude Opus 5와 Claude Fable 5의 일반 작업에서 품질을 높인다고 입증되지 않았다.** 두 모델에서는 기본 비활성화하고, 네이티브 adaptive thinking으로 실패한 좁은 작업에서만 A/B 평가 후 opt-in하는 것이 타당하다.

판정의 근거는 다음과 같다.

1. 업스트림 Sequential Thinking 서버는 별도 추론 모델이나 검색기를 실행하지 않는다. 모델이 만든 `thought` 문자열을 메모리에 누적하고 번호·분기·이력 길이를 반환하는 외부 스크래치패드다.
2. Opus 5는 thinking이 기본 활성화되고, Fable 5는 adaptive thinking을 끌 수조차 없다. 두 모델 모두 도구 호출 사이의 interleaved thinking을 네이티브로 수행한다.
3. Anthropic은 2025-12-15에 전용 `think` 도구보다 내장 thinking을 대부분의 경우 우선하라고 기존 글을 갱신했다. Sequential MCP가 그보다 더 낫다는 최신 Opus 5/Fable 5 통제 실험은 찾지 못했다.
4. 2026년 커뮤니티 평가는 대체로 토큰 증가·과잉 사고·네이티브 reasoning과의 중복을 지적한다. 이 자료들은 방향성 참고용이며 실험 품질은 낮다.
5. Fable 5에서 `thought` 도구 호출이 `reasoning_extraction` 거부를 일으킨다는 직접 증거는 없다. 다만 Fable 5의 공식 지침과 “사고 과정을 외부화”하는 도구 설계가 긴장 관계에 있으므로, 안전하다고 가정해서도 안 된다.

## SuperClaude에 대한 권고

| 항목 | 권고 |
|---|---|
| 기본 설치 분류 | `core` 자동 제안에서 제외하고 legacy/experimental opt-in으로 이동 |
| Opus 5 | 기본 off. 먼저 native thinking의 `effort`를 조정 |
| Fable 5 | 기본 off. reasoning-like text 외부화를 피하고 결정·가정·증거만 보고 |
| `recommend.md` | 일반 debug, API 설계, Python 작업에 `--seq`를 자동 추천하지 않음 |
| 호환성 | 당장 플래그를 삭제하기보다 명시적 opt-in으로 유지하고 폐기 경고 제공 |
| 보존 조건 | 모델별 반복 A/B에서 품질 이득이 비용·지연·거부 위험을 상쇄할 때만 좁은 사용 사례로 유지 |

`--seq`의 유효성을 “서버가 실행되는가”와 “최신 모델의 결과를 개선하는가”로 나누면 전자는 확인됐고 후자는 미입증이다. 이 구분이 이번 검증의 핵심이다.

## 문서 안내

| 문서 | 내용 |
|---|---|
| [01-scope-and-method.md](./01-scope-and-method.md) | 조사 범위, 증거 등급, 검색 한계 |
| [02-upstream-and-runtime.md](./02-upstream-and-runtime.md) | 업스트림 구현, npm 버전, 로컬 MCP 재현 |
| [03-opus5-fable5-assessment.md](./03-opus5-fable5-assessment.md) | 모델별 공식 지침과 유효성 판정 |
| [04-community-evidence.md](./04-community-evidence.md) | 긍정·부정 커뮤니티 평가와 신뢰도 |
| [05-cost-privacy-security.md](./05-cost-privacy-security.md) | 토큰, 지연, 로깅, 공급망, Fable 위험 |
| [06-repository-recommendations.md](./06-repository-recommendations.md) | SuperClaude 변경 권고와 우선순위 |
| [07-evaluation-plan.md](./07-evaluation-plan.md) | Opus 5/Fable 5 반복 A/B 설계 |
| [08-sources.md](./08-sources.md) | 1차·2차 자료 목록 |
| [09-VERIFICATION.md](./09-VERIFICATION.md) | 실행한 검증과 남은 미검증 항목 |

