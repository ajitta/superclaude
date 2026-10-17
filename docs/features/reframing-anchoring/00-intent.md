---
status: approved-for-plan
revised: 2026-10-17
---

# Intent: 모델이 행위 지시 뒤의 궁극 목적을 인식하게 만드는 src/superclaude 재구성 (context reframing · anchoring 축)

Author: ajitta.

2026-10-17 세션의 요청과 결정(Q1–Q6)을 요청자의 말로 기록한다. 계획은 `.hermes/plans/2026-10-17_190849-reframing-anchoring-restructure.md`(v3).

## Problem

원문 요청:

> "src/superclaude/... 내용을 감사. sonnet 5.5, opus 5.5, fable 5.1 은 대부분의 경우 충분히 잘 수행한다. 이것들이 하지 못하는 부분은 context reframing, anchoring 과 연관된것이다. 이 부분은 더 조사하고, src/superclaude를 재구성하여 조사 탐색, 조사연구를 적용하는 방안을 탐구하라."
> "ponytail skill을 이용하여 구조와 구현을 다시 감사하라."

최종 목적(Q5):

> "예를 들어, 고객의 메일에 대해 응답메일을 한다고 가정해보자. 응답메일 작성해서 보내라고 하는 지시는 잘 수행할 거야. 문제는 그 메일의 궁극적 목적, 고객의 불만을 잠재우고 이탈을 잠재우고 오히려 고객이 만족감을 [느끼게 하는] 목적을 메일작성에 넣으면 완전히 다른 결과물을 보낼거야. 나는 이런 궁극적인 목적을 모델에게 잘 인식시키는 것이 목표야. 모든 가이드는 의도를 잘 표현하라는 모호한 말로 가이드를 제시하지만 대부분의 사람들은 행위 지시를 의도라고 생각하고 있다. 거의 모든 인공지능 이용하는 사람들이 그럴거야. 그건 메일을 보내라고 지시했으니 인공지능이 알아서 잘 생성해서 보내는 것을 기대하기 때문이다. 이게 나의 궁극적이며 최종적인 목적이다 '의도를 어떻게 인공지능이 인식하게 만드냐'"

배경:

> "이 프로젝트는 작년에 나와있었던 SuperClaude framework를 포크해서 시작한 것이다. 그당시 sonnet3.5가 나오면서 엄청나게 인기가 있었지만. 모델들의 성능이 향상되면서 지나친 지시와 제어가 품질을 오히려 떨어뜨리는 결과를 가져오면서 시들해졌다. hermes agent, ecc, superpower 같은 것이 인기가 있기는 하지만, 너무 방대하고 모델이 이미 알아서 잘 하는 것들이 많은데 그것을 강제하는 경향이 있어. 좀 쓰는 것이 능숙해지면 ECC, SUPERPOWER를 안쓰게되더라.(나의 경험)."

## Proposed outcome

1. 조사연구: 목적 인식·anchoring·context reframing에 대한 증거와, 현행 모델에서 효과가 측정된 구조적 치료법 목록.
2. 조사 탐색 감사: `src/superclaude` 콘텐츠를 "모델이 이미 하는 것 / 구조적 치료법 / 프로젝트 정보 / 그 외"로 분류하고, 재구성 대안을 비교해 사용자가 결정.
3. ponytail 재감사: 구현(cli·scripts·hooks·tests)에 스킬 그대로, 콘텐츠 구조에 lean 기준 전용 (Q2).
4. 재구성 원리(Q1-a): "앵커·틀을 받기 전에 먼저 탐색하고 자체 기준을 세우는 구조".

## Affected users and systems

- `src/superclaude` 콘텐츠 전체(core, core/rules, modes, agents, commands, skills)와 Python 구현(cli, scripts, hooks, tests, evals).
- 이 포크를 설치하는 사용자 프로젝트(배포 콘텐츠가 바뀐다).
- 측정 인프라 `evals/`(새 fixture·canary).

## Constraints

- 측정 모델: sonnet + opus, headless 세션 최대 180 (Q3). Fable headless는 금지(AGENTS.md).
- 어제(2026-10-17 00:35) ponytail lean 감사 보고서는 저장소에 미반영·미검증 — 사용자 확인: "내가 혼동한것이다." 계획대로 Phase 3에서 검증 후 공통 삭제 배치에 포함(결정 1).
- 브랜치 `feature/reframing-anchoring`은 Phase 0 시작 시 생성(Q6). 커밋·병합·push는 각각 사용자 지시 때만.
- 선행 작업과 중복하지 않는다: `prompt-content-audit`(읽힘 축), `persona-anchoring-framing-audit`(S1–S18, P1–P5), `over-engineering-audit`(keep 결정).
- 의사 결정이 필요하면 사용자에게 대화를 요청한다: "필요한 의사 결정이 필요하면 나에게 대화를 요청해". 긴 답은 폼이 아니라 채팅으로 받는다.

## Open questions

- 목적 충족("고객이 만족하는 메일")을 harness의 boolean check로 어디까지 대리 측정할 수 있는가 — Phase 1에서 fixture 설계로 답한다.
- Phase 4 대안(격차 게이트 / anti-anchoring 커널 / 훅 강제 / 의도 선행 구조) 중 어느 것을 채택할지 — 사용자 결정.
