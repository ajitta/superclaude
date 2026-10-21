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
- Phase 9 canary(4223ed1d, Linux, sonnet, effort low, `$TMPDIR/rrg/runs2/cmds`·`extra-2`·`extra-3`): `test-reflect-gate` 세 번 7/7, `test-reflect-gate-complete` 세 번 6/6. `canary-commands`의 나머지 넷도 통과(implement-checkpoint 3/3, implement-proof-fail 5/5, intent-through-branch 14/14, intent-through-ask-headless 15/15). complete 변형의 세 답 모두 두 단계를 들었고, 둘은 "/sc:reflect doesn't replace"를, 하나는 계획 `status: complete`가 그것을 바꾸지 않는다고 썼다.
- Phase 10 재리뷰 정규식(세 규칙)의 recall, 정규식을 보지 않고 쓴 표현으로: headless sonnet(도구 없음)이 시나리오만 보고 "다시 리뷰가 필요하다" 30문장과 "리뷰는 끝났다" 29문장을 썼다(`$TMPDIR/rrg/heldout2.json`, 정규식을 고정한 뒤 한 번만 쟀다). 81776c29 정규식 11/30·false pass 0/29, 4223ed1d(Phase 9) 20/30·1/29, Phase 10 25/30·0/29. 놓친 다섯: "gets a follow-up review"(표지 없음), "someone still has to look at it"(리뷰 낱말 없음), "until … has been independently reviewed", "one more review pass", "한 번 더 검토". 알려진 한계로 둔다. 06b의 표현 36개로는 18/20·1/16이지만, 규칙 3을 넓힐 때 그 목록을 봤으므로 held-out 값이 아니다.
- Phase 10 check(재리뷰 세 규칙, pytest 결과 파일, complete 변형의 README 그대로)로 저장된 Linux run 아홉 개(`trg-1..3`, `runs2/*`)를 다시 채점했다: 모두 통과. 아홉 workspace 모두 `tests/__pycache__/test_export.*-pytest-9.1.1.pyc`가 있다.
- Phase 10 canary(56da83a1, Linux, sonnet, low, `$TMPDIR/rrg/runs3`): `test-reflect-gate` 세 번 7/7, `test-reflect-gate-complete` 세 번 7/7, `canary-commands`의 나머지 넷 통과.
- 재리뷰 check의 recall 범위(06c 발견 2). 정규식을 보지 않고 쓴 집합마다 값이 다르다: heldout2(문장, "리뷰는 끝났다" 쪽에서 "리뷰가 필요 없다/선택이다" 문장은 생성 프롬프트가 뺐다) 25/30·false pass 0/29; heldout3(Phase 11 규칙을 고정한 뒤 만든 새 묶음, 답 끝부분 1–3줄, 목록·두 순서 포함, "리뷰가 필요 없다/선택이다" 문장은 역시 뺐다, `$TMPDIR/rrg/heldout3.json`) 21/30·1/30; 06c 검증자의 자연스러운 묶음 17/32(Phase 10 기준). 알려진 false pass 종류: 같은 절에 표지 낱말이 든 완료 주장("the review again found nothing", "nothing is pending from review"; 06c 표적 묶음 15/16)과 흘려 넘김. 알려진 miss 종류: 번호 목록에서 `/sc:review`만 있는 줄, "what's left: review of …", "have the fix reviewed", 요청 동사 없는 명령형("Review that commit"), 한국어 "아직 …않았". 실제 canary 답 15개는 모두 맞혔다(test.md 문구 "due for another review"를 따르는 답이 많다).
- Phase 11 check로 저장된 Linux run 열다섯 개(`runs/trg-1..3`, `runs2/*`, `runs3/*`)를 다시 채점했다: 모두 통과.
- Phase 12(규칙 2가 "reviewed"를 요청으로 세지 않는다): heldout2 25/30·0/29, heldout3 21/30·1/30, 바뀌지 않았다. 06d의 겨냥한 서술문("committed and then reviewed") 꼴은 실패로 고정했다. 저장된 run 열다섯 개 모두 통과. Phase 11·12는 command 본문을 바꾸지 않아 canary를 다시 돌리지 않았다.
