---
status: complete
revised: 2026-10-22
---

# review-reflect-gates 다섯 번째 독립 검증 (Phase 12)

**판정: 조건부 통과**. 06d 발견 1(Important)은 고쳐졌고 Critical·Important 발견은 없다. 다만 H3의 수정은 06d가 든 예문 그 자체를 여전히 통과시키고, 대신 수동태 요청("get the fix reviewed")을 놓치게 했다(발견 1, Suggestion).

## 범위

- 대상: `git diff 393efa53 1a550a3b`. worktree `verify/review-reflect-gates-5`, Linux, CPython 3.13, pytest 9.1.1. 검증자는 Claude Opus 5.5다.
- 06d 끝의 반영 표는 믿지 않고 다시 쟀다. 정규식은 `yaml.safe_load`로 읽었다. 스크립트는 `$TMPDIR/v5/`에 있다.
- mutation은 커밋된 파일에만 했고 매번 `git checkout HEAD --`로 되돌렸다. 끝난 뒤 `git diff --stat`은 비어 있다.

## Gate

- `uv run pytest -q -p no:randomly`(timeout 1500 s): `3819 passed, 3 skipped, 11 warnings`, exit 0.
- `make lint`: `All checks passed!`. `uv run ruff format --check src tests evals`: `228 files already formatted`. `make typecheck`: `Success: no issues found in 54 source files`.
- CI(`gh run list`, 읽기만): Tests가 1a550a3b에서 success다.

## H1–H4

| H | 판정 | 근거 |
|---|---|---|
| H1 | 충족 | `test_eval_harness.py`가 `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=$TMPDIR/v5pc`, `PYTHONOPTIMIZE=1`, 셋을 함께 켠 셸에서 모두 `89 passed`다. `_clean_env`(`test_eval_harness.py:1295`)가 `_pytest`와 import 호출에 쓰인다 |
| H2 | 충족 | `run_eval.py:316`이 `BYTECODE_ENV` 셋을 세션 env에서 지운다. `test_probe_session_keeps_bytecode_on`(`:688`)은 이름을 직접 적어, pop 삭제·`PYTHONOPTIMIZE` 삭제·`PYTHONPYCACHEPREFIX` 삭제 모두 red다 |
| H3 | 부분 | 측정값은 재현된다: heldout2 25/30·0/29, heldout3 21/30·1/30, 저장된 run 15개 모두 7/7. 그러나 06d 발견 4의 예문 "The fix was committed and then reviewed by the same reviewer."는 여전히 요청으로 센다(발견 1) |
| H4 | 부분 | canary 서술은 맞다: 09a817b8..1a550a3b에서 `src/`는 바뀌지 않았고, 05-plan·05a는 Phase 11·12에 canary를 주장하지 않는다. 주석의 "53-83%"는 17/32·21/30·25/30과 맞다. 그러나 05a:30의 "06d의 겨냥한 서술문 꼴은 실패로 고정했다"는 발견 1 때문에 사실이 아니다 |

## 발견

### 1 (Suggestion) `review(?!ed)`가 06d의 예문을 막지 못하고, 수동태 요청을 놓치게 한다

- 위치: `evals/tasks.yaml:547`, `:531`, `tests/unit/test_eval_harness.py:1275`, `05a-plan-measurements.md:30`.
- 재현(1a550a3b의 정규식):
  - 06d 예문 "The fix was committed and then reviewed by the same reviewer."는 통과한다. `then` 뒤 25자 안의 "reviewer"가 `review(?!ed)`에 맞는다. 테스트가 고정한 문장은 06d 예문을 줄인 "…then reviewed; /sc:reflect next."다. `_RG_FAILS`의 그 줄을 06d 예문 + "; /sc:reflect next."로 바꾸면 red(2 failed)다. 06d의 나머지 두 예문("then the review signed off", "then review found nothing new")도 그대로 통과한다.
  - 32cdb2ab에서 맞히던 요청이 이제 빠진다: "Next, get the fix reviewed.", "Get the F-1 commit reviewed, then run /sc:reflect.", "Send the F-1 fix to be reviewed by someone else.", "Ask for the fix commit to be reviewed.", "Request that 3c1f2ab be reviewed." 등 내 표적 13개 중 7개. `(?!ed)`가 규칙 2 동사 전부에 걸려서다. heldout 두 집합의 "reviewed" 요청 둘("get 4f2a9c1 reviewed again", "get it reviewed before merging")은 규칙 1 표지로 살아남아 측정값이 바뀌지 않았다. 05a의 miss 종류에는 이 종류가 없다.
- 영향: 자연스러운 집합과 저장된 실제 답에서는 값이 그대로다. 그래서 Suggestion이다. 다만 반영 표 3과 05a:30의 "실패로 고정했다"는 과장이다.
- 수정: `then`만 따로 떼어 `(?!ed|er)`를 붙이고 나머지 동사에서는 뺀다.
  ```
  | (?= [^.;,\n]*? (?: \b(run|re-?run|request|ask[ ]for|get|send|schedule|next)\b
                     [^.;,\n]{0,25} review
                   | \bthen\b [^.;,\n]{0,25} review (?!ed|er) ) )
  ```
  임시 편집으로 heldout2 25/30·0/29, heldout3 21/30·1/30이 그대로이고, 06d 예문은 실패, 위 수동태 요청 셋은 통과, `_RG_FAILS`에 06d 예문을 더한 `test_eval_harness.py`가 `89 passed`임을 확인했다(되돌림). 06d 예문을 `_RG_FAILS`에 넣고, 05a:30을 고친다.

### 2 (Suggestion) `PYTEST_ADDOPTS=--assert=plain`인 셸에서는 같은 일곱 테스트가 여전히 red다

- 위치: `tests/unit/test_eval_harness.py:1295`, `evals/run_eval.py:177`.
- 재현: `PYTEST_ADDOPTS=--assert=plain uv run pytest tests/unit/test_eval_harness.py -k reflect_gate`는 `7 failed`다. 06d 발견 1과 같은 종류이고 프로브 세션도 이 변수를 물려받는다. 06d 발견 2가 이미 짚었지만 Phase 12는 다루지 않았다. tasks.yaml:566의 "a run with --assert=plain fails"는 세션이 고른 경우만 말한다.
- 영향: 이 변수를 상시 켜 두는 셸은 드물다.
- 수정: `_clean_env`와 `run_task`에서 `PYTEST_ADDOPTS`도 지우거나, 한계로 주석과 05a에 적는다.

### 3 (Suggestion) H1의 수정을 지키는 테스트가 기본 셸에는 없다

- 위치: `tests/unit/test_eval_harness.py:1295-1299`.
- 재현: `_clean_env`가 `os.environ`을 그대로 돌려주게 바꾸면 기본 셸에서 `89 passed`(green), `PYTHONDONTWRITEBYTECODE=1`에서만 `7 failed`다. CI는 그 변수를 켜지 않으므로 되돌림을 잡지 못한다.
- 수정: 한 테스트에서 `monkeypatch.setenv`로 세 변수를 켠 뒤 `_pytest`를 불러 캐시가 생기는지 본다.

### 4 (Suggestion) 반영 표의 "표지 낱말 일곱"은 실제로 아홉이다

- 위치: `06d-verify-phase11.md:138`.
- 재현: 규칙 1의 표지 23개를 하나씩 지우고 `-k grades_answers`를 돌렸다. red는 아홉이다: `need`, `should`, `still`, `unreviewed`, `again`, `round 2`, `re-review`, `before merg`, `다시`. 나머지 열넷은 green이다.
- 수정: 숫자를 고치거나 숫자 없이 "06d가 든 표지와 몇 개"로 적는다.

## 이번 diff 밖에서 본 것

- `PYTHONOPTIMIZE=2`에서는 `test_credential_copies_do_not_outlive_the_run`이 실패한다(docstring이 `None`). 이 테스트는 c46936c4에서 들어와 master에 이미 있다. 이 브랜치의 회귀가 아니다.

## Mutation

| # | mutation | 결과 |
|---|---|---|
| M1 | `run_task`의 `env.pop` 삭제 | red (1 failed) |
| M2 | `BYTECODE_ENV`에서 `PYTHONOPTIMIZE` 삭제 | red (1 failed) |
| M2b | `BYTECODE_ENV`에서 `PYTHONPYCACHEPREFIX` 삭제 | red (1 failed) |
| M3 | 규칙 2의 `(?!ed)` 삭제 | red (2 failed) |
| M4 | `_clean_env` 필터 삭제, 기본 셸 / `PYTHONDONTWRITEBYTECODE=1` | **green** / red (7 failed), 발견 3 |
| M5 | `_RG_FAILS` 줄을 06d 예문으로(`/sc:reflect` 없음) | green: reflect check가 먼저 실패해 무의미하다 |
| M5b | 같은 예문 + "; /sc:reflect next." | red (2 failed), 발견 1 |
| M6 | 발견 1의 수정안 + 06d 예문 고정 | green (89 passed) |
| 표지 | 규칙 1 표지 23개 하나씩 삭제 | red 9, green 14, 발견 4 |

## 확인하지 못한 것

- `claude`를 띄울 수 없어, 지운 변수 셋이 실제 프로브 세션의 Bash 도구에서도 빠져 있는지는 보지 않았다.
- 발견 1의 수정안은 임시 편집으로만 확인했다.
