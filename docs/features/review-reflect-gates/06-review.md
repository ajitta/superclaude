---
status: draft
revised: 2026-10-21
---

# review-reflect-gates 브랜치 리뷰

## 1차 (2026-10-21, `master...4de7ccb6`, `self-review` 에이전트)

리뷰어에게는 브랜치 diff, 이 계획, 소유자 결정(수용 기준 1–5)을 줬다. 작성자 판단과 커밋 메시지의 평가는 주지 않았다(리뷰어가 git log를 읽을 수는 있다). 리뷰어는 shell이 없어 git·pytest를 돌리지 않았고 파일과 저장된 run을 읽었다.

Critical 없음. 아래는 발견과 처리다. "반영"은 이 브랜치의 다음 커밋에서 고쳤다는 뜻이고, 고친 것이 맞는지는 2차 리뷰가 본다.

| ID | 발견 | 처리 |
|---|---|---|
| I-1 | 채점이 언급만 본다. "no re-review needed", "/sc:reflect is optional" 같은 답이 통과한다 | 반영: `output_not_regex` check 추가, 그런 답 세 개를 채점 테스트에 실패로 고정 |
| I-2 | 재리뷰 정규식이 `test.md` 자신의 표현("due for another review")과 "reviewed again", "has not been reviewed", "unreviewed", "another round", "second-round review"를 놓친다 | 반영: 정규식을 넓히고 아홉 표현을 통과로 고정 |
| I-3 | "plan document" 정의가 셋이다. `test.md`는 `05-plan.md`만, RULES_DOCS는 "the Medium and Large chains"(설치되지 않는 README 용어), README의 bug·refactor 체인은 `/sc:plan`을 거치고도 `/sc:test`에서 끝난다 | 반영: 두 곳 모두 "a feature folder's `05-plan.md` or a `docs/plans/` plan", README 두 체인 끝에 `/sc:reflect` |
| I-4 | `intent.md` `--through`는 리뷰 발견을 한 번 고치고 Proof만 다시 돈다. 새 재리뷰 게이트와 같은 세션에서 충돌한다 | 소유자 결정: 게이트에 예외를 둔다(`--through`는 한 번의 수정 round를 유지하고 Report에서 리뷰받지 않은 수정을 밝힌다). `intent.md`는 그대로 |
| I-5 | `/sc:implement`가 `/sc:test`·`/sc:reflect` 전에 계획을 `complete`로 만든다 | 소유자 결정: 이 브랜치가 만든 것이 아니므로(이전 `/sc:test -> done`도 같았다) 분석 문서에 후속 항목으로 남긴다 |
| I-6 | 재리뷰 종료 조건이 끝나지 않을 수 있고("기계로 확인 가능"만), "grading·canary"는 이 repo 용어이고, 86행과 88행의 범위가 다르다 | 반영: "Critical·Important가 없거나 사용자가 받아들였고, 남은 것은 실행해 확인 가능(tests, linters, evals)", 88행도 "reviewed code or shipped content" |
| I-7 | README `/sc:review --scope branch` 행이 재리뷰 없이 Proof 재실행만 말한다 | 반영: 그 행에 재리뷰를 넣었다 |
| I-8 | Phase 4 뒤 전체 suite 기록이 없는데 상자가 체크됐다 | 사실 확인: 4de7ccb6에서 전체 suite를 돌렸다(3789 passed, 12 skipped, lint·format·typecheck 통과). 리뷰와 동시에 돌아서 리뷰어는 몰랐다. 이 반영 뒤 다시 돌린다 |
| I-9 | CHANGELOG가 행동을 바꾼 Report 단계 줄을 빠뜨리고, RULES_DOCS가 `/sc:test`에서 읽힌다고 잘못 말한다 | 반영: Report 단계를 먼저 쓰고, 틀린 문장은 지웠다 |
| S-1 | drift test가 한 방향만 본다(reflect를 optional로 옮겨도 통과), 재리뷰 게이트와 Report 줄을 고정하지 않는다 | 반영: 두 체인에서 reflect가 optional 밖에 있는지, 재리뷰 게이트 줄, Report 줄의 `/sc:reflect`를 본다. README에서 reflect를 optional로 옮기는 변경을 심어 실패를 확인했다 |
| S-2 | `verifier.md:3`이 "the /sc:test → done gate"라고 쓴다 | 반영: "the /sc:test gate" |
| S-3 | 테스트 실행 check가 표현에 묶여 있다 | 반영: `transcript_regex` `pytest`로 바꿨다 |
| S-4 | 새 untracked 테스트 파일을 못 잡는다 | 반영: `file_absent_glob` `**/*.py`, `exclude_baseline`. 채점 테스트에 고정 |
| S-5 | setup의 `write_text`가 Windows에서 줄 끝을 모두 바꿀 수 있다 | 반영: `read_bytes`/`write_bytes` |
| S-6 | `covers:`가 없어 `reflect.md`가 바뀌어도 프로브가 다시 돌지 않는다 | 반영: `covers: [test, reflect]` |
| S-7 | 다시 채점한 수치를 저장된 `report.md`로는 재현할 수 없다 | 반영: Measurements에 방법(각 run의 `sc-full/logs/*.stream.jsonl`을 `run_eval._parse_stream`으로 읽고 현재 check로 채점)을 적었다 |
| S-8 | 계획 28행 "3 passed"(테스트는 2개), 분석 문서 8행 "후속 작업은 아직 하지 않았다", 결정 기록에 Phase 4가 없다 | 반영 |
| S-9 | `test.md:17`이 게이트를 다시 말한다(로딩 때문에 의도), 두 곳을 묶는 테스트가 없다 | S-1의 Report 줄 확인으로 묶었다 |
