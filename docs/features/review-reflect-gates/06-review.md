---
status: complete
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

## 2차 (2026-10-21, `90301a42`, `self-review` 에이전트, 새 세션)

리뷰어에게는 1차 발견을 결함과 확인 방법으로만 줬고, 고쳤다는 주장과 이 표의 처리 칸은 증거로 쓰지 말라고 했다. 소유자 결정(I-4 예외, I-5 후속)은 결정으로만 전했다. 리뷰어는 shell이 없어 pytest를 돌리지 않았다.

1차 판정: I-2, I-3, I-7, I-9, S-2–S-8 고쳐짐. I-4·I-5는 결정대로. I-1, I-6 일부. I-8은 Phase 5 뒤 suite 출력이 계획에 인용되지 않음.

| ID | 발견 | 처리 |
|---|---|---|
| I-1·N-3 | 다른 표현의 흘려 넘김("no need to review it again", "re-review isn't needed", "No second round is needed", "optionally run /sc:reflect")과 두 단계를 언급하면서 "done and ready to merge"라 하는 답이 통과한다. 고친 쪽이 리뷰어가 인용한 문자열만 고정한다 | 반영: `output_not_regex`를 표현 class 단위로 넓혔다(no X needed, no need to/for X, X isn't needed, doesn't need X, optional(ly) /sc:reflect, it's ready to merge). class마다 인용 문자열과 인용되지 않은 변형을 실패로, "not ready to merge"·"before it's ready to merge" 같은 부정·조건 표현을 통과로 고정 |
| I-6·N-2·N-17 | 종료 조건 끝의 "and what is left can be checked by running something"이 다시 끝없는 round를 만든다. "it"이 단수 | 반영: "the user has accepted the ones left; leftover Suggestions are reported, not reviewed again" |
| N-1 | 재리뷰 규칙이 수정이 일어나는 `/sc:review`·`/sc:implement` 세션에 로드되지 않는다 | 소유자 결정: `review.md` Process 단계에 한 줄. drift test가 그 줄을 고정 |
| I-8 | Phase 5 뒤 전체 suite 출력이 계획에 없다 | 반영: 90301a42에서 돈 suite(3789 passed, 12 skipped, lint·format·typecheck 통과)를 계획에 적고, 마지막 커밋 뒤 다시 돌려 `Result:`에 적는다 |
| N-4 | 게이트가 `--through` Report에 리뷰받지 않은 수정을 적는다고 하지만 `intent.md` Report 목록에 그 항목이 없다 | 받아들임: `intent.md`를 그대로 두는 것이 소유자 결정이다. 게이트는 `/sc:intent`에서 로드되므로 그 세션에서는 읽힌다 |
| N-5 | README `/sc:review --scope branch` 행이 "reviewed code"만, "Critical findings fixed"만 말하고, `/sc:reflect` 행이 "—" | 반영 |
| N-6 | `test.md`가 "any fix"로 게이트보다 넓다 | 반영: "a fix to a review finding" |
| N-7 | drift test가 계획 문서 정의가 같은지, 재리뷰 줄의 수용 기준 구절을 고정하지 않는다 | 반영: 두 곳의 계획 문서 정의가 같은 문자열인지, `review.md` Process 줄의 "earlier findings as acceptance criteria"를 본다 |
| N-8 | reflect만 흘려 넘기는 답이 따로 고정되지 않았다 | 반영: "It needs a re-review; /sc:reflect is optional" 등 세 개 |
| N-9 | "No review was required for the test-only change, but…"처럼 맞는 답이 실패할 수 있다 | 받아들임: 저장된 열두 run에서 오탐은 없다. 표현에 기대는 채점의 한계로 남긴다 |
| N-10 | `exclude_baseline`은 HEAD 기준이라 shop·tests 밖에 커밋된 새 .py(루트 conftest.py)가 빠진다 | 반영: scope check를 `git diff --quiet baseline -- '*.py'`로. 루트 conftest.py 커밋을 실패로 고정 |
| N-11 | `pytest`가 들어간 아무 명령(`pip show pytest`)이 테스트 실행으로 셈된다 | 반영: `-m pytest` 또는 명령 시작·구분자 뒤의 `pytest`만. `pip show pytest`를 실패로 고정 |
| N-12 | 단위 테스트가 하네스의 workspace 준비(.gitignore, `.claude` 설치)를 거치지 않는다 | 받아들임: 리뷰어가 읽은 대로 설치 파일은 setup의 `git add -A` 전에 들어가 baseline에 포함된다. 하네스 채점 7/7과 맞다 |
| N-13 | README "End of branch" 체인에 reflect가 없다 | 받아들임: 계획 문서와 무관한 일반 체인이다. 게이트가 계획 문서로 진행한 작업을 다룬다 |
| N-14 | "shipped content"가 이 repo 말이다 | 받아들임: 사용자 프로젝트에서도 "배포되는 내용"으로 읽힌다 |
| N-15 | CHANGELOG가 프로브의 실패 조건을 덜 적는다 | 반영 |
| N-16 | fixture 리뷰가 "Major"를 쓴다 | 반영: "Important" |
| N-18 | 분석 문서 절 순서가 B, D, C | 반영 |

## 3차 (2026-10-21, `68112487`, `self-review` 에이전트, 새 세션)

1·2차 발견을 G1–G12 수용 기준(결함과 확인 방법)으로, 소유자 결정을 D1–D6으로 줬다. 리뷰어는 shell이 없어 정규식을 손으로 따라갔다.

판정: G2, G3, G5, G6, G10, G11 충족. G4·G7·G8·G9는 충족하되 아래 Suggestion이 남았다. G1·G12 일부.

| ID | 발견 | 처리 |
|---|---|---|
| N1 | 완료 주장 정규식이 맞는 조건부 답("If both come back clean, it's ready to merge", "csv-export is done only after /sc:reflect")을 실패시킨다 | 소유자 결정: 흘려 넘김·완료 주장 check(`output_not_regex`)를 뺐다. 프로브는 언급 check만 하고, 흘려 넘기는 답이 통과하는 것은 알려진 한계로 `tasks.yaml` 주석과 CHANGELOG에 적었다. 두 조건부 답을 통과로 고정 |
| N2 | 흘려 넘김 class가 여전히 샌다("doesn't need to be re-reviewed", "No need for /sc:reflect"), 한 대안은 영영 맞지 않는다 | N1과 같은 결정으로 check가 없어졌다 |
| N3 | 종료 조건의 "open"이 모호하다. 작성자는 고친 순간 닫혔다고 읽어 재리뷰를 건너뛸 수 있다 | 반영: "a review round finds no Critical or Important finding, or the user has accepted the ones it found"(RULES_DOCS와 `review.md` 같은 문장) |
| N4 | `review.md`에 `--through` 예외가 없다 | 반영: `review.md` 끝에 괄호로 |
| N5 | CHANGELOG가 `review.md`에 없는 "leftover Suggestions…"를 `review.md`의 말로 적는다 | 반영: `review.md`에 그 구절을 넣었다 |
| N6 | 체크된 suite 상자 안에 할 일이 있고 68112487 run 인용이 없다 | 반영: 68112487 run(3789 passed, 12 skipped)을 적고 남은 일은 따로 뺐다 |
| N7 | drift test가 `test.md` 재리뷰 구절, 두 곳의 종료 조건, bug·refactor 체인을 고정하지 않는다 | 반영 |
| N8 | `/sc:reflect -> done`의 재리뷰 괄호가 `/sc:reflect` 세션에 로드되지 않는다 | 소유자 결정: 받아들임. reflect 뒤 수정은 `/sc:review`를 거치고, `review.md`가 규칙을 직접 싣는다. 계획 Risks에 적었다 |
| N9 | 테스트 실행 정규식이 `PYTHONPATH=. pytest`, `timeout 60 pytest`를 놓치고 `pytest --version`, `--collect-only`를 센다 | 반영: pytest가 든 명령 줄 중 `pip`, `--version`, `--collect-only`가 없는 것. 여섯 경우를 고정 |
| N10 | 굽은 따옴표로 흘려 넘김이 샌다 | N1 결정으로 해당 없음 |
| N11 | "No need to edit code; it needs a re-review"가 실패할 수 있다. `test.md`가 게이트보다 넓다 | 앞은 N1 결정으로 해당 없음. 뒤는 반영: "that changed reviewed code or shipped content" |
| N12 | README `/sc:reflect` 행에 재리뷰 괄호가 없다 | 반영 |
| (범위 밖) | `review.md` handoff가 4개(규칙은 2-3개) | 이 브랜치 전부터다. 손대지 않았다 |

## 4차 (2026-10-21, `69ad177c`, `self-review` 에이전트, 새 세션)

3차 반영이 맞춰야 할 R1–R9와 소유자 결정 D1–D7을 줬다. 리뷰어는 shell이 없어 정규식을 손으로 따라갔다. R1–R9 충족, D1–D7 일치. 같은 커밋에서 전체 suite 3789 passed, 12 skipped.

| ID | 발견 | 처리 |
|---|---|---|
| N-1 (Important) | 재리뷰 조건이 심각도와 무관하게 "a fix to a review finding"이라, Suggestion만 고쳐도 새 round가 생긴다 | 소유자 결정: Critical·Important에 대한 수정만. RULES_DOCS, `review.md`, `test.md`, README, CHANGELOG에 같은 범위로. drift test가 세 곳을 고정 |
| S-1 | README `/sc:reflect` 행이 "reviewed code"만 | 반영: "reviewed code or shipped content" |
| S-2 | 테스트 실행 check 주석이 정규식보다 넓게 말한다(`cat pytest.ini`도 셈) | 반영: 주석이 실제 규칙을 말한다. 무엇이든 테스트 실행이 없을 때를 막는 guard다 |
| S-3 | 여러 줄 입력 경우가 고정되지 않았다 | 반영: 두 경우 고정 |
| S-4 | scope 주석이 "adds no file"이라 하지만 .py와 README phase만 본다 | 반영: 주석이 보는 것과 보지 않는 것을 말한다 |
| S-5 | drift test가 `review.md`의 `--through` 예외와 README `/sc:reflect` 행을 고정하지 않고, docstring이 좁다 | 반영 |
| N-6 | `--through` Report 목록에 리뷰받지 않은 수정 항목이 없다 | 2차 N-4와 같다. 받아들임(소유자 결정, `intent.md` 그대로) |
| N-7, N-8, N-9 | Spec gate의 "Critical finding open"이 비슷하게 읽힘(이 브랜치 전부터), 계획 Measurements의 지난 check 이름(기록), `review.md` Process 단계가 두 일을 함(규칙 위반 없음) | 받아들임 |

리뷰 round 종료(소유자 결정, 2026-10-21): N-1과 Suggestion을 반영한 뒤 남은 것은 테스트, 프로브, drift test로 확인한다. 소유자가 남은 문구를 받아들이고 5차는 돌리지 않는다.
