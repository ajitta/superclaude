---
status: complete
revised: 2026-10-21
---

# review-reflect-gates 두 번째 독립 검증 (Phase 9)

**판정: 조건부 통과**. shipped 문구는 다섯 곳이 서로 맞고 전체 gate가 녹색이다. 그러나 다시 짠 두 프로브 정규식은 덜 과적합하지 않다. 재리뷰 정규식은 06a가 든 여덟 표현에 대안을 하나씩 맞췄고, 지난 리뷰를 말하는 완료 답을 새로 통과시킨다. pytest 정규식은 실제 실행 꼴을 놓친다. 다시 짠 drift test는 옛 assert 두 개를 잃었다.

## 범위

- 대상: `9436ea36..4223ed1d`(93533db9 Phase 9, 4223ed1d gotcha). 주장 확인에는 `4fd32d90..4223ed1d` 전체를 봤다. 이 worktree의 `verify/review-reflect-gates-2`, Linux.
- 검증자: Claude Opus 5.5, effort high.
- 돌린 것: 전체 suite, `make lint`, `ruff format --check`, `make typecheck`. 두 정규식은 `yaml.safe_load`로 `evals/tasks.yaml`에서 읽어 답 36개와 명령 40개에 돌렸고, 81776c29의 옛 정규식과 나란히 비교했다. 저장된 Linux run `trg-1..3`은 `run_eval._parse_stream` + `_check_one`으로 다시 채점했다. mutation은 내 것 19건과 빌더 목록 표본 7건이다. 스크립트는 `$TMPDIR/v2/`(repo 밖)에 있다.
- canary, `claude`, push는 돌리지 않았다(오케스트레이터 몫). mutation은 커밋된 파일에만 했고, 매번 `git checkout HEAD -- <file>`로 되돌렸다. 마지막 `git diff --stat`은 비어 있다.

## 빌더 주장 1–7

| # | 판정 | 근거 |
|---|---|---|
| 1 | 재현됨 | `implement.md:19` Integrate 끝에 "a fix to a Critical or Important review finding that changes reviewed code or shipped content also goes back to /sc:review for another round before done"가 있다. 이 구절을 지우면(B7) `test_review_reflect_gate_wording`이 red다. 문장 구성은 발견 5를 보라 |
| 2 | 부분 | layout은 맞다. `(?ix)`/`(?mx)` 리터럴 블록이고 한 줄에 한 묶음이다. 제어 문자는 0개다(`grep -c $'\x08'`). 그러나 "표현마다 대안을 덧붙이지 않았다"는 반박된다. 새 대안은 06a F-2의 여덟 표현과 하나씩 짝이 맞는다(발견 1). pytest check는 "명령 조각의 프로그램"을 묻게 됐다. 하지만 launcher 허용 목록이 새로 덧대는 층이 됐고, 실제 실행 꼴 15/23을 놓친다(발견 2) |
| 3 | 재현됨 | yaml 로드 결과 두 번째 변형의 check 6개가 첫 변형의 anchor와 같은 dict이고, setup 5단계와 prompt를 나눠 쓴다. `test_test_reflect_gate_fixture_states`는 `Result: <HEAD~1 short sha> `, `status: complete`, `phase: complete`를 확인한다. M16(feat sha)과 M20(phase 안 바꿈)은 red다. Windows 실행은 하지 않았다. 정적으로 보면 `python -c` 인자에 `"`가 없어 list2cmdline 인용이 안전하다. bytes replace는 CRLF와 상관없다. 덧붙인 LF 한 줄은 줄끝을 섞을 뿐 `git commit -am`이 실패하지 않는다. `Result:` 줄은 `—` 대신 ` - `를 쓰지만 implement.md 형식(sha, 한 줄 출력, footer 아래)으로 읽힌다 |
| 4 | 부분 | 구조는 주장대로 바뀌었다. 빌더 목록 표본 7건(B1–B7)은 모두 red로 재현된다. 그러나 81776c29 테스트에 있던 assert 두 개가 사라졌다(M1, M2). 내 mutation 19건 중 14건이 green이다(발견 3·4) |
| 5 | 재현됨 | `intent.md:20` Run 단계는 branch review 뒤 "fix the Critical and Important ones once, then re-run the Proof"를 하고 `/sc:test`를 부른다. `test.md:17` Report가 그 수정을 "due for another review"로 짚는다. `intent.md`를 바꾸지 않아도 문장은 참이다. 다만 그 말은 중간 출력이고 최종 Report 목록에는 없다. 06a F-8의 판단대로 Suggestion 수준이다 |
| 6 | 재현됨 | `RULES_DOCS.md:86`, `review.md:20`, CHANGELOG가 "accepted the ones it found unfixed or waived the review of their fix"로 같다. 옛 문구로 되돌리면(B2) red다 |
| 7 | 재현됨 | `trg-1..3`을 지금 check로 다시 채점하면 세 번 모두 `YYYYYYY`(7/7)다. 실행 명령은 `… ; python -m pytest`, `(pytest …`·`PYTHONPATH=. pytest -q`, `python -m pytest -q`다. 4223ed1d 자체에서 `uv run pytest`: `3821 passed, 3 skipped, 11 warnings in 123.31s`, exit 0. `make lint` → `All checks passed!`. `ruff format --check src tests` → `223 files already formatted`. `make typecheck` → `Success: no issues found in 54 source files` |

## 발견

### 1 (Important) 재리뷰 정규식은 같은 덧댐을 다른 모양으로 했고, 완료 답을 새로 통과시킨다

- 위치: `evals/tasks.yaml:527-543`(`&rereview_named`), `tests/unit/test_eval_harness.py:1181`(`_RG_REREVIEW`).
- 과적합: 06a F-2의 여덟 표현이 새 대안과 하나씩 짝이 맞는다. "fresh review pass" → `fresh`, "follow-up review" → `follow-up`, "have the fix commit reviewed" → `(have|get)…fix…reviewed`, "run /sc:review on the fix" → `(run|re-?run|call)…/sc:review`, "hasn't been reviewed yet" → `n't…been reviewed`, "has had no review" → `\bno[ ]review\b`, "review round two" → `(2|two)`, "재검토" → 한국어 줄. `_RG_REREVIEW` 19개는 이 대안을 만든 바로 그 목록이다. 그래서 테스트는 정규식이 자기를 만든 표현에 맞는다는 것만 보여 준다. 이 브랜치의 insight(`.claude/insights.jsonl`, "loses to new wordings every review round")가 부정 정규식에 대해 적은 패턴이 긍정 정규식에서 되풀이됐다.
- 재현(`$TMPDIR/v2/rx.py`, tasks.yaml에서 로드, 옛 81776c29와 비교). 06a 목록에 없는 맞는 답 20개 중 새 정규식은 5개, 옛 정규식은 4개를 잡는다. 놓치는 예: "The F-1 fix still needs review before merge.", "The fix was never reviewed.", "The fix wasn't reviewed.", "Nobody has reviewed the fix yet.", "Review the fix commit before merging.", "Another /sc:review round is needed for F-1.", "Send the fix back to review.", "리뷰를 다시 받아야 한다.", "2차 리뷰가 필요하다.". 지난 리뷰를 말하는 완료 답 16개 중 옛 정규식은 1개, 새 정규식은 10개를 통과시킨다. 새로 통과하는 9개는 "No review findings remain, ready to merge.", "No review comments are open; run /sc:reflect.", "No new review findings; /sc:reflect next.", "The review of the fix is complete; run /sc:reflect.", "Review on the fix commit passed in round 1.", "/sc:review approved the fix; run /sc:reflect.", "/sc:review found F-1 and the fix landed; run /sc:reflect.", "The earlier /sc:review covers the fix; /sc:reflect next.", "Called /sc:review earlier; F-1 fixed. /sc:reflect next."다. 원인은 `\bno[ ]review\b`(옛 `no review … after`를 넓혔다), 두 방향의 `/sc:review…fix`, `review (of|on) … fix`다. 둘 다 미래·필요 표지 없이 리뷰와 fix가 함께 나오기만 하면 맞는다. 이것은 소유자가 받아들인 "흘려 넘김" 한계가 아니다. F-2가 계속 실패해야 한다고 한 "Review done" 꼴이다.
- 영향: 재리뷰 쪽은 프로브가 재는 유일한 행동 신호다(05-plan reflect 판정: "재리뷰 부분은 규칙과 drift test로만 확인"). false pass가 늘면 재리뷰 회귀가 green으로 숨는다. M9·M10(대안을 더 넓힘)도 green이다.
- 수정: (a) 넓힌 세 대안에 필요·미래 표지를 요구한다. 예: `\bno[ ]review\b[^.\n]{0,20}\b(after|of|on|for|since|covers?)\b`. `/sc:review`·`review of`는 같은 절에 `\b(need|needs|due|should|must|still|pending|before|next|then)\b`가 있을 때만 맞게 한다. (b) 위 완료 답 9개를 `_RG_FAILS`에 넣는다. (c) 대안을 더 늘리지 않는다. 대신 정규식을 고치기 전에 쓴 보류 표현 묶음(예: 위 20개)으로 recall을 재서 05a에 적고, 놓친 표현은 known limit으로 둔다.

### 2 (Important) pytest check가 실제 실행 꼴을 놓친다. launcher 목록이 새 덧댐 층이다

- 위치: `evals/tasks.yaml:557-567`(`&pytest_ran`).
- 재현: 실제로 테스트를 돌리는 명령 23개 중 15개가 실패로 채점된다(옛 정규식은 0개). 예: `& .venv\Scripts\python.exe -m pytest`, `& "C:\Program Files\Python312\python.exe" -m pytest`(PowerShell 호출 연산자. `run_eval.py:388-391`은 PowerShell 입력도 `bash_inputs`에 넣는다), `coverage run -m pytest`(`/sc:test`는 "coverage analysis" 명령이다), `uvx pytest -q`, `uv run --with pytest-cov pytest -q`, `env PYTHONPATH=. pytest -q`, `time pytest -q`, `bash -c 'pytest -q'`, `python -B -m pytest`, `py -3 -m pytest`, `python3 -X utf8 -m pytest`, `pdm run pytest`, `hatch run pytest`, `nohup pytest -q`, `"$PY" -m pytest -q`. 테스트를 돌리지 않는데 통과하는 것도 남았다. `pytest --co -q`, `pytest --help`, `pytest --fixtures`, `echo "(pytest)"`. 정밀도는 나아졌다(`which pytest`, `type pytest`, `Get-Command pytest`, `rg pytest …`, `python -c "import pytest"`가 이제 실패한다). 대신 recall을 잃었다. 저장된 세 run은 단순한 꼴이라 7/7이 이 차이를 드러내지 않는다.
- 판단: `(uv|poetry|pipenv) run`, `env`, `timeout`, `python -m`은 열거한 허용 목록이다. 실행 꼴이 새로 나올 때마다 한 줄씩 붙는다. `(` 구분자도 run trg-2의 `(pytest …`에서 왔다. 단위 테스트는 `(`, `||`, `poetry|pipenv`, `env`를 지켜 주지 않는다(M11–M14 green).
- 수정(하나를 고른다): (a) 방향을 뒤집는다. 조각의 첫 낱말이 이름만 대는 명령(`pip`, `uv pip`, `which`, `type`, `where`, `Get-Command`, `cat`, `grep`, `rg`, `ls`, `echo`, `git`)이면 빼고, 나머지 조각에서 `\bpy\.?test\b` 토큰을 찾는다. 단일 `&`와 따옴표도 구분자로 본다. 실행하지 않는 옵션은 `--version|--collect-only|--co|--help|-h|--fixtures|--markers`로 넓힌다. 이름만 대는 명령 목록은 실행 꼴 목록보다 작고 덜 변한다. (b) 결과를 본다. pytest는 테스트 모듈을 모을 때 `tests/__pycache__/test_export.cpython-313-pytest-9.1.1.pyc`를 쓰고 `--version`은 아무것도 쓰지 않는다(fixture 사본에서 확인했다). `file_exists_glob: tests/__pycache__/*-pytest-*.pyc`는 launcher 철자와 상관없다. 한계도 있다. `--collect-only`도 이 파일을 쓰고, `PYTHONDONTWRITEBYTECODE`는 막는다. `build_workspace`의 copytree는 로컬 fixture의 `__pycache__`를 복사하므로 ignore가 필요하다. 어느 쪽이든 위 23+17개를 단위 테스트 표에 넣는다.

### 3 (Suggestion) drift test 재구성에서 옛 assert 두 개가 빠졌고, 새 범위 구절이 고정되지 않는다

- 위치: `tests/unit/test_docs_ssot_guards.py:525-571`(`_GATE_PHRASES`).
- 빠진 것(81776c29의 `test_docs_ssot_guards.py`): `:556` `assert plan_doc in gates.group(1)`. 계획 문서 정의가 두 곳에서 같다는 확인이다. 지금은 gates 쪽에 "`docs/plans/` plan) goes to /sc:reflect" 조각만 있다. M2(gates에서 "a feature folder's `05-plan.md` or " 삭제)가 green이다. `:573` `assert "A fix to a Critical or Important finding" in process`. M1(`review.md` 범위를 "any finding"으로)이 green이다. 0f6a3bf8의 범위 축소를 review.md에서 지키는 assert가 없어졌다.
- 고정되지 않은 이 브랜치의 구절: `test.md` Report의 "after the last review round"(M3)와 "that changed reviewed code or shipped content"(M4), gates `/sc:reflect -> done`의 "(a fix that changes reviewed code or shipped content goes back to review, above)"(M5), `implement.md`의 "before done"(M6), `review.md`의 "with no claim that they are fixed"(M7), README reflect 행의 "reviewed code or"(M8). 모두 green이다.
- 수정: `_GATE_PHRASES`에 다음을 더한다. `("gates", _PLAN_DOC)`, `("review Process", "A fix to a Critical or Important finding that changes reviewed code or shipped content")`, `("test Report", "that changed reviewed code or shipped content after the last review round")`, `("gates", "(a fix that changes reviewed code or shipped content goes back to review, above)")`, `("implement Integrate", "for another round before done")`, `("review Process", "with no claim that they are fixed")`, `("README reflect row", "a fix that changes reviewed code or shipped content")`. `_FIX_SCOPE`도 "that changes reviewed code or shipped content"까지 넓히면 네 곳을 한 번에 묶는다(test.md는 "changed"라 따로 둔다).

### 4 (Suggestion) 채점 테스트가 false pass 쪽과 구분자·launcher를 지키지 않는다

- 위치: `tests/unit/test_eval_harness.py:1210`(`_RG_FAILS`), `:1222`(`_RG_TEST_RUNS`).
- 재현: M9(`\bno[ ]review\b` → `\bno\b[^.\n]{0,30}\breview`), M10(`/sc:review…fix` 창을 400자로), M11(`(` 구분자 삭제), M12(`||` 삭제), M13(`poetry|pipenv` 삭제), M14(`env` 삭제) 모두 green이다. `_RG_FAILS`의 완료 답 다섯은 모두 "review done/reviewed in round 1/found F-1 and it is fixed" 꼴이다. 지난 리뷰를 다르게 말하는 답은 없다.
- 수정: 발견 1의 완료 답 9개를 `_RG_FAILS`에, `(cd ws && pytest -q)`, `false || pytest -q`, `poetry run pytest`, `env PYTHONPATH=. pytest`(허용한다면)를 `_RG_TEST_RUNS`에 넣는다. 덤: `:1312`, `:1341`의 `read_text()`에 `encoding="utf-8"`을 준다. fixture의 `—`, `→`는 cp949로 decode되지 않는다. 기존 `test_command_structure.py:74`도 같은 꼴로 Windows에서 통과했으니 red 가능성은 낮다.

### 5 (Suggestion) `implement.md` 새 구절이 같은 단계의 `complete` 규칙과 한 문장에 묶였다

- 위치: `src/superclaude/commands/implement.md:19`.
- 문제: 같은 단계에서 녹색 Proof는 docs 커밋으로 `status: complete`를 정하고, README `phase: complete`는 "never moves back"이다. 새 구절은 그 뒤에 "before done"을 요구한다. 그래서 파일은 complete라고 말하는데 done은 아직 아닌 상태가 shipped 문구로 생긴다. 바로 `test-reflect-gate-complete`가 재현하는 상태다. 2차 round가 Critical을 찾아도 계획을 `implementing`으로 되돌리는 경로가 없다. 되돌리는 것은 "a red re-run"뿐이다. 또 새 구절이 Proof 문장과 "; a red re-run …" 사이에 끼어, "re-run"이 Proof의 재실행이라는 것이 덜 분명해졌다.
- 수정: 구절을 Proof 문장 뒤의 독립 문장으로 뺀다. 예: "A fix to a Critical or Important review finding that changes reviewed code or shipped content goes back to /sc:review for another round before done, even when its Proof is green." 그리고 "complete가 재리뷰보다 먼저"를 분석 문서 D의 후속 항목에 적는다(README는 D를 이 기능 밖으로 둔다).

### 6 (Suggestion) 두 번째 변형에서 아직 잴 수 있는 것

- 위치: `evals/tasks.yaml:569-595`.
- phase check를 뺀 것은 맞다. 다만 `implement.md:19`가 README `phase:`는 "never moves back"이라고 하므로, `/sc:test`가 `complete`를 `implementing`으로 되돌리는 것은 shipped 규칙 위반이다. `/sc:test`는 계획 문서를 고칠 단계도 아니다. 주석("reopening the plan or the phase is not failed")은 이 규칙과 어긋난다.
- 수정: 두 번째 변형에 `{type: cmd_ok, tag: scope, cmd: [git, diff, --quiet, baseline, --, docs/features/csv-export/README.md]}`를 더하거나, 열어 둔 이유를 주석에 implement.md 규칙과 함께 적는다. `Result:` 줄이 그대로인지도 같은 방식으로 잴 수 있다.

### 7 (Suggestion) 규칙 대신 리뷰 이력을 서술하는 주석

- `tests/unit/test_docs_ssot_guards.py:575-577` docstring "weakening any of these went unnoticed in the independent verification's mutation checks, 06a F-4". `test_eval_harness.py`의 "(06-review round 3, owner decision)", "the ones the independent verification listed (06a F-2)", "# A second review without /sc:reflect (06a F-5).". `tasks.yaml:519-520` "A negation regex lost to new wordings every review round … (06-review.md round 3), so it was dropped."
- 판단: 이유를 남긴 것이라 해롭지는 않다. 그러나 소유자 지시("리뷰 history를 서술하는 주석")에 해당한다. 규칙을 한 줄로 적고 feature 폴더 링크 하나만 남긴다. 예: "Mention checks only (known limit, docs/features/review-reflect-gates)".
- 정당한 중복: 다섯 곳의 범위 문장(RULES_DOCS, test.md, review.md, implement.md, README)과 `--through` 예외가 `review.md`·RULES_DOCS 두 곳에 있는 것은 로딩 제약 때문이다. `--through` 세션은 `review.md`를 Skill로 로드하므로 거기에도 예외가 있어야 한다. 단어 차이는 test.md의 시점("changed … after the last review round")과, reflect 줄에 C/I 제한이 없는 것(reflect gap은 리뷰 발견이 아니다)뿐이고 둘 다 의도다.

### 8 (Suggestion) 06a 반영 표의 빈칸

- F-4 행은 D13·D14를 고정하지 않았다고 적었지만, 06a가 green으로 든 D18(`verifier.md` "the /sc:test gate")은 다루지 않는다. 지금도 고정되지 않는다(`grep -rn "the /sc:test gate" tests/` 결과 없음).
- F-6 행은 정밀도 향상만 적고 recall 손실(발견 2)은 적지 않았다.
- F-11의 뒷부분("독립 검증 기록이 예외인지 적는다")은 반영되지 않았다. gotcha `plan-docs-on-branch`는 여전히 "never onto master"인데, master에 `docs/features/` 커밋 1407a138(`docs: independent verification of v4.34.1..4fd32d90`)이 있다.
- 나머지는 맞다. `05-plan.md` 24,144 bytes(목표 25,000 이하), 05a 4,286 bytes, 15/15 합계(body·fix·fix2·fix3·final 각 3), `_RG_REREVIEW` 19개, mutation 목록 21건.

## Mutation 표

내 mutation(M)은 `test_docs_ssot_guards.py`, `test_eval_harness.py`, `test_version_consistency.py`를 돌렸다. 빌더 표본(B)은 앞의 두 파일을 돌렸다.

| ID | 바꾼 것 | 결과 |
|---|---|---|
| M1 | `review.md` "A fix to a Critical or Important finding" → "A fix to any finding" | green |
| M2 | gates 계획 문서 정의에서 "a feature folder's `05-plan.md` or " 삭제 | green |
| M3 | `test.md` Report "after the last review round" 삭제 | green |
| M4 | `test.md` Report "that changed reviewed code or shipped content" 삭제 | green |
| M5 | gates `/sc:reflect -> done`의 재리뷰 괄호 삭제 | green |
| M6 | `implement.md` "before done" 삭제 | green |
| M7 | `review.md` "with no claim that they are fixed" 삭제 | green |
| M8 | README reflect 행 "reviewed code or" 삭제 | green |
| M9 | 재리뷰 `\bno[ ]review\b` → `\bno\b[^.\n]{0,30}\breview` | green |
| M10 | 재리뷰 `/sc:review…fix` 창 60 → 400(마침표 허용) | green |
| M11 | pytest 구분자 `(` 삭제 | green |
| M12 | pytest 구분자 `\|\|` 삭제 | green |
| M13 | pytest launcher `poetry\|pipenv` 삭제 | green |
| M14 | pytest launcher `env` 삭제 | green |
| M15 | 두 번째 변형에서 `*review_untouched` 삭제 | **red** |
| M16 | 두 번째 변형 `Result:` sha를 `HEAD~1`(feat)로 | **red** |
| M17 | `test.md` handoff에서 `/sc:reflect`를 둘째로 | **red** |
| M19 | gates `--through` "keeps its single fix round" 삭제 | **red** |
| M20 | 두 번째 변형이 README phase를 바꾸지 않음 | **red** |
| B1–B7 | 빌더 목록 표본: "which /sc:reflect does not replace" 삭제, F-9 이전 문구, pytest 위치 `.*`, D8, D10, D1, F-1 구절 삭제 | 모두 **red** |

M18(README review 행의 "a code change after the `Result:` sha re-runs the Proof" 삭제)도 green이다. 이 구절은 base 4fd32d90부터 있었으므로 아래 "이 브랜치 밖"에 둔다.

## 이 브랜치 밖

- README `/sc:review --scope branch` 행의 Proof 재실행 구절은 base부터 어떤 테스트도 고정하지 않는다(M18).
- 06a가 남긴 두 항목은 그대로다. `_parse_stream`이 subagent의 tool_use를 구분하는지(`run_eval.py:342-404`, 미확인)와 `exclude_baseline`이 setup baseline이 아니라 HEAD를 뺀다는 것이다.
- 분석 문서 D(`complete`가 `/sc:test`·`/sc:reflect`·재리뷰보다 먼저 온다)는 발견 5로 더 분명해졌다. D를 정할 때 implement.md의 상태 전이와 두 번째 변형의 check를 함께 다룬다.

## 반영 (2026-10-21, claude-box, Phase 10)

| # | 처리 |
|---|---|
| 1 | 반영: 재리뷰 check를 표현 목록에서 한 절(. ; , 줄 끝 사이)에 대한 세 규칙으로 바꿨다. (1) 필요·미완·반복 표지(need, due, should, still, not yet, n't, never, again, another, second, round 2, back to, before merg, 필요, 다시, 2차)가 붙은 리뷰, (2) 리뷰 앞의 요청 동사나 "next", (3) fix·commit·F-1이 있는 절의 부정된 리뷰(no, without, not, never, nobody). 넓은 세 대안(`no review`, `/sc:review…fix`, `review of/on…fix`)은 없어졌다. 규칙을 고정한 뒤 정규식을 보지 않고 쓴 표현(headless sonnet, 도구 없음, 30+29)으로 한 번 쟀다: 81776c29 11/30·0/29, 4223ed1d 20/30·1/29, 지금 25/30·0/29. 이 보고서의 표현 36개로는 18/20·1/16이다(규칙 3을 넓힐 때 봤으므로 held-out이 아니다). 놓친 표현은 [05a](./05a-plan-measurements.md)에 알려진 한계로 적었다. 위 완료 답 9개와 쉼표·"next" 경우 둘을 `_RG_FAILS`에 넣었다 |
| 2 | 반영 (b): 명령 모양 대신 결과를 본다. `file_exists_glob: tests/__pycache__/*-pytest-*.pyc`(pytest assertion-rewrite 캐시). launcher 목록과 pip 예외가 없어졌다. `run_eval.build_workspace`와 단위 테스트의 fixture 복사는 `__pycache__`·`.pytest_cache`를 뺀다(`FIXTURE_IGNORE`). 단위 테스트는 실제 pytest를 돌려 본다: 실행 전 실패, `--version` 뒤 실패, `-q` 뒤 통과. 저장된 Linux run 아홉 개 모두 그 파일이 있고 통과한다. 남은 한계: collect-only 호출, `PYTHONDONTWRITEBYTECODE` |
| 3 | 반영: `_GATE_PHRASES`가 조각 대신 각 곳의 규칙 문장 전체를 고정한다(계획 문서 정의가 gates에, `review.md` 범위, `test.md` 시점, `/sc:reflect -> done` 괄호, "with no claim that they are fixed", README reflect 행). M1–M8 모두 red |
| 4 | 반영: 1의 완료 답, 2의 실제 실행 경우. 구분자·launcher 테스트는 2로 필요 없어졌다. `read_text`에 `encoding="utf-8"` |
| 5 | 반영: `implement.md` 구절을 Proof 문장 뒤 독립 문장으로("…for another round before done, even when its Proof is green"). `complete`가 재리뷰보다 먼저 오는 것은 분석 문서 D에 적었다 |
| 6 | 반영: complete 변형에 `git diff --quiet baseline -- docs/features/csv-export/README.md`. 주석은 implement.md의 "never moves back"을 이유로 든다 |
| 7 | 반영: 리뷰 이력을 말하던 주석(`tasks.yaml`, 두 테스트 파일)을 규칙 한 줄과 feature 폴더 링크로 바꿨다 |
| 8 | 반영: D18은 drift test가 shipped 내용 어디에도 폐기된 `/sc:test -> done`(또는 `→`) 이름이 없는지 본다. F-6 recall 손실은 2로 해소. F-11 뒷부분: gotcha `plan-docs-on-branch`는 소유자 결정(2026-10-21)을 출처로 들고, master의 1407a138은 그 결정 전 커밋이다 |
| M18, 이 브랜치 밖 | 손대지 않았다 |

Mutation(반영 뒤, 메모리의 원본으로 되돌림, `git diff --stat`이 mutation 전과 같다): M1–M8, D1, D6, D8, D10, D18, F-9 이전 문구, "even when its Proof is green" 삭제, 재리뷰 규칙 1에 "next" 추가, 규칙 2 삭제, 규칙 3 삭제, 규칙 3의 fix 조건 삭제, 쉼표 절 분리 삭제, `/sc:reflect` check 삭제, pytest glob을 `tests/**`로, `FIXTURE_IGNORE`에서 `__pycache__` 삭제, complete 변형의 README check 삭제, `06-review.md` check 삭제. 25건 모두 red다.
