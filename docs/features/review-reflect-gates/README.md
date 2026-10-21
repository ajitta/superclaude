---
feature: review-reflect-gates
phase: implementing
owner: ajitta
created: 2026-10-21
updated: 2026-10-21
related: ../../analysis/review-reflect-gate-gap-ajitta-2026-10-21.md
---

# review·reflect 게이트 맞추기

README 작업 크기 표의 Medium·Large 체인은 `/sc:reflect`로 끝나는데, RULES_DOCS `workflow_gates`는 `/sc:test -> done`에서 끝나고 리뷰 뒤 수정을 다시 리뷰하라는 줄도 없다. 2026-10-21 session-memory-multi-machine 작업에서 두 단계가 실제로 빠졌다. 원인 분석은 [review-reflect-gate-gap](../../analysis/review-reflect-gate-gap-ajitta-2026-10-21.md)(항목 B)에 있다.

소유자 결정(2026-10-21):

- reflect 게이트는 RULES_DOCS `workflow_gates`에 둔다.
- 리뷰 뒤 리뷰된 코드나 shipped 내용을 바꾼 수정은 다시 리뷰한다는 줄을 넣는다.
- RULES_DOCS는 `/sc:test`에서 로드되지 않으므로(`context_loader.py:191`) `test.md` handoff에도 `/sc:reflect`를 넣는다. handoff만으로 답이 바뀌지 않아(0/3) `test.md` Report 단계에 한 줄을 더한다.
- 리뷰 1차 뒤: `/sc:intent --through`는 한 번의 수정 round를 유지하는 예외를 게이트에 둔다(`intent.md`는 그대로). 계획 `complete`가 reflect보다 먼저 오는 문제는 이 기능 밖의 후속 항목이다(분석 문서 D).
- 리뷰 2차 뒤: RULES_DOCS는 `/sc:review`에서도 로드되지 않으므로 `review.md` Process 단계에 재리뷰 한 줄을 둔다.
- 이 실패를 재는 canary 프로브를 더한다.
- 독립 검증([06a](./06a-verify-independent.md)) 뒤: 권고안을 모두 반영하고, 반복된 리뷰 round를 통과하려고 들어간 덧댐·예외·중복을 정리한다. `implement.md` Integrate에도 재리뷰 구절을 둔다.
- 릴리스는 보류한다. 이 기능은 master 병합까지만 한다.

## Documents

- [05-plan.md](./05-plan.md): implementation plan
- [05a-plan-measurements.md](./05a-plan-measurements.md): probe measurements (moved out of the plan)
- [06-review.md](./06-review.md): branch review rounds
- [06a-verify-independent.md](./06a-verify-independent.md): independent verification of 81776c29 (headless opus, Linux)
- [06b-verify-fixes.md](./06b-verify-fixes.md): second independent verification, of the 06a fixes (4223ed1d)
- [06c-verify-phase10.md](./06c-verify-phase10.md): third independent verification, of the 06b fixes (56da83a1)
- [06d-verify-phase11.md](./06d-verify-phase11.md): fourth independent verification, of the 06c fixes (32cdb2ab)

## 릴리스 뒤

릴리스는 소유자가 정한다. 할 때는 4.34.2 범프에 이 기능을 묶고, `make canary-gates`와 `make canary-commands`를 한 번씩 돌린 뒤 `CANARY_OK=1 make release`를 실행한다.
