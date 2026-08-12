# Frontier Prompting Principles

이 문서는 세션의 핵심 이론을 후속 정정과 현재 공개 자료에 맞춰 재편집한 것입니다. 긴 프롬프트 자체보다 **최소 충분 명세(Minimum Sufficient Specification)** 를 목표로 합니다.

## 표시 규칙

- **[Confirmed]**: Anthropic 공개 문서나 공개 제품 자료로 직접 확인된 내용
- **[Framework]**: 확인된 원칙을 production engineering 관점에서 재구성한 이 문서의 설계 체계
- **[Heuristic]**: 특정 모델·워크로드에서 실험으로 검증해야 하는 경험적 가설

## 0. 모델 명칭 (2026-08-12 검증 기준)

> **정정 이력**: 이 절의 이전 판은 “Claude Opus 5는 공개 자료에서 확인되지 않았다”고 기술했습니다.
> 오류였습니다. Opus 5는 2026-07-24 출시됐습니다. 부재 주장을 `[Confirmed]`로 표기한 것이 판정 오류이며,
> 이 문서가 §7에서 가르치는 “Confirmed fact / Assumption / Material unknown” 구분을 스스로 어긴 사례입니다.

**[Confirmed]** 현행 모델(공식 발표 및 플랫폼 문서 확인):

| 모델 | 모델 ID | 출시 | 가격(per MTok) |
|---|---|---|---|
| Claude Fable 5 | `claude-fable-5` | 2026-06-09 | $10 / $50 |
| Claude Opus 5 | `claude-opus-5` | 2026-07-24 | $5 / $25 |
| Claude Opus 4.8 | `claude-opus-4-8` | 2026-05-28 | 레거시 |

**[Confirmed]** 위치 관계:

- Fable 5는 플랫폼 문서상 가장 능력이 높은 일반 공개 모델이며, 길고 복잡한 에이전틱 작업을 겨냥합니다.
- Opus 5는 “Fable 5의 프런티어 지능에 근접하되 절반 가격”으로 포지셔닝됩니다. 사이버보안 과제에서는
  Mythos 5보다 뒤처집니다.
- Fable 5 = Mythos 5 + 안전장치. 고위험 사이버·생물·화학 요청에서 **Opus 4.8로 폴백**합니다.
- Fable 5는 2026-06-12~06-30 수출통제로 접근이 중단됐다가 07-01 재배포됐습니다.

따라서 이 문서에서:

- `Claude Opus 5`와 `Claude Fable 5`는 **둘 다 실재하는 공개 모델**을 뜻합니다.
- 모델별 **프롬프트 조정**(§11)은 여전히 `[Heuristic]`입니다. 모델의 존재가 확인됐다고 해서
  그 모델용 프롬프트 조정의 효과가 확인된 것은 아닙니다.
- A/B 평가 대상은 `claude-opus-5`와 `claude-fable-5`입니다. Opus 4.8은 마이그레이션 비교용으로만 씁니다.

공식 자료:

- [Introducing Claude Opus 5](https://www.anthropic.com/news/claude-opus-5)
- [Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5)
- [Redeploying Claude Fable 5](https://www.anthropic.com/news/redeploying-fable-5)
- [Claude 모델 개요](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## 1. 핵심 전환: 사고 절차보다 작업 계약을 설계한다

**[Confirmed]** 최신 Claude 계열은 명확하고 직접적인 지시, 관련 맥락, 구체적인 성공 기준에서 이점을 얻습니다. Extended thinking 계열에서는 명시적인 chain-of-thought 유도나 세세한 추론 안무를 먼저 제거하고 baseline을 측정하는 것이 공식 문서의 일반 방향과 일치합니다.

**[Framework]** 좋은 작업 명세의 기본 골격:

```text
Intent
→ Objective
→ Context
→ Constraints
→ Priorities
→ Authority
→ Uncertainty Policy
→ Success Criteria
→ Evidence
→ Escalation
```

단순한 생성 작업에는 전부 넣지 않습니다. 필요한 블록만 선택합니다.

```text
Task complexity ↑
Risk ↑
External side effects ↑
Long-horizon ↑
→ 더 많은 계약 요소가 필요
```

### 사람이 주로 정할 것

```text
왜 하는가
무엇이 달라져야 하는가
현실의 제약
우선순위
위험 허용도
권한 경계
완료 기준
```

### 모델에 맡길 기본 영역

```text
분석 방법
검색 순서
구현 전략
도구 선택
루틴하고 되돌릴 수 있는 결정
```

**[Confirmed]** 방법이나 순서 자체가 요구사항이라면 단계 지시는 여전히 유효합니다. 규제 절차, SOP, 안전 점검, 누락이 치명적인 체크리스트는 numbered steps로 명시합니다.

---

## 2. Intent와 Objective

```text
Intent = 왜 하는가?
Objective = 무엇을 달성해야 하는가?
```

예:

```text
Intent:
CEO가 제한된 자본을 어디에 배분할지 결정하도록 돕는다.

Objective:
AI 회계 자동화 시장에
Go / Conditional Go / No-Go 중 하나를 권고한다.
```

**[Framework]** Intent를 만드는 실용 공식:

```text
Actor + Decision + Success + Time Horizon
```

```text
Actor:
누가 결과를 쓰는가?

Decision:
어떤 실제 선택이나 행동을 지원하는가?

Success:
무엇이 좋은 현실 결과인가?

Time Horizon:
어느 기간을 보는가?
```

약한 지시:

```text
경쟁사를 철저히 분석해.
```

강한 지시:

```text
이 분석의 목적은 업계 개요를 만드는 것이 아니다.
창업자가 향후 12개월의 제품 투자를 결정하도록,
가격과 진입 경로를 바꿀 경쟁 증거를 식별하는 것이다.
```

---

## 3. Context: 판단을 바꾸는 정보만 넣는다

**[Confirmed]** Context는 유한한 attention budget입니다. Anthropic은 context engineering을 prompt engineering의 자연스러운 확장으로 설명하며, 전체 기록을 보관하는 것보다 현재 추론에 유용한 토큰을 선별해야 한다고 강조합니다.

포함:

```text
decision-relevant facts
current state
available resources
environment
relevant history
known risks
```

제외 후보:

```text
중복 설명
오래되어 대체된 상태
관련 없는 배경
미래에 쓸지도 모른다는 이유만으로 넣은 정보
반복된 tool output
```

**[Framework]**

```text
Context ≠ Transcript

좋은 context
= 현재 판단을 바꿀 수 있는 고신호 상태
```

---

## 4. Constraints: 방법보다 경계를 정의한다

약한 방식:

```text
1. 경쟁사를 찾는다.
2. TAM을 계산한다.
3. SWOT을 작성한다.
```

더 나은 경계:

```text
- 한국 시장 수치와 글로벌 수치를 혼합하지 않는다.
- 출처가 없는 수치를 사실처럼 제시하지 않는다.
- TAM만으로 진입 매력도를 판정하지 않는다.
```

**[Framework]** 제약을 최소 두 층으로 분리합니다.

```text
<hard_constraints>
위반하면 결과가 실패하는 조건
</hard_constraints>

<preferences>
hard constraints와 충돌하지 않을 때 최적화할 조건
</preferences>
```

필요하면 자유도도 명시합니다.

```text
<freedoms>
분석 방법, 구현 세부, 조사 순서는 모델이 결정한다.
</freedoms>
```

중요 원칙:

```text
plausible constraint
≠
confirmed hard constraint
```

사용자가 말하지 않았고 환경에서도 확인되지 않은 제약은:

- 비워 두거나
- 가정으로 표시하거나
- 결과를 크게 바꿀 때만 질문합니다.

---

## 5. Priorities: 충돌 해결 규칙

모든 목표를 동시에 최대화할 수 없을 때만 넣습니다.

```text
<priorities>
충돌하면 다음 순서로 우선한다.

1. Correctness
2. Security
3. Backward compatibility
4. Maintainability
5. Performance
</priorities>
```

**[Framework]** Priority는 장식이 아니라 trade-off policy입니다. 충돌 가능성이 거의 없는 단순 작업에는 생략합니다.

---

## 6. Authority: 자율성과 인간 개입의 경계

**[Framework]** 기본 결정 규칙:

```text
Routine + reversible
→ 모델이 결정하고 진행

Available context/tools로 해결 가능
→ 모델이 조사

Material but reversible
→ 가정을 명시하고 진행할 수 있음

High-impact or hard-to-reverse
→ 질문 또는 승인 요청
```

좋은 authority 블록:

```text
<authority>
범위 안의 조사, 파일 읽기, 로컬 수정, 테스트 실행은
독립적으로 수행한다.

사용자만 결정할 수 있는 제품 전략,
외부 메시지 발송, production 변경,
데이터 삭제처럼 결과가 중대한 행동은 실행 전에 요청한다.
</authority>
```

---

## 7. Uncertainty Policy

두 극단을 피합니다.

```text
If anything is unclear, ask me.
```

```text
Never ask questions.
```

**[Framework]** 추천 정책:

```text
context/tools로 확인 가능
→ 조사한다.

영향이 작고 되돌릴 수 있음
→ 합리적 가정으로 진행한다.

결론을 크게 바꾸는 가정
→ 명시한다.

비가역적이거나 영향이 큼
→ 질문하거나 escalation한다.
```

사실의 상태를 구분합니다.

```text
Confirmed fact
Reasonable inference
Assumption
Material unknown
```

---

## 8. Success Criteria / Definition of Done

약한 기준:

```text
좋은 결과
철저한 분석
깔끔한 코드
전문적인 문서
```

관찰 가능한 기준:

```text
- 권고가 명확하다.
- 결론을 바꿀 가정이 식별돼 있다.
- 사실과 추론이 구분돼 있다.
- 요청된 파일이 존재한다.
- 관련 테스트가 통과한다.
- public API가 유지된다.
- 중요한 unknown이 노출돼 있다.
```

**[Framework]** 판정 질문:

```text
외부 관찰자가 실제 상태만 보고
완료 여부를 판단할 수 있는가?
```

---

## 9. Evidence: 업무 유형에 맞게 요구한다

Research:

```text
Claim
→ Evidence
→ Source
→ Confidence
```

Decision:

```text
Recommendation
→ Decision-driving evidence
→ Strongest counterevidence
→ What would change the decision
```

Coding / execution:

```text
Completion claim
→ Actual changed state
→ Tests or tool results
```

단순 글쓰기:

```text
불필요한 evidence ceremony를 추가하지 않는다.
```

**[Confirmed]** 실행 가능한 테스트, 컴파일, schema 검사, 실제 상태 확인은 프롬프트상의 “다시 생각해”보다 강한 증거입니다.

---

## 10. Procedure와 Method Autonomy

다음이면 절차를 명시합니다.

```text
순서 자체가 안전 요구사항
누락이 치명적
법적·규제 절차
재현 가능한 SOP
평가 protocol
```

다음이면 방법을 모델에 맡기는 편이 낫습니다.

```text
여러 정답 경로가 존재
탐색 중 정보가 바뀜
모델이 tools/context를 보고 선택해야 함
방법이 사용자의 실제 요구사항이 아님
```

**[Heuristic]** “think step by step”, “think extremely carefully”, “verify three times” 같은 지시는 모델·과제별 이득을 측정하지 않았다면 기본 템플릿에서 제외합니다.

---

## 11. Claude Opus 5와 Claude Fable 5의 차이

아래 표는 **공식 제품 사실(`[Confirmed]`)과 프롬프트 조정 가설(`[Heuristic]`)을 분리**합니다.
두 모델 모두 실재합니다. 나뉘는 것은 모델의 존재 여부가 아니라 **조정 효과의 검증 여부**입니다.

| 항목 | Claude Opus 5 | Claude Fable 5 |
|---|---|---|
| 상태 | **[Confirmed]** 공개 모델 (2026-07-24) | **[Confirmed]** 공개 모델 (2026-06-09) |
| 가격 | **[Confirmed]** $5 / $25 per MTok | **[Confirmed]** $10 / $50 per MTok |
| 위치 | **[Confirmed]** Fable 5에 근접, 절반 가격. 에이전틱 코딩 중심 | **[Confirmed]** 최상위. Mythos 5와 동일 모델, 차이는 안전장치 |
| 프롬프트 | **[Heuristic]** 완전한 명세 upfront, 방법 자율성 | **[Heuristic]** 동일한 core + 장기 상태·권한·종료 조건 강화 |
| 검증 | **[Heuristic]** 반복적 self-check 문구는 eval 없으면 생략 | **[Heuristic]** progress claim을 관찰 가능한 상태와 연결 |
| 런타임 | **[Heuristic]** 단일 세션의 고난도 완수에 초점 | **[Heuristic]** compaction, note-taking, checkpoint가 특히 중요 |
| 보안 | **[Framework]** capability boundary 필수 | **[Confirmed]** 고위험 도메인에서 Opus 4.8 폴백. 수출통제 중단 이력 있음 |
| 운영 원칙 | 조정 가설은 A/B 평가 후 채택 | 조정 가설은 A/B 평가 후 채택 + 가용성 폴백 경로 설계 |

### Claude Opus 5 기본값

```text
Complete specification upfront
Clear intent and hard constraints
Observable success
High method autonomy
Executable validation where available
No redundant reasoning choreography
```

### Claude Fable 5 기본값

```text
Goal and scope
Autonomy boundary
Pause conditions
Canonical task state
Evidence-grounded progress
Context compaction / reset policy
Checkpoint and recovery
Delegation policy
Containment and permissions
```

**[Heuristic]** “Opus에서는 verification ceremony를 줄이고 Fable에서는 progress grounding을 강화한다”는 구분은 유용한 실험 가설입니다. 모델이 실재한다는 사실은 이 조정이 효과적이라는 근거가 아닙니다. Anthropic의 공식 권고로 취급하지 말고, 동일 workload에서 generic prompt와 model-adapted prompt를 비교해 채택하세요.

---

## 12. 잘못된 패턴과 권장 패턴

### 역할 문구만 길게 쓰기

```text
You are the world's most brilliant expert...
```

역할이 도메인·톤·책임을 실제로 바꾸지 않으면 삭제 후보입니다.

### 모든 요청에 거대한 템플릿 씌우기

```text
Simple task
→ simple specification
```

### 질문을 지나치게 많이 하기

```text
추가 정보가 있으면 더 좋아진다
≠
지금 진행할 수 없다
```

### prompt로 중요한 보안을 강제하기

```text
"production DB를 삭제하지 마"
```

만으로는 부족합니다. 실제 도구를 read-only로 만드는 mechanism이 필요합니다.

### 결과가 아니라 노력 평가하기

```text
열심히 조사했는가?
```

보다:

```text
필수 질문이 증거로 해결됐는가?
```

를 봅니다.

---

## 13. 최소 충분 명세 체크리스트

```text
[ ] 실제 intent가 보존됐는가?
[ ] observable objective가 있는가?
[ ] 판단을 바꾸는 context만 포함했는가?
[ ] hard constraints와 preferences를 분리했는가?
[ ] 사용자가 말하지 않은 constraint를 발명하지 않았는가?
[ ] 충돌할 목표에 priority가 있는가?
[ ] routine reversible decision은 모델에게 위임했는가?
[ ] uncertainty 행동 규칙이 있는가?
[ ] 완료를 실제 상태로 판정할 수 있는가?
[ ] 증거 요구가 task type에 맞는가?
[ ] 비가역적 행동의 escalation 경계가 있는가?
[ ] 제거해도 성능이 같을 문장이 남아 있지 않은가?
```

## 14. 결론

**[Framework]**

```text
좋은 prompt
=
가장 긴 prompt가 아니라
가장 작은 충분한 task specification
```

```text
Agent quality
=
Model
+ Task specification
+ Context
+ Tools
+ Harness
+ Security
+ Evaluation
```

