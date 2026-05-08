---
status: draft
revised: 2026-05-05
---

# Rule vs. Instruction — 저작 가이드 디스커버리

> 이 디스커버리 스펙은 SuperClaude 저자들이 프레임워크 콘텐츠 트리에서 "rule" 콘텐츠(항상 켜져 있는 행동 불변량)와 "instruction" 콘텐츠(작업 트리거 방식의 의사결정 참조)를 어떻게 구별해야 하는지, 그리고 이 구별을 일관되게 적용하는 데 어떤 저작 메타 문서 추가가 도움이 될지를 탐구합니다.

## 1. 발단

이 디스커버리는 `src/superclaude/core/RULES.md`의 토큰 비용 분석(커밋 `bc2a318`, 2026-05-05)에서 시작되었습니다. 해당 파일은 **174줄 / 약 6.6K 토큰**이며, 그 구성은:

- 35.7%는 `<core_rules>` (R01–R20 규칙 정의 + 16행 예시 테이블).
- ~28%는 **의사결정 참조 콘텐츠** — "행동 불변량" 형태가 아닌 "작업 트리거 가이드" 형태: `<sub_agent_decision>` (10.7%), `<agent_routing>` (9.6%), `<doc_output_convention>` (7.7%).
- 나머지 ~36%는 예시 테이블, 안티패턴 블록, 소규모 불변량.

RULES.md는 항상 로드되는 `@superclaude/CLAUDE_SC.md` 임포트 체인의 일부입니다 (FLAGS 2.1K + PRINCIPLES 1K + RULES 6.5K = 모든 대화에 ~9.6K 토큰 주입). **이 디스커버리를 촉발한 관찰**: RULES.md의 모든 내용이 항상 로드될 필요는 없습니다. 의사결정 매트릭스와 참조 테이블은 기존 동적 주입 메커니즘(`src/superclaude/scripts/context_loader.py`의 `TRIGGER_MAP` / `INSTRUCTION_MAP`)을 활용할 수 있지만, 프레임워크 저자들에게는 행동 콘텐츠를 항상 켜진 체인에 넣을지 동적 주입 참조 파일에 넣을지에 대한 서면 가이드가 없습니다.

이 디스커버리의 산출물은 **저작 가이드**이지 리팩터링이 아닙니다. 리팩터링 계획은 하위 단계입니다.

## 2. 범위

포함:
- `src/superclaude/` 아래의 SuperClaude 콘텐츠 트리 (core, components, modes, mcp, scripts).
- `.claude/rules/`의 다섯 개 `*-authoring.md` 메타 문서와 `xml-prose-format.md`.
- 기존 동적 주입 메커니즘: `context_loader.py`의 `TRIGGER_MAP`, `INSTRUCTION_MAP`, `TIER_0_MAP`, `COMPOSITE_FLAGS`.

제외:
- LLM 업계 컨텍스트 엔지니어링 이론 (Karpathy, Anthropic 공개 문서) — 배경 참조만, 산출물 아님.
- RULES.md 자체 리팩터링. 이는 이 스펙을 입력으로 사용하는 별도 `/sc:plan` 사이클입니다.
- 개별 컴포넌트 본문 재저작. 저작 가이드가 기준을 제공하고, 기존 컴포넌트에 적용하는 것은 하위 단계.
- 훅 및 기타 CC 네이티브 주입 경로 (system-reminders, PreToolUse) — 개념적으로 같은 축을 공유하지만 프레임워크 콘텐츠 트리 외부에 있음.

## 3. 확정된 결정 사항

브레인스토밍 대화 2026-05-05 §3에서 수집:

| Q | 결정 | 방식 | 근거 |
|---|---|---|---|
| Q1: 질문의 출처 | **1a — 진단적 동기, RULES.md 6.6K 분석에 기반** | 확정 | 사용자가 리터럴 옵션 문자 `1a` 입력. |
| Q2: 산출물 형태 | **2b — `.claude/rules/*-authoring.md` 저작 가이드 추가** | 확정 | 사용자가 리터럴 옵션 문자 `2b` 입력. |
| Q3: 범위 | **3a — SuperClaude 프레임워크만** | 확정 | 사용자가 리터럴 옵션 문자 `3a` 입력. |

세 결정 모두 `confirmed` 모드. 위임된 결정 없음. 따라서 §10의 `/sc:review` 핸드오프에 감사 의무 없음.

## 4. 질문 프레이밍

오늘날 프레임워크 저자들이 직면하는 실질적 질문: **"행동 콘텐츠 한 조각이 있는데. 어디에 넣어야 하나?"**

현재의 선택지 — 암묵적이고 문서화되지 않음:
1. `core/RULES.md` (항상 켜짐, 수동 큐레이션, ~6.6K).
2. `core/FLAGS.md` / `core/PRINCIPLES.md` (항상 켜짐, 역할 특화).
3. `core/<DOMAIN>.md` (예: `BUSINESS_SYMBOLS.md`) — `TRIGGER_MAP`을 통해 동적 로드.
4. 컴포넌트별 XML 본문 (`commands/*.md`, `agents/*.md`, `modes/*.md`, `skills/*/SKILL.md`, `mcp/*.md`).
5. 컴포넌트별 examples / gotchas 섹션 (본문 내).

저작 가이드 없이 역사적으로 나타난 편향: **"프레임워크 전반적으로 느껴지는" 모든 것이 RULES.md에 들어감** — 특정 동사(`<sub_agent_decision>`은 위임 시에만, `<doc_output_convention>`은 `/sc:plan`/`/sc:design`/`/sc:brainstorm` 실행 시에만 필요)에서만 발동하는 의사결정 매트릭스도 예외 없이. 이는 항상 켜진 비용을 늘리지만 항상 켜진 효과는 얻지 못합니다.

디스커버리 산출물: rule과 instruction을 구별하는 **콘텐츠 분류**, 저자들이 적용할 수 있는 **의사결정 트리**, 구별을 확실히 하기 위한 **안티패턴 예시**.

## 5. 작업 분류 체계 — 4개 축

브레인스토밍에서는 6개 축(Lifetime, Voice, Authority, Source, Compaction, Conflict)을 제안했습니다. 두 가지는 **파생** 축으로 수렴하여 제외: Compaction 우선순위는 Lifetime에서 파생(항상 켜진 콘텐츠는 배치로 압축에서 살아남음); Conflict 해결은 Authority에서 파생(우선순위 계층 자체가 rule 형태).

4개의 핵심 축:

### Voice (어조)
- **Rule:** 선언적, 3인칭, 행동적. *"Claude는 X를 한다."* / *"절대 Y하지 않는다."*
- **Instruction:** 명령형 또는 참조 형태. *"위임 시, 에이전트를 … 기준으로 선택한다."* / *"`docs/<type>/…`에 출력한다."*

이것이 표면적 형태입니다. Opus 4.7은 선언적 어조를 핵심으로 읽고 완화 표현("should", "might", "consider")을 선택 사항으로 버립니다. 참조 형태의 테이블은 그 자체로 핵심이 아니며, 관련 동사가 나타날 때 참조됩니다.

### Lifetime (수명)
- **Rule:** 모든 대화, 모든 턴. 비활성화 옵션 없음.
- **Instruction:** 동사/범위/컨텍스트에 의해 트리거됨. 트리거가 발동하지 않을 때 생략해도 안전.

명확한 테스트: *"/sc:brainstorm을 한 번도 호출하지 않는 30턴 디버깅 세션에서 이 콘텐츠를 생략하면 해로운가?* 그렇다 → rule. 아니다 → instruction.

### Authority (권위)
- **Rule:** 행동 공간을 제한함. 에이전트가 무엇을 하든 상관없이 유지되는 불변량을 정의함.
- **Instruction:** 이미 경계가 설정된 공간 내에서 특정 행동을 지시함. 에이전트에게 *무엇이 허용되는지*가 아닌 *어떻게 할지*를 알려줌.

R10("근본 원인 분석, 항상 테스트")은 rule 형태 — 모든 구현을 제한함. 에이전트 라우팅 매트릭스는 instruction 형태 — "서브 에이전트에 위임하기"라는 이미 결정된 행동 *내에서* 선택을 지시함.

### Source (출처)
- **Rule:** `src/superclaude/core/` + `src/superclaude/CLAUDE_SC.md` 임포트 체인 아래의 커밋된 프레임워크 코드. 프레임워크 유지보수자가 저작; 동적 주입 없음.
- **Instruction:** 동적 로드 참조 파일(`mcp/`, `modes/`, `core/BUSINESS_SYMBOLS.md`), 컴포넌트별 본문, 또는 훅에 위치. 프레임워크 유지보수자뿐 아니라 컴포넌트 저자도 저작 가능.

Source는 **운영** 축 — 저자에게 어느 파일에 쓸지 알려줌. 다른 세 축은 콘텐츠의 *종류*를 결정하고, Source는 *위치*를 결정함.

## 6. 기존 메커니즘 (이미 있는 것)

프레임워크에는 이미 instruction 형태 콘텐츠를 위한 배관이 있습니다. `src/superclaude/scripts/context_loader.py`는 사용자 프롬프트의 정규식 패턴으로 트리거되는 3-티어 주입 모델을 정의합니다:

| 티어 | 메커니즘 | 토큰 비용 | 사용 대상 |
|---|---|---|---|
| Tier 0 | `TIER_0_MAP`의 1줄 요약 | ~10–25 토큰 | 도구 MCP (Context7, Sequential, Playwright, DevTools), 보조 참조 |
| Tier 1 | `INSTRUCTION_MAP`의 다단락 지시 | ~150–250 토큰 | 행동 MCP (Serena, Tavily) — 워크플로 패턴, 의사결정 규칙 |
| Tier 2 | 전체 `.md` 본문 | ~500–2000 토큰 | 모드(Brainstorming, Token-Efficiency 등) 및 패턴 충실도가 필요한 행동 MCP |

Plus `COMPOSITE_FLAGS` (`--frontend-verify`, `--all-mcp`) 원샷 다중 파일 주입용.

빠진 것: **`BUSINESS_SYMBOLS.md` 외에 core/ 파일들은 `TRIGGER_MAP`에 없습니다.** `RULES.md`/`FLAGS.md`/`PRINCIPLES.md`는 `CLAUDE_SC.md`를 통해 정적 `@`-임포트되며 티어 태그가 없습니다. 현재 RULES.md에 있는 의사결정 참조 콘텐츠는 형태상으로는 Tier 0/1/2에 맞지만, 탈 것이 없습니다.

## 7. 저작 의사결정 트리

"이 콘텐츠는 어디에 가는가?" — 저자 관점에서의 제안 테스트:

1. **콘텐츠가 항상 참인 행동 불변량인가?** *(Voice: 선언적; Lifetime: 모든 대화; Authority: 행동 공간 제한)*
   - 그렇다 → `core/RULES.md` (또는 도메인별로 `FLAGS.md`/`PRINCIPLES.md`).
   - 아니다 → 계속.

2. **작업 트리거 의사결정 참조인가?** *(Voice: 참조/매트릭스; Lifetime: 동사 발동 시에만; Authority: 경계 내 선택 지시)*
   - 여러 컴포넌트에서 프레임워크 전반으로 사용됨 → `core/<DOMAIN>.md` + `TRIGGER_MAP` 항목 추가. 티어 선택:
     - 단일행 조회, 워크플로 없음 → Tier 0.
     - 의사결정 규칙이 있는 다단락 워크플로 → Tier 1.
     - 패턴 충실도를 위해 전체 본문 필요 → Tier 2.
   - 정확히 한 컴포넌트에서만 사용됨 → 해당 컴포넌트 XML 본문의 적절한 섹션 태그 아래 유지 (`<flow>`, `<patterns>`, `<focus_agent_mapping>` 등).

3. **일시적/턴별인가?** (사용자 메시지, 훅 주입, system-reminder.) → 프레임워크 콘텐츠 트리 외부. SuperClaude의 저작 관심사 아님.

콘텐츠가 1단계와 2단계에서 각각 다른 방식으로 실패할 수 있음. 태그 수준 신호:

| 태그 형태 | likely 카테고리 | 기본 위치 |
|---|---|---|
| `<core_rules>` 번호 매긴 목록 (R-rules) | Rule | `core/RULES.md` |
| `<priority_system>` / `<thresholds>` | Rule | `core/RULES.md` |
| 동사 키 행이 있는 의사결정 매트릭스 (예: `<agent_routing>`, `<sub_agent_decision>`) | Instruction | 동적 로드 core 파일 (Tier 1 또는 2) |
| 출력 형식 / 디렉토리 매핑 | Instruction | 관련 동사 키의 동적 로드 core 파일 (Tier 0 또는 1) |
| rule에 붙은 예시 테이블 (`<examples>`) | Rule에 인접 — 부모와 같이 이동 | 규칙과 같은 파일 |
| 컴포넌트별 flow / patterns / tools | Instruction (컴포넌트 범위) | 컴포넌트 XML 본문 |

## 8. 혼합 콘텐츠 감사 — RULES.md 위반 사례

현재 `core/RULES.md`에서 rule과 instruction 콘텐츠가 혼재하는 구체적 사례:

- **`<sub_agent_decision>` (13–30줄, ~600 토큰).** 혼합: *트리거 휴리스틱* ("3개 이상의 독립적인 병렬 스트림", "3단계 미만")은 rule 형태 — 서브 에이전트 적절성을 제한함. *7행 예시 매트릭스*는 instruction 형태 참조. 동사 트리거: 서브 에이전트 생성 의도 (`--delegate`, `--p`, "audit", "research X + Y + Z"). 후보 분리: RULES에서 2줄 불변량 유지 (Direct vs Sub-agent vs Never), 매트릭스는 `core/AGENT_ROUTING.md` Tier 1으로 이동.
- **`<agent_routing>` (32–44줄, ~550 토큰).** 순수 instruction 형태. 동사 트리거: 위와 동일, 추가로 단일 트리거 모호성 동사 (`optimize`, `refactor`, `test`, `teach`, `research`, `docs`). 항상 로드될 필요 없음. 후보: 동일한 `core/AGENT_ROUTING.md` Tier 1 또는 2.
- **`<doc_output_convention>` (146–158줄, ~510 토큰).** 순수 instruction 형태 (디렉토리/접미사/상태 매핑). 동사 트리거: 파일 생성 명령 (`/sc:brainstorm`, `/sc:design`, `/sc:plan`, `/sc:workflow`, `/sc:analyze`, `/sc:research`, `/sc:document`). 항상 로드될 필요 없음. 후보: `core/DOC_CONVENTIONS.md` Tier 1.
- **`<core_rules>` 예시 테이블 (64–83줄, ~990 토큰).** Rule에 인접. 기본적으로 R01–R20과 함께 유지. 항상 켜진 rules 블록을 줄여야 한다면 형제 `core/RULES_EXAMPLES.md` Tier 0/1으로 분리 가능하지만 우선순위 낮음 — 예시는 모호성 해소 시점에 규칙을 보강하며 16행이 20개 규칙 전체에 걸쳐 있어 부분 주입이 어색함.
- **`<anti_over_engineering>` (91–109줄, ~620 토큰).** 혼합: 산문 규칙 ("Bug fix ≠ cleanup", "Earned > Premature")은 rule 형태; 5행 예시 테이블은 rule에 인접; `<model_tendencies>` 블록은 rule 형태 (불변 모델 행동 설명). RULES에 유지.

예상 추출량 (하위 `/sc:plan`이 분리를 채택할 경우): 항상 켜진 체인에서 ~1,660 토큰 제거 (-RULES.md의 25%). 이는 저작 가이드 결과의 **상한선**이지 약속이 아닙니다.

## 9. 제안된 저작 가이드 추가 사항

이 디스커버리의 산출물은 두 개의 기존 메타 문서에 대한 콘텐츠이지 새 파일이 아닙니다. (파일 하나당 개념 하나의 위생 원칙; 별도 `rule-vs-instruction.md`는 주제를 고립시킬 것임.)

### 9.1 `xml-prose-format.md`에 새 섹션 추가

제목: **Rule vs. Instruction 콘텐츠**. 배치: "Section Ordering" 이후 "Root Structure" 이전 — 본문 형식 규칙의 동료 위치인 콘텐츠 분류 규칙.

콘텐츠 (설계 단계를 위한 초안 형태 제안):
- §5의 4개 축을 컴팩트 테이블로.
- §7의 의사결정 트리를 번호 산문으로 (1./2./3.).
- §7의 태그 형태 조회를 테이블로.
- 짧은 예시 블록 한 개: "이 콘텐츠는 어디에 가는가?" — 가상의 저자가 `<sub_agent_decision>`을 통해 rule-부분-유지 / 매트릭스-추출 분리를 보여줌.

예상 추가 크기: ~80–110줄 / ~3K 토큰. xml-prose-format.md는 현재 ~6.6K 토큰; 추가 후 ~9.5K. 이는 스펙 자체의 비컴포넌트 메타 문서 크기 가이드 내 (xml-prose-format의 크기 목표는 컴포넌트에 적용되며 메타 문서 자체에는 상한 없음).

### 9.2 각 `*-authoring.md`에 교차 참조 블록 추가

다섯 개 유형별 메타 문서 (`agent-`, `command-`, `mode-`, `skill-`, `mcp-authoring.md`)에는 이미 "xml-prose-format.md에서 상속됨" 섹션이 있습니다. 이 디스커버리는 그 상속을 한 줄 포인터로 확장합니다:

> Rule vs. Instruction 콘텐츠 분류 — xml-prose-format.md §"Rule vs. Instruction 콘텐츠" 참조. `<…>` 섹션을 저작할 때, 그 콘텐츠가 항상 켜진 rule 형태인지 작업 트리거 instruction 형태인지 결정하세요; instruction 형태 콘텐츠는 동적 로드 core 파일이나 컴포넌트별 본문에 속하며, `core/RULES.md`에 있으면 안 됩니다.

컴포넌트별 저작 문서는 이미 크로스커팅 xml-prose 규칙을 반영함; 이것은 같은 패턴.

### 9.3 이 가이드가 규정하지 않는 것

- **특정 TRIGGER_MAP 항목 없음.** 저자들이 제안하고 프레임워크 유지보수자들이 새 항목을 게이트키핑함 (`TRIGGER_MAP`은 의견이 강한 인프라).
- **"프레임워크 전반 vs 단일 컴포넌트"의 임계값 없음.** 결정은 질적; 트리가 신호를 제공하지만 숫자 커트라인을 강제하지 않음.
- **소급 적용 없음.** 기존 컴포넌트와 core 파일은 위반이 아닙니다. 가이드는 전향적; 혼합 콘텐츠 리팩터링은 별도 계획 사이클.

## 10. 핸드오프

이 스펙은 `/sc:plan`으로 진행하기 전에 `/sc:review`를 통과해야 합니다 (`/sc:brainstorm` 플로우 6단계 — 필수 게이트, 권장 아님).

**`/sc:plan` 전에 이 스펙에 `/sc:review`를 실행하세요. 계획 핸드오프는 검토에 게이트됨.**

(§3의 모든 결정은 `confirmed` 모드; 감사 의무 문구 불필요.)

§11에 검토 반복 로그가 추가되고 상태가 `approved-for-plan`으로 올라간 후, 계획 사이클이 목표로 해야 할 것:
- `xml-prose-format.md` §"Rule vs. Instruction 콘텐츠" 섹션을 구체적인 산문으로 초안 작성.
- 각 `*-authoring.md`에 대한 교차 참조 블록 초안 (5개 파일).
- 구조적 테스트 스위트 (`tests/structural/`)가 core/* 파일에 instruction 형태 콘텐츠가 없음을 검증해야 하는지 테스트 추가 (범위 외 질문으로 계획 단계에서 다룰 것, 여기서 확정하지 않음).

*별도* 하위 계획이 이 가이드를 입력으로 사용해 RULES.md를 리팩터링합니다 (§8 감사). 그 계획은 이 디스커버리의 일부가 **아닙니다**; 이 가이드가 출시되고 유용성이 입증된 경우에만 시작해야 합니다.

## 11. 셀프 리뷰 반복 로그

*`/sc:review`가 채울 예정.*

| 라운드 | 날짜 | 검토자 | 요약 | 해결됨 |
|---|---|---|---|---|
| _v1 baseline_ | 2026-05-05 | 저자 | 브레인스토밍에서 초기 초안 | n/a |

## 12. 비목표 및 설계 단계로 미룬 열린 질문들

`/sc:plan`으로 미룬 열린 질문들 (여기서 해결하지 않음):

1. **`xml-prose-format.md` 자체가 일반 마크다운으로 유지되어야 하는가** (현재 형태, 자체 §범위 주석에 따라) 아니면 새 §"Rule vs. Instruction" 섹션이 그것이 문서화하는 XML 본문 형식을 채택해야 하는가? 메타 문서는 SuperClaude 컴포넌트가 아니므로 일반 마크다운도 허용됨; 파일 나머지와의 일관성이 더 단순한 선택.
2. **새 core/* 추출의 Tier-0 vs Tier-1 커트라인** — `core/AGENT_ROUTING.md`가 Tier 1 (instruction-단락)이 될 수도 Tier 2 (전체 본문)가 될 수도 있음; 답은 7행 매트릭스가 ~200 토큰으로 충실하게 표현 가능한지에 달림. 하위 리팩터링 계획에 속함, 이 가이드 아님.
3. **구조적 테스트 스위트가 rule/instruction 분류를 강제해야 하는가?** 예: 항상 로드되는 core/* 파일에서 의사결정 매트릭스 테이블에 플래그를 다는 테스트. 설계 단계에서 후보 테스트로 제시; 여기서 확정하지 않음.
4. **명명.** "Rule vs. Instruction"이 최선의 레이블인가, 아니면 "Invariant vs. Reference"가 더 적은 모호성으로 구별을 전달하는가? Voice 테스트 (선언적 vs 명령적)는 rule/instruction 분리가 Anthropic 자체의 system-vs-user 프롬프트 관례를 더 잘 추적한다고 시사함; 검토자 판단.
