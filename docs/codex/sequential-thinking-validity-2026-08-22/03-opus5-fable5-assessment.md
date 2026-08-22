---
status: complete
researched_at: 2026-08-22
---

# Opus 5와 Fable 5 모델별 판정

## 공통 기준

Anthropic의 [최신 prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)는 adaptive thinking이 복잡한 멀티스텝·도구 사용·장기 에이전트 작업에 적합하며, 최신 모델에서는 도구 호출 사이 thinking도 자동으로 interleave된다고 설명한다. 또한 수동 단계 지시보다 일반적인 목표 지시를 우선하라고 권한다.

더 직접적인 선행 근거는 Anthropic의 [`think` 도구 글](https://www.anthropic.com/engineering/claude-think-tool)이다. 2025년 Claude 3.7에서는 정책이 많은 연속 도구 작업에 효과가 있었지만, Anthropic은 2025-12-15 업데이트에서 내장 thinking이 개선됐으므로 대부분의 경우 전용 `think` 도구보다 내장 기능을 권장한다고 밝혔다.

Sequential MCP는 단순 `think` 도구보다 branch 메타데이터가 많지만, 결과를 계산하는 별도 엔진은 아니다. 그러므로 위 업데이트를 뒤집으려면 최신 모델 직접 비교가 필요하며 그런 공개 비교는 찾지 못했다.

## Claude Opus 5

공식 [What's new in Claude Opus 5](https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5)에 따르면 thinking은 기본 활성화되고, 모델이 turn마다 깊이를 결정하며, `effort`가 주 조절 수단이다. 복잡한 분석 사슬과 도구 사용 사이의 reasoning은 이미 모델 내부 경로에 있다.

[Opus 5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)는 불필요한 검증 지시가 native self-verification과 겹쳐 토큰과 지연을 늘릴 수 있다고 경고한다. Sequential 도구의 description은 가설 검증을 반복하고 만족할 때까지 계속하라는 지시를 포함한다.

**판정: 기본 off.** 먼저 `effort`를 올리거나 문제·제약·성공 조건을 명확히 해야 한다. Sequential MCP는 native thinking이 실패한 정책 집약형 연속 의사결정에서만 실험 후보이며, 일반 debug·설계·리뷰에 기본 추천할 근거는 없다.

## Claude Fable 5

공식 [Fable 5 모델 문서](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5)에 따르면 adaptive thinking은 항상 켜져 있고 끌 수 없다. raw chain of thought는 반환되지 않으며, 공개 가능한 thinking은 요약 또는 빈 블록이다.

[Fable 5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)는 두 가지를 강조한다.

- 과거 모델용으로 만든 과도하게 처방적인 skill은 품질을 떨어뜨릴 수 있으므로 최소 prompt에서 시작한다.
- 내부 reasoning을 응답 텍스트로 재현·전사·설명하도록 요구하면 `reasoning_extraction` 거부와 Opus 4.8 fallback이 늘 수 있다.

Sequential MCP의 긴 tool description은 11개 행동 단계와 `Chain of Thought` 검증을 요구한다. `thought` tool argument가 공식 문서의 “response text”와 동일한 안전 분류를 받는지는 공개돼 있지 않다. 따라서 직접 거부 위험이 **확인됐다**고 쓰면 과장이고, 안전하다고 가정하는 것도 근거가 없다.

**판정: Opus 5보다 더 강한 기본 off.** Fable 5에서는 내부 사고를 외부화하기보다 결정, 가정, 관찰된 증거, 선택한 대안을 사용자용 산출물로 작성해야 한다. Sequential MCP를 시험한다면 `reasoning_extraction` stop reason과 fallback 모델을 품질 지표와 함께 측정해야 한다.

## 비교표

| 축 | Opus 5 | Fable 5 | `--seq` 영향 판정 |
|---|---|---|---|
| native thinking | 기본 on | 항상 on | 중복 가능성 높음 |
| inter-tool thinking | 자동 | 자동 | 과거 핵심 사용 사례가 내장됨 |
| 주 조절 수단 | `effort` | `effort` | 외부 단계 수보다 공식 제어가 우선 |
| 과도한 처방 | 과검증 비용 위험 | 품질 저하 위험이 명시됨 | 긴 tool description이 불리할 수 있음 |
| reasoning 외부화 | 불필요 | 거부 분류와 긴장 | Fable에서 특히 보수적으로 처리 |
| 직접 Seq MCP A/B | 발견 못함 | 발견 못함 | 효과 크기 미측정 |

## 남아 있는 좁은 가능성

다음 경우에는 완전 폐기보다 opt-in 실험이 합리적이다.

- 각 단계의 외부 도구 결과가 다음 비가역 행동을 결정하는 정책 집약형 workflow
- 약한 비추론 모델까지 같은 도구 인터페이스를 사용해야 하는 다중 모델 harness
- 사람이 중간에 branch나 가정을 검토해야 하는 workflow

그러나 “감사 가능성”이 목적이라면 자유형 `thought` 전문보다 근거가 연결된 decision record가 더 안전하다. 모델이 생성한 사고 문자열은 충실한 raw CoT도 아니고 사실 검증된 감사 로그도 아니다.

