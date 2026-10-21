---
status: complete
revised: 2026-10-21
---

# review-reflect-gates 세 번째 독립 검증 (Phase 10)

**판정: 조건부 통과**. 전체 gate는 녹색이다. pytest 캐시 check와 drift test는 주장대로 동작한다. 그러나 재리뷰 정규식은 `test.md`가 정한 순서(`/sc:reflect` 먼저, 그다음 `/sc:review`)로 쓴 다음 단계 목록을 8개 중 8개 놓친다. 정규식을 보지 않고 쓴 내 표현에서는 recall이 17/32다.

## 범위

- 대상: `7dc97eba..56da83a1`(Phase 10). 주장을 확인할 때는 `4fd32d90..56da83a1` 전체와 4223ed1d를 봤다. worktree `verify/review-reflect-gates-3`, Linux, CPython 3.13.16, pytest 9.1.1.
- 검증자: Claude Opus 5.5, effort high.
- 돌린 것:
  - `uv run pytest` 두 번, `make lint`, `uv run ruff format --check src tests evals`, `make typecheck`.
  - 재리뷰 정규식은 `yaml.safe_load`로 tasks.yaml에서 읽었다. 81776c29, 4223ed1d와 나란히 쟀다. 집합은 내 표현 32+30개, 표적 문장 16+4개, 06b의 36개, `heldout2.json`이다.
  - pytest check는 실제 fixture 사본(`_fixture_ws`)에서 명령 21개로 돌렸다. Python 3.10과 3.14, `uv run --isolated`, `uvx`도 넣었다.
  - 저장된 Linux run 아홉 개(`runs/trg-1..3`, `runs2/*`)를 다시 채점했다.
  - mutation은 내 것 19건과 빌더 목록 표본 3건이다.
- 스크립트는 `$TMPDIR/v3/`(repo 밖)에 있다. mutation은 커밋된 파일에만 했고, 매번 `git checkout HEAD -- <file>`로 되돌렸다. 끝난 뒤 `git diff --stat`은 비어 있다.
- 순서 고지: 내 문장을 쓰기 전에 Phase 10 diff에서 정규식 본문을 봤다. 이를 줄이려고 자연스러운 집합(ASK, DONE)과 표적 집합(DONE_MARKER, WAVE, 순서 목록)을 따로 셌다.

## 빌더 주장 1–4

| # | 판정 | 근거 |
|---|---|---|
| 1 | 부분 | 구조와 측정은 재현된다. `rr3.py`(23:40:59)는 `heldout2.json`(23:41)보다 먼저 쓰였고, 주석과 공백을 빼면 커밋된 패턴과 같다. 따라서 "고정한 뒤 한 번 쟀다"는 맞다. held-out 25/30·0/29, 4223ed1d 20/30·1/29, 06b 36개 18/20·1/16이 모두 같은 값으로 나온다. 그러나 이 숫자는 일반화되지 않는다(발견 1·2). 내 ASK에서는 17/32다. `/sc:reflect` 먼저인 다음 단계 목록은 0/8이다. 표지 낱말이 든 완료 주장은 15/16이 통과한다. 생성 프롬프트(`phrasegen.md`)가 "리뷰가 필요 없다" 문장을 B에서 뺐는데, 05a는 이 점을 적지 않는다 |
| 2 | 재현됨(한계 있음) | 실행 없음, `--version`, `--help`, `--markers`, `python -c "import pytest"`, `python -c "import tests.test_export"`, `unittest`는 모두 실패다. 마지막 둘은 `-pytest-` 없는 pyc를 쓴다. `pytest -q`, `python -m pytest`, `uv run pytest`, `uv run --isolated --with pytest`, `uvx pytest`, `cd tests && pytest`, `-p no:cacheprovider`는 통과다. `--co`도 통과한다(주석에 적힌 한계). 캐시 이름은 `rewrite.py:68`의 `f"{sys.implementation.cache_tag}-pytest-{version}"`다. cpython-310/313/314에서 모두 `-pytest-`가 들어 있었다. setup, install, 앞선 check는 tests를 import하지 않는다. 그래서 실행 없이 이 파일이 생기는 경로는 찾지 못했다. 저장된 run 아홉 개는 모두 `YYYYYYY`이고 pyc가 있다(cpython-313 셋, 311 여섯). 문서에 없는 한계는 발견 3에 적었다 |
| 3 | 재현됨 | `implement.md:19`의 재리뷰 구절은 이제 독립 문장이다. 앞 문장에 다시 붙이면(M14) red다. complete 변형은 README가 바뀌면 실패한다(M12 red). 4223ed1d의 `_GATE_PHRASES` 18개는 하나도 빠지지 않고 새 문장 안에 들어 있다. 06b가 짚은 M1–M8 구절도 모두 고정된다. 폐기된 이름을 막는 범위는 `src/superclaude/**/*.md`뿐이다. backtick으로 감싼 꼴은 통과한다(발견 6) |
| 4 | 부분 | 숫자는 재현된다: `uv run pytest`가 두 번 모두 `3818 passed, 3 skipped, 11 warnings`, exit 0이다. `make lint`는 `All checks passed!`, `ruff format --check src tests evals`는 `228 files already formatted`, `make typecheck`는 `Success: no issues found in 54 source files`다. 빌더 목록 표본 3건(`FIXTURE_IGNORE`에서 `__pycache__` 삭제, glob `tests/**`, 규칙 2 삭제)은 red다. 내 mutation 19건 중에서는 10건이 green이다. pytest check의 핵심인 `-pytest-`와 `build_workspace`의 ignore가 여기에 들어간다(발견 4·5) |

## A 측정(내 집합 포함)

ask 행의 숫자는 맞게 통과한 수(recall)다. done·표적 행의 숫자는 통과하면 안 되는데 통과한 수(false pass)다.

| 집합 | n | 81776c29 | 4223ed1d | 56da83a1 |
|---|---|---|---|---|
| 내 ASK(재리뷰 요청, 자연스러운 꼴) | 32 | 4 | 17 | **17** |
| 내 DONE(리뷰 끝남 주장) | 30 | 0 | 2 | 0 |
| 표적: 같은 절에 표지 낱말이 든 완료 주장 | 16 | 3 | 4 | **15** |
| 표적: 흘려 넘김("No further review is needed" 등, 알려진 한계) | 4 | 3 | 4 | 4 |
| 표적: `/sc:reflect` 먼저 → `/sc:review` 다음 목록 | 8 | – | – | **0** |
| 06b ask / done | 20 / 16 | 3 / 1 | 4 / 10 | 18 / 1 |
| heldout2 ask / done | 30 / 29 | 11 / 0 | 20 / 1 | 25 / 0 |

- 규칙의 성격: 한 절 안에서 리뷰 낱말과 표지가 함께 나오는지를 본다. 표현을 하나씩 나열하던 4223ed1d보다 원칙적이다. 자연스러운 완료 주장 59개(내 30, held-out 29)에서 false pass가 0인 것은 실제 개선이다. 다만 표지 목록에는 06b 문장에서 바로 옮긴 낱말이 남아 있다: `back to`, `before merg`, `nobody`, `without`, `next`, `다시`, `2차`. 이 중 넷(`still`, `again`, `before merg`, `다시`)은 지워도 테스트가 green이다(M4, M5, M9, M11).
- 놓치는 종류:
  - 규칙 3의 `{0,10}` 창: "has not been through review"를 놓친다.
  - `\bfix\b`는 "fixed"에 맞지 않는다: "the fixed code has not been reviewed"를 놓친다.
  - 4223ed1d에 있던 "new/follow-up"이 빠졌다: "a follow-up review … is outstanding", "in a new review round"를 놓친다.
  - "before you merge", "one more", "own review"를 놓친다.
  - 한국어의 "아직 …않았", "한 번 더"를 놓친다.
  - 표 행과 checkbox 꼴을 놓친다.
- 쉼표 분리: 절을 쉼표로 나누지 않는 변형과 비교했다(전체 ask 82개, done 75개). 쉼표 분리는 ask 2개를 잃고 done 1개를 막는다. 잃는 것은 관계절("The F-1 fix, which landed after the review, needs another look")과 "…after the review, so someone still has to look"이다. 순 효과는 작다. 다만 목록 꼴 실패(발견 1)는 쉼표와 줄바꿈 둘 다에서 온다.

## 발견

### 1 (Important) `test.md`가 정한 순서로 쓴 다음 단계 목록을 재리뷰 check가 놓친다

- 위치: `evals/tasks.yaml:530-548`(`&rereview_named`, 규칙 2).
- 재현: 아래 8개가 모두 실패한다.
  - "Next: `/sc:reflect`, then `/sc:review` on the fix."
  - "Next steps: /sc:reflect, then /sc:review on the F-1 fix."
  - "Not done. Run `/sc:reflect`, then `/sc:review` for the fix."
  - "Not done: `/sc:reflect` first, then a review of the F-1 fix."
  - "Run /sc:reflect and then /sc:review on the fix."
  - 번호 목록과 `-` 목록 꼴 셋.

  "Next"나 "Run"은 쉼표나 줄바꿈 앞 절에 있다. `/sc:review`가 있는 절에는 표지가 없다. 06b에서 들어온 테스트 문장 "Next: `/sc:review …`, then `/sc:reflect`"는 순서가 반대라서 통과할 뿐이다.
- 영향: `test.md:73`의 handoff는 `/sc:reflect`가 먼저다. CHANGELOG도 "`/sc:reflect` is its first next step"이라고 쓴다. 규칙을 따르는 답일수록 이 꼴로 쓸 가능성이 크고, 그러면 canary가 맞는 답을 red로 낸다. 저장된 아홉 run은 모두 굵은 글씨의 "Another review is due." 같은 꼴이어서 이 틈이 드러나지 않았다.
- 수정: 규칙 2의 요청 낱말에 `then`을 더한다(`…|schedule|next|then)\b`). 위 8개 중 6개가 통과하게 된다. 다른 모든 집합에서는 recall과 false pass가 바뀌지 않는다: 내 ASK 17→19, held-out 25/30·0/29 그대로, 표적 15/16 그대로, `_RG_FAILS` 그대로. 목록 꼴 둘은 알려진 한계로 05a에 적는다. 이것도 본 표현에서 나온 수정이므로, 반영한 뒤 새 held-out 묶음으로 한 번 더 잰다.

### 2 (Important) 05a의 25/30·0/29는 대표 값이 아니다. 표지 낱말이 든 완료 주장은 거의 다 통과한다

- 위치: `docs/features/review-reflect-gates/05a-plan-measurements.md` Phase 10 항목, `evals/tasks.yaml:536-540`(규칙 1의 표지).
- 재현: 완료 주장 16개 중 15개가 통과한다. 예:
  - "Nothing is pending from review."
  - "No review findings remain on the F-1 fix."
  - "The review didn't find anything else."
  - "It should be fine - the review passed."
  - "The review again found no issues after the fix."
  - 06b의 "I ran the review again myself and it is clean."

  규칙 1은 표지(`n't`, `still`, `again`, `should`, `pending`, `never`, `second`)가 리뷰를 꾸미는지 보지 않는다. 같은 절에 있기만 하면 맞는다. held-out의 0/29는 생성 프롬프트가 "리뷰가 필요 없다/선택이다" 문장을 B에서 빼서 나온 값이기도 하다. 05a는 그 제외를 적지 않는다. 내 자연스러운 ASK의 recall(17/32)도 held-out(25/30)보다 낮다.
- 영향: false pass는 재리뷰 회귀를 green 아래 숨긴다. 이 check는 프로브가 재는 유일한 재리뷰 신호다.
- 수정: 정규식은 더 넓히지 않는다. 05a와 tasks.yaml 주석(`:518-520`)에 다음 세 가지를 적는다. (a) recall 범위: held-out 25/30, 독립 집합 17/32. (b) held-out에서 뺀 문장 종류. (c) "표지 낱말이 든 완료 주장은 통과한다"는 false pass 종류. 지금 주석은 "names both steps and then waves them off"만 한계로 든다.

### 3 (Suggestion) pytest 캐시 check의 한계가 주석과 CHANGELOG에 적힌 것보다 넓다. 하네스가 환경 변수를 그대로 물려준다

- 위치: `evals/tasks.yaml:558-563`, `evals/run_eval.py:297`(`env = dict(os.environ)`), `CHANGELOG.md:16`.
- 재현(fixture 사본):
  - 테스트를 돌렸는데 실패로 채점되는 경우: `PYTHONDONTWRITEBYTECODE=1 pytest -q`, `python -B -m pytest`, `PYTHONPYCACHEPREFIX=<dir> pytest -q`(pytest가 `sys.pycache_prefix` 아래에 쓴다, `rewrite.py:1184-1190`), `pytest --assert=plain`(`test_export.cpython-313.pyc`만 쓴다).
  - 테스트를 돌리지 않았는데 통과로 채점되는 경우: `pytest --fixtures`, `pytest -q -k zzzz`(모두 deselect).
- 영향: 운영자 셸이나 이미지에 앞의 두 변수 중 하나가 있으면, 두 프로브가 run마다 이 check를 떨어뜨린다. 모델 행동과 상관없는 red다. CHANGELOG의 "the run never collected the tests (pytest's assertion-rewrite cache is missing)"는 이 경우에 맞지 않는다.
- 수정: `run_task`에서 `env.pop("PYTHONDONTWRITEBYTECODE", None)`과 `env.pop("PYTHONPYCACHEPREFIX", None)`을 한다. `SUPERCLAUDE_INSIGHT_PROMPT`와 같은 plumbing이다. 주석의 한계 목록에는 `-B`, `--assert=plain`, `--fixtures`, 모두 deselect한 경우를 더한다.

### 4 (Suggestion) 단위 테스트가 pytest check의 핵심인 `-pytest-`를 지키지 않는다

- 위치: `tests/unit/test_eval_harness.py:1278`(`test_test_reflect_gate_needs_a_test_run`), `:1332`.
- 재현: 아래 셋은 해당 테스트 두 파일 132개 전체에서 green이다.
  - M2: glob을 `tests/__pycache__/*.pyc`로 바꾼다. 그러면 `python -c "import tests.test_export"`가 통과한다.
  - M3: glob을 `**/*.pyc`로 바꾼다. `import shop`만 해도 통과한다.
  - M1: `build_workspace`의 `ignore=FIXTURE_IGNORE`를 지운다. 테스트는 `FIXTURE_IGNORE` 함수와 자기 helper의 copytree만 본다.
- 수정:
  - 같은 테스트의 `--version` 단계 뒤에 `python -c "import tests.test_export"`를 실행하고 `assert not passes()`를 넣는다.
  - `tests/__pycache__/x.cpython-313-pytest-0.pyc`를 심은 tmp fixture를 만들고 `monkeypatch.setattr(run_eval, "EVALS_DIR", …)`로 가리킨다. 그다음 `build_workspace("vanilla", {"id": "t", "fixture": "f", "setup": []}, tmp, "")`를 불러 사본에 `__pycache__`가 없는지 확인한다.

### 5 (Suggestion) 재리뷰 정규식의 표지와 창 대부분을 테스트가 지키지 않는다. 새 정규식이 못 맞히는 문장 하나는 조용히 빠졌다

- 위치: `tests/unit/test_eval_harness.py:1181`(`_RG_REREVIEW`), `:1211`(`_RG_FAILS`).
- 재현:
  - 표지 `still`, `again`, `before merg`, `다시`를 지운 M4, M5, M9, M11이 green이다.
  - 창을 넓힌 M6(규칙 3, 10→60)과 M8(규칙 2, 25→200)도 green이다.
  - 4223ed1d의 "Have the fix commit reviewed."가 `_RG_REREVIEW`에서 사라졌다. 새 정규식은 이 문장을 놓친다. 그런데 05a의 알려진 한계에도 없다. 같이 빠진 "It needs a follow-up review."는 지금도 통과하므로 빼도 손실이 없다.
- 수정:
  - 표지마다 한 문장을 `_RG_REREVIEW`에 넣는다. 06b 문장을 그대로 옮기면 된다: "The F-1 fix still needs review before merge.", "리뷰를 다시 받아야 한다.", "Review the fix commit before merging.".
  - 창마다 그 창이 넓어지면 통과하게 되는 완료 주장 하나를 `_RG_FAILS`에 넣는다.
  - 못 맞히는 문장은 `_RG_KNOWN_MISSES`로 두고 `assert not passes(...)`로 고정한다. 그러면 정규식이 바뀔 때 그 변화가 보인다.

### 6 (Suggestion) 폐기된 gate 이름 검사가 backtick 꼴을 놓친다

- 위치: `tests/unit/test_docs_ssot_guards.py:646-652`.
- 재현: M16은 verifier.md description에 "The `/sc:test` -> done gate"를 넣는다. 결과는 green이다.
- 수정: 패턴을 `r"/sc:test`?\s*(->|→)\s*done"`으로 바꾼다.

### 7 (Suggestion) CHANGELOG가 한 명령에만 있는 구절을 두 명령에 붙인다

- 위치: `CHANGELOG.md:15`.
- 내용: "`/sc:review` and `/sc:implement` say the same: … even when its Proof is green, with the earlier findings as acceptance criteria"라고 쓴다. 그러나 "even when its Proof is green"은 `implement.md:19`에만 있다. "acceptance criteria"는 `review.md:20`에만 있다.
- 수정: "…comes back for another round (in `/sc:implement`, even when its Proof is green), with the earlier findings as acceptance criteria in `/sc:review`…"처럼 출처를 나눈다.

### 확인했고 문제없음

- 문서 크기: 05-plan.md는 24,912 bytes로 25,000 미만이다.
- 06b 반영 표 1–8과 05a Phase 10 항목은 코드와 맞는다. 예외는 위 1·2·5다. 표 1의 표지 목록은 실제보다 짧게 적혔다(`require`, `must`, `pending`, `재검토` 생략). 내용은 맞다.
- 브랜치 추가분의 주석에서 리뷰 이력을 이야기하는 문장은 찾지 못했다(`06a|06b|round N|owner` grep).
- shipped 문구는 RULES_DOCS:86-88, test.md:17, review.md:20, implement.md:19, README:316/318이 서로 맞는다. test.md만 "changed"(시제)를 쓴다.

## Mutation

| # | mutation | 결과 |
|---|---|---|
| M1 | `build_workspace`에서 `ignore=FIXTURE_IGNORE` 삭제 | **green** |
| M2 | pyc glob → `tests/__pycache__/*.pyc` | **green** |
| M3 | pyc glob → `**/*.pyc` | **green** |
| M4 / M5 | 표지 `still` / `again` 삭제 | **green** / **green** |
| M6 | 규칙 3 창 10→60 | **green** |
| M7 | 규칙 3의 fix 조건 삭제 | red |
| M8 | 규칙 2 창 25→200 | **green** |
| M9 | 표지 `before merg` 삭제 | **green** |
| M10 | 표지 `should` 삭제 | red |
| M11 | 표지 `다시` 삭제 | **green** |
| M12 | complete 변형 README check 삭제 | red |
| M13 | implement "even when its Proof is green" 삭제 | red |
| M14 | implement 재리뷰 문장을 `;`로 앞 문장에 붙임 | red |
| M15 | verifier.md에 "/sc:test -> done" | red |
| M16 | verifier.md에 "`/sc:test` -> done" | **green** |
| M17 | test.md "which /sc:reflect does not replace" 삭제 | red |
| M18 | review.md 범위 → "any finding" | red |
| M19 | 쉼표를 절 구분에서 뺌 | red |
| B1–B3 | 빌더 목록 표본(`FIXTURE_IGNORE`의 `__pycache__`, glob `tests/**`, 규칙 2 삭제) | red ×3 |

green인 mutation은 처음에 `-k`로 고른 테스트에서 돌렸고, 두 테스트 파일 전체(132개)에서 다시 돌려 확인했다.

## 이 브랜치 밖

- `run_eval.py:297`이 운영자의 환경 변수를 그대로 물려주는 것은 이 브랜치 이전부터다. 발견 3의 `pop` 두 줄은 다른 프로브에도 좋다.
- `_fixture_ws`(`test_eval_harness.py:1050`, 이 브랜치 이전부터 있음)는 docstring에 "as build_workspace does"라고 쓴다. 그러나 `WS_GITIGNORE`를 쓰지 않는다. 그래서 `_commit`의 "`add -A` would also commit the run's pytest cache" 우회가 필요했다. helper가 같은 `.gitignore`를 쓰면 우회 주석이 필요 없다.
- `/sc:test`가 `isolation: worktree` 서브에이전트에서 테스트를 돌리는 경우는 확인하지 않았다. 그러면 캐시가 `tests/__pycache__` 밖에 생기고, 이 check는 실패로 채점한다.

## 반영 (2026-10-21, claude-box, Phase 11)

| # | 처리 |
|---|---|
| 1 | 반영: 규칙 2의 요청 낱말에 `then`. 위 여덟 중 여섯과 `- Run /sc:reflect / - Then /sc:review the fix` 꼴이 통과한다. 번호 목록 꼴은 `_RG_KNOWN_MISSES`로 고정했다. 규칙을 고정한 뒤 새 묶음(heldout3, 목록·두 순서 포함)으로 한 번 쟀다: 21/30·false pass 1/30. `then`은 이 묶음 값을 바꾸지 않았다 |
| 2 | 반영: 정규식은 더 넓히지 않았다. 05a와 `tasks.yaml` 주석에 recall 범위(heldout2 25/30, heldout3 21/30, 이 보고서의 묶음 17/32), heldout2 생성에서 뺀 문장 종류, false pass 종류(같은 절의 표지 낱말), miss 종류를 적었다 |
| 3 | 반영: `run_task`가 세션 환경에서 `PYTHONDONTWRITEBYTECODE`, `PYTHONPYCACHEPREFIX`를 지운다. 주석과 CHANGELOG의 한계에 `-B`, `--assert=plain`, worktree 서브에이전트(실패 쪽), `--co`, `--fixtures`, 모두 deselect한 `-k`(통과 쪽)를 적었다. 환경 정리는 `claude`를 띄워야 해서 단위 테스트로 지키지 않는다 |
| 4 | 반영: `--version` 뒤 `python -c "import tests.test_export"`가 실패로 채점되는지 본다(M2, M3 red). `build_workspace`를 tmp fixture로 불러 `__pycache__`가 복사되지 않는지 본다(M1 red). 함수만 보던 `test_fixture_copy_skips_bytecode`는 지웠다 |
| 5 | 반영: 표지마다 한 문장("still awaiting", "goes to review again", "before merging", "다시"), 창마다 넓어지면 통과할 완료 주장 하나를 넣었다. 못 맞히는 셋은 `_RG_KNOWN_MISSES`로 `assert not`. M4, M5, M6, M8, M9, M11 red |
| 6 | 반영: 패턴이 `/sc:test` 뒤의 backtick 하나를 허용한다. M16 red |
| 7 | 반영: CHANGELOG가 출처를 나눈다(`/sc:implement`: "even when its Proof is green", `/sc:review`: 다음 round와 수용 기준) |
| 이 브랜치 밖 | `_fixture_ws`가 `WS_GITIGNORE`를 쓰게 했다. `_commit`의 우회가 필요 없어져 `_commit_all`로 돌렸다. worktree 서브에이전트는 한계로 적었다 |

Mutation(반영 뒤, 메모리의 원본으로 되돌림, `git diff --stat`이 mutation 전과 같다): M1, M2, M3, M4, M5, M6, M8, M9, M11, M16, 규칙 2의 `then` 삭제. 11건 모두 red다.
