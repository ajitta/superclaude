# 03b — modes 감사

**대상:** `modes/` 아래 MODE 파일 8개(Brainstorming, Business_Panel, DeepResearch, Introspection, Orchestration, Task_Management, Token_Efficiency, Verbalized_Sampling)와 `RESEARCH_CONFIG.md`, `README.md`.

**전달 방식:** modes는 사용자 입력의 키워드나 플래그가 맞을 때 hook이 주입한다.

줄 번호는 감사 시점(커밋 `0c63688d`) 기준이다.

## 요약

- **가장 큰 위험: 규칙과 예시·출력 포맷이 어긋난다** (Verbalized_Sampling, Business_Panel). 현행 모델은 규칙 문장보다 예시와 출력 템플릿을 따른다.
- **두 번째 위험: 주입되지 않거나 환경에 없을 수 있는 자원을 전제한다.** RESEARCH_CONFIG.md, Workflow 도구, 저장 위치가 정해지지 않은 "persist"가 그렇다.
- **전보체 문법:** 대부분 해독된다. 다만 Token_Efficiency가 금지하는 문체를 다른 모드가 그대로 써서, 두 모드를 함께 켜면 신호가 충돌한다.
- **상호 참조는 대부분 해석된다.** handoff 대상 명령 12개, FLAGS `<mcp>`, RULES_DELEGATION `delegate_packet`, save.md `<compaction_strategy>`가 모두 실재한다.

## 발견사항

| 심각도 | path:line | 근거 인용 | 왜 문제인가 (모델 인식 관점) | 제안 | 상태 |
|---|---|---|---|---|---|
| High | MODE_Verbalized_Sampling.md:21 vs :60 | "probabilities… only AFTER the text exists" vs `### Response N (p={probability})` | 모델은 위에서 아래로 생성하므로 헤더 포맷을 따르면 확률과 라벨을 본문보다 먼저 쓴다. 사후 라벨링 원칙이 포맷 때문에 깨진다 | `p=`와 라벨을 각 블록 끝으로 이동 | 재확인, **P0 적용** |
| High | MODE_Verbalized_Sampling.md:20, 48–52 | "run the template verbatim"; VS-Multi "T1 … → T2 … → T3+" | 템플릿은 다른 모델에게 보내는 프롬프트 문장이다. 출력에 붙일지, 서브에이전트에 보낼지, 스스로 따를 지시인지 모호하다. "turn"이 사용자 턴인지 한 응답 안의 단계인지도 불명확하다 | "이 응답에서 스스로 따를 지시로 사용하고 템플릿은 출력하지 말 것", "Multi는 한 응답 안의 섹션, cutoff 시에만 `[CONTINUE]`" 명시 | P1 |
| High | MODE_Business_Panel.md:20 vs :54 | "Synthesis-First: Integrate… before show individual views" vs 예시 "Porter:… Kim:… Synthesis:" | 예시는 개별 관점 → 종합 순서라서 규칙과 반대다. 모델은 예시를 따를 가능성이 크다 | 순서를 하나로 통일 | 재확인, **P0 적용** |
| High | MODE_Business_Panel.md:45, 49 vs :54–55 | "Market entry \| Porter + Kim \| Debate", "Communication \| Doumont + Godin \| Socratic" | 예시에는 Taleb이 추가되고 Debate 구조(Position→Challenge→Rebuttal)도 Socratic 질문도 없다. 라우팅 표가 무력화된다 | 예시를 라우팅 표에 맞게 재작성 | 재확인, **P0 적용** |
| Med | MODE_DeepResearch.md:3 | "Operational params… reference RESEARCH_CONFIG.md." | loader가 주입하지 않는 파일이고 경로도 없다. 모델은 무시하거나 파일을 찾느라 도구 호출을 낭비한다 | 핵심 값(소스 3개 게이트, replan 트리거)을 모드 본문에 넣고 나머지는 설치 경로로 명시 | P1 |
| Med | MODE_DeepResearch.md:13, 24 vs :31 | "Lead with confidence", "Per-claim confidence stated" | "Lead with confidence"는 "단정적으로 써라"로도 읽혀 "Acknowledge uncertainty"와 충돌한다. per-claim 신뢰도는 예시에 없어서 무시되거나 모든 문장에 붙는 과적용이 생긴다 | "답과 그 신뢰 수준으로 시작"처럼 완전한 문장으로 쓰고, 신뢰도는 결론을 떠받치는 핵심 주장에만 적용 | P1 |
| Med | MODE_Orchestration.md:24–30 | "Workflow tool… ships no runtime for", `agent()`, `opts.schema` | 도구가 존재한다고 전제한다. 도구가 없는 사용자 환경에서는 존재하지 않는 도구를 호출하거나 흉내 낼 위험이 있다. 함께 참조하는 RULES_DELEGATION.md는 `--orchestrate`만으로는 주입되지 않는다 | 섹션 첫 줄에 "Workflow 도구가 도구 목록에 있을 때만" 조건 추가 | P1 |
| Med | MODE_Task_Management.md:14, 20, 32 | "Memory persist > ephemeral ctx", "never… bypass task hierarchy" | 무엇을 어디에 저장할지 정해져 있지 않아(예시 :27에만 `.claude/memories/`) 사용자 저장소에 파일을 임의로 만들 수 있다. "never bypass"는 4단계짜리 작업에도 Plan→Phase→Task→Todo를 강제한다 | 세션 내는 TaskCreate/TodoWrite, 세션 간은 `/sc:save`로 명시하고 계층 깊이는 작업 크기에 비례하게 | P1 |
| Med | RESEARCH_CONFIG.md:7 vs :19–21 | "planning: unified… (DEFAULT)" vs "Planning-Only \| clear query \| Run now" | 기본값 unified("Show plan, get feedback") 때문에 명확한 질의에도 승인 대기로 멈출 수 있다 | 기본값을 질의 명확도로 선택하게 하거나 unified의 적용 조건 명시 | P1 |
| Med | RESEARCH_CONFIG.md:46, 76 | "≥3 independent sources", "replan when… fewer than 3" | 공식 문서 하나로 결정되는 주제에서도 replan 루프에 빠진다. 이유가 없어서 예외를 일반화하지 못한다 | "tier-1 단일 출처로 충분한 경우는 예외"와 근거 추가 | P1 |
| Med | MODE_Introspection.md:13, 19, 27 | "📊 metrics", "Compare… vs past patterns", "auth.js:15, config.js:22" | 정의되지 않은 metrics와 존재하지 않는 "past patterns"가 수치와 이력을 꾸며내도록 유도한다. 예시의 file:line 인용이 모방된다 | "이번 세션에서 읽은 위치만 인용"으로 제한하고 📊를 정의하거나 삭제 | P1 |
| Med | MODE_DeepResearch.md:15 vs MODE_Token_Efficiency.md:14; README.md:43 | "Completeness > speed" vs "Selectivity > completeness"; "`--research --uc`" | README가 권장하는 조합에서 우선순위가 정면으로 충돌하는데 우선순위를 정하는 규칙이 없다 | TE는 표현에만, Research는 조사 범위에만 적용된다고 명시 | P1 |
| Med | MODE_Brainstorming.md:13, 34 | "Ask q's > give answers", "never prescribe solutions" | 사용자가 명시적으로 추천을 요청해도 질문만 반복한다. 이유가 없다 | "추천을 요청받으면 옵션 형태로 제시" 예외 추가 | P1 |
| Low | MODE_DeepResearch.md:7–8; MODE_Business_Panel.md:8; MODE_Brainstorming.md:3 | "structure investigation methodical, no casual", "every claim need verify", "insight live there", "Collab… reqs" | 의미는 복원되지만 TE:42가 금지하는 "dropped articles, invented abbreviations"와 같은 문체다. 함께 켜면 신호가 충돌하고 출력 문체로 옮겨간다 | 완전한 문장으로 재작성 | P2 |
| Low | MODE_Token_Efficiency.md:23–25, 36, 38 | "Ultracode Posture", "answer quality degrading", "Clear old tool call results" | "ultracode"는 미정의 용어다. 품질 저하는 모델이 자체 측정할 수 없다. 도구 결과 삭제는 모델이 수행할 수 없는 동작이다 | 삭제하거나 실행 가능한 지시로 교체 | P2 |

참고: README.md:28의 "confidence thresholds"는 낡은 기술이다(RESEARCH_CONFIG에 해당 값이 없다). README는 주입되지 않으므로 유지보수자용 정정 대상이다.

## 공통 패턴

- **규칙보다 예시가 이김:** Business_Panel, DeepResearch, VS 포맷 세 곳에서 예시가 규칙과 어긋난다. 현행 모델은 예시를 우선 모방하므로 규칙이 사실상 무효가 된다.
- **로드되지 않은 자원 전제:** RESEARCH_CONFIG, RULES_DELEGATION, Workflow 도구, 저장 위치. 사용자 프로젝트에서 경로가 해석된다는 보장도 없다.
- **이유 없는 절대 표현(`<never>`):** 사용자 의도에 따른 예외로 일반화할 근거가 없다 (Brainstorming, Task_Management, RESEARCH_CONFIG 게이트).
- **`<fallback>Revert to default when N/A`:** 명시적 플래그로 켜졌을 때 무엇이 "N/A"인지 기준이 없다. 실제로 의미 있는 경우는 키워드 오탐지뿐이니 그렇게 한정해 쓰면 좋다.
- **XML 구조 혼용:** Business_Panel(:24, 37, 42)과 TE(:23, 35)는 XML 본문 안에 `##` 헤더와 태그 없는 섹션을 섞어 다른 모드와 구조가 다르다. 영향은 작다.

## 강점

- DeepResearch의 Name-Verification(:21)과 인용 예시(:26–33)는 이유를 함께 제시하며 현행 모델의 약점(빠르게 변하는 고유명사, 과다 인용)을 정확히 겨냥한다.
- Token_Efficiency의 "생략을 통한 간결성, 문장 압축 금지, 생략 사실 공개(Omission-Disclosure)"는 현행 모델 행동과 잘 맞는다.
- VS의 gotchas(task-fit, population-sim, calibration 금지)는 이유가 붙어 있어 일반화가 잘 된다.
- 구세대 관용구가 없다.
- Introspection의 communication 줄(결정, 근거, 기각한 대안, 미검증 항목)은 좋은 보고 계약이다.
