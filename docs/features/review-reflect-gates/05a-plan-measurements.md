---
status: implementing
revised: 2026-10-21
---

# review·reflect 게이트 측정

[05-plan.md](./05-plan.md)의 `## Measurements`를 옮긴 것이다.

`test-reflect-gate`, sonnet, effort low, check 순서: reflect / 재리뷰 / 코드 그대로 / phase 그대로 / 테스트 실행.

- 바꾸기 전(Phase 1 시점 src, `C:/sc-evals/rrg-before-1..3`, 이 컴퓨터): 세 번 모두 `n Y Y Y Y`(4/5). `/sc:reflect`를 부른 답은 0/3. 세 답 모두 F-1 수정에 round 2 리뷰가 없다고 스스로 짚었다(재리뷰 3/3). 재리뷰 check는 이미 바닥이 높아 규칙 효과를 재지 못한다.
- 바꾼 뒤(Phase 2 src, `C:/sc-evals/rrg-after-1..3`, 이 컴퓨터): 세 번 모두 `n Y Y Y Y`(4/5). `/sc:reflect`는 여전히 0/3이다. 설치된 `test.md` handoff에 `/sc:reflect`가 들어간 것은 확인했다. 세 답 모두 "다음 단계"로 테스트 추가, round 2 리뷰, status 갱신을 들었고 reflect는 들지 않았다. `/sc:test`만 도는 세션에서는 handoff 한 단어로 행동이 바뀌지 않았다. RULES_DOCS 게이트는 이 세션에 로드되지 않으므로(Risks) 이 프로브로는 재지 못한다.
- Phase 4 뒤(`test.md` Report 단계 한 줄, `C:/sc-evals/rrg-body-1..3`, 이 컴퓨터): 세 번 모두 `Y Y Y Y Y`(5/5). `/sc:reflect` 3/3(전 6회 0/6). 세 답 모두 "계획 문서로 진행했으니 `/sc:reflect` 전에는 끝이 아니다"와 F-1 수정의 다음 리뷰 round를 다음 단계로 들었다. 아홉 번 모두 최종 정규식으로 다시 채점한 값이다.
- Phase 5 채점(7 check: reflect / 재리뷰 / 흘려 넘김 없음 / 코드 그대로 / 새 .py 없음 / phase 그대로 / pytest 실행)으로 같은 아홉 run을 다시 채점했다: before·after 여섯 번 `n Y Y Y Y Y Y`(6/7), body 세 번 7/7. 좋은 답이 새 `output_not_regex`에 걸린 경우는 없다. 방법: 각 run의 `sc-full/logs/test-reflect-gate.stream.jsonl`을 `run_eval._parse_stream`으로 읽어 답과 명령을 얻고, workspace `sc-full/test-reflect-gate`에 현재 `tasks.yaml` check를 `run_eval._check_one`으로 돌린다. 저장된 `report.md`·`results.json`은 그 run 때의 채점이다.
- Phase 5 뒤(바뀐 `test.md`·RULES_DOCS 문구, `C:/sc-evals/rrg-fix-1..3`, 이 컴퓨터): 세 번 모두 7/7, 하네스가 run 때 채점한 값이다(`run_eval.py` exit 0).
- Phase 6 채점(2차 리뷰의 흘려 넘김·완료 주장 class, `'*.py'` scope, 실제 pytest 실행)으로 저장된 열두 run을 다시 채점했다: before·after 여섯 번 6/7, body·fix 여섯 번 7/7. 좋은 답의 오탐은 없다.
- Phase 6 뒤(`review.md` 한 줄, 종료 조건, `test.md` 범위, `C:/sc-evals/rrg-fix2-1..3`, 이 컴퓨터): 세 번 모두 7/7, 하네스가 run 때 채점(`run_eval.py` exit 0).
- Phase 7 채점(6 check: reflect / 재리뷰 / `'*.py'` 그대로 / 새 .py 없음 / phase 그대로 / pytest 실행)으로 저장된 열다섯 run을 다시 채점했다: before·after 여섯 번 5/6(reflect만 n), body·fix·fix2 아홉 번 6/6.
- Phase 7 뒤(종료 조건 문구, `review.md`·`test.md` 문구, `C:/sc-evals/rrg-fix3-1..3`, 이 컴퓨터): 세 번 모두 6/6, 하네스가 run 때 채점(`run_eval.py` exit 0).
- Phase 8 뒤(최종 문구: Critical·Important 수정만 재리뷰, `C:/sc-evals/rrg-final-1..3`, 이 컴퓨터): 세 번 모두 6/6, 하네스가 run 때 채점(`run_eval.py` exit 0). 합계: `/sc:reflect`는 Report 단계 한 줄 전 0/6, 뒤 15/15(body·fix·fix2·fix3·final 각 3회).
- Linux 재현(오케스트레이터, 81776c29에 master를 시험 병합한 92590f10, sonnet, effort low, `$TMPDIR/rrg/runs/trg-1..3`): 세 번 모두 6/6, 하네스가 run 때 채점. `/sc:reflect`와 재리뷰 3/3. run 1은 "run `/sc:review` on the F-1 fix, or `/sc:reflect`, which also covers the second gate"라고 써서 reflect를 재리뷰의 대안으로 읽었다. 언급만 보는 채점은 이를 통과시킨다. Phase 9가 `test.md`에 "which /sc:reflect does not replace"를 더한 이유다.
- Phase 9 채점(7 check: reflect / 재리뷰 / `'*.py'` 그대로 / 새 .py 없음 / `06-review.md` 그대로 / phase 그대로 / pytest 실행)으로 위 세 run을 다시 채점했다: 세 번 모두 7/7. 방법은 위와 같다(`run_eval._parse_stream` + `_check_one`).
