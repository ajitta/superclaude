---
status: complete
revised: 2026-10-21
---

# review-reflect-gates 네 번째 독립 검증 (Phase 11)

**판정: 조건부 통과**. G1–G7의 결함은 고쳐졌고 전체 gate는 녹색이다. 그러나 G3와 같은 결함이 단위 테스트에 남았다. 개발자 셸에 `PYTHONDONTWRITEBYTECODE`, `PYTHONPYCACHEPREFIX`, `PYTHONOPTIMIZE` 중 하나가 있으면 `uv run pytest`가 7개 실패로 red가 된다(발견 1, Important).

## 범위

- 대상: `git diff 09a817b8 32cdb2ab`. worktree `verify/review-reflect-gates-4`, Linux, CPython 3.13, pytest 9.1.1. 검증자는 Claude Opus 5.5다.
- 정규식은 `yaml.safe_load`로 읽었다. 56da83a1과 나란히 쟀다. 측정 집합은 heldout2, heldout3, 내 집합 15+15개, 표적 `then` 문장 5개, 저장된 canary 답 15개다.
- 스크립트는 `$TMPDIR/v4/`에 있다. mutation은 커밋된 파일에만 했고, 매번 `git checkout HEAD --`로 되돌렸다. 끝난 뒤 `git diff --stat`은 비어 있다.
- 내 문장은 diff에서 정규식을 본 뒤에 썼다. 그래서 측정값은 held-out이 아니다.

## Gate

- `uv run pytest -q -p no:randomly`: `3818 passed, 3 skipped, 11 warnings`, exit 0.
- `make lint`: `All checks passed!`.
- `uv run ruff format --check src tests evals`: `228 files already formatted`.
- `make typecheck`: `Success: no issues found in 54 source files`.
- CI(`gh run list`, 읽기만): Tests가 32cdb2ab에서 success다.

## G1–G7

| G | 판정 | 근거 |
|---|---|---|
| G1 | 부분 | 06c의 reflect 먼저 8개 중 6개가 통과한다. 내 reflect 먼저 답에서는 산문 12개 중 9개가 통과한다. 목록과 화살표 꼴은 3개 중 1개만 통과하고, 그 하나도 줄에 표지가 있어서다(발견 3). 완료 주장 false pass는 내 15개 중 0개다. 다만 `then`이 서술문 false pass를 새로 만든다(발견 4) |
| G2 | 부분 | 숫자는 재현된다: heldout2 25/30·0/29, heldout3 21/30·1/30, 저장된 답 15/15. 05a에 집합 이름, 놓치는 종류, false pass 종류가 있다. 그러나 heldout3 생성 프롬프트(`phrasegen3.md`)도 "unnecessary or optional" 문장을 B에서 뺐는데 05a는 이를 heldout2에만 적는다. tasks.yaml:521의 "about half"는 05a 값(17/32–25/30)과 맞지 않는다(발견 5) |
| G3 | 충족(프로브) | `run_eval.py:311`이 세션 env에서 두 변수를 지운다. 그러나 같은 env에서 단위 테스트가 red다(발견 1). `PYTHONOPTIMIZE`와 지운 동작을 지키는 테스트가 없는 문제는 발견 2다 |
| G4 | 충족 | glob에서 `-pytest-`를 지운 A1·A2, `build_workspace` ignore를 지운 A3, `FIXTURE_IGNORE`에서 `__pycache__`를 지운 A4가 모두 red다 |
| G5 | 충족(종류 단위) | 표지 세 종류(필요·아직·반복)마다 red가 되는 표지가 있다. 두 창은 양쪽 방향 모두 red다(25→200·25→0, 10→60·10→0). 알려진 miss 고정도 red다(A12). 개별 대안 27개는 하나씩 지우면 green이다(발견 6) |
| G6 | 충족 | `` `/sc:test` -> done ``와 `` `/sc:test`→done ``를 심으면 red다(B1, B3). 가드 정규식을 되돌리면 green이다(B2) |
| G7 | 충족 | "even when its Proof is green"은 `implement.md:19`에, round·수용 기준·종료 조건·Suggestions는 `review.md:20`에 있다. CHANGELOG도 그 명령에 붙인다 |

## 새로 들어온 것 점검

- `_fixture_ws`의 `WS_GITIGNORE`: 이 helper를 쓰는 fixture(implement-proof-fail, plan-draft-spec-gate, intent-through 둘, reflect-gate 둘)에는 자체 `.gitignore`가 없다. `.gitignore`는 baseline 커밋에 들어가므로 diff check가 바뀌지 않는다. `.gitignore`나 pyc를 읽는 check도 없다. 이제 vanilla `build_workspace`와 같다. 이 쓰기를 지우면(A6) red다. 그래서 `_commit_all`로 돌린 것도 지켜진다.
- `run_task`의 env 정리: 지우는 env는 `claude` 자식 프로세스에만 넘어간다. 다른 프로브 workspace에는 bytecode가 생긴다. 그러나 `WS_GITIGNORE`가 `__pycache__/`와 `*.pyc`를 무시하고, `_git_changed`는 `git status`를 쓴다. glob check(`**/*.py`, `*.md` 등)도 pyc에 맞지 않는다. 부작용은 없다.

## 발견

### 1 (Important) 단위 테스트가 개발자 셸의 bytecode 환경 변수에 따라 red가 된다

- 위치: `tests/unit/test_eval_harness.py:1269`(`_pytest`). 영향받는 테스트는 `test_test_reflect_gate_*` 일곱 개다.
- 재현: `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/unit/test_eval_harness.py`는 `7 failed, 81 passed`다. `PYTHONOPTIMIZE=1`과 `PYTHONPYCACHEPREFIX=<dir>`도 각각 7 failed다. Phase 11은 프로브 세션의 env를 지웠다. 그러나 같은 check를 시험하는 테스트의 pytest 자식 프로세스는 여전히 env를 물려받는다. 그래서 캐시가 생기지 않거나(`.pyo`, prefix 디렉터리) `passes()`가 거짓이 된다.
- 영향: AGENTS.md의 통합 gate(전체 suite exit 0)가 그 환경에서 늘 실패한다. 규칙상 red는 회귀로 읽히므로 없는 회귀를 찾게 된다.
- 수정: `run_eval`에 튜플(`PYTHONDONTWRITEBYTECODE`, `PYTHONPYCACHEPREFIX`, `PYTHONOPTIMIZE`)을 두고 `run_task`와 `_pytest`가 같이 쓴다. `_pytest`에 그 키를 뺀 `env=`를 넘기면 세 env 모두에서 88 passed임을 임시로 확인했다(되돌림).

### 2 (Suggestion) `PYTHONOPTIMIZE`가 빠졌고, env 정리를 지키는 테스트가 없다

- 위치: `evals/run_eval.py:311`, `evals/tasks.yaml:561-567`.
- 재현:
  - `PYTHONOPTIMIZE=1`(또는 `python -O`)이면 pytest가 `test_export.cpython-313-pytest-9.1.1.pyo`를 쓴다. 그러면 check가 실패한다. 이 경우는 주석의 한계 목록에 없다. `PYTEST_ADDOPTS=--assert=plain`도 실패다(`--assert=plain`의 env 꼴).
  - pop 두 줄을 지운 A5가 green이다. 06c 반영 표는 "claude를 띄워야 해서 단위 테스트로 지키지 않는다"고 쓴다. 그러나 `test_eval_harness.py:672-716`은 이미 `fake_run`으로 `run_task`의 env를 검사한다(`SUPERCLAUDE_INSIGHT_PROMPT`, `ENABLE_CLAUDEAI_MCP_SERVERS`).
- 수정: 발견 1의 튜플에 `PYTHONOPTIMIZE`를 넣는다. 같은 `fake_run` 꼴로 `monkeypatch.setenv` 뒤 키가 없는지 확인한다. 반영 표의 이유 문장도 고친다.

### 3 (Suggestion) 목록 꼴 다음 단계는 표지가 없으면 놓친다. 정규식을 넓히지 말고 한계로 적는다

- 위치: `evals/tasks.yaml:526-548`, `test_eval_harness.py:1218`.
- 재현: 다음 셋을 놓친다.
  - "- `/sc:reflect`\n- `/sc:review` on commit 3c1f2ab (the F-1 fix)"
  - "Steps: `/sc:reflect` → `/sc:review` on the F-1 fix → merge."
  - "Do `/sc:reflect`, followed by `/sc:review` of the fix commit."

  두 독립 집합의 목록 꼴은 7개 중 2개만 통과한다.
- 넓힐 때의 대가(측정):
  - "같은 절에 `/sc:review`와 fix" 규칙을 더하면 내 ask가 10→14/15가 된다. 그러나 `_RG_FAILS` 셋이 통과한다("/sc:review approved the fix; …").
  - 목록 항목 규칙을 더하면 heldout3가 21→23/30이 되지만 false pass도 1→2/30이 되고, 표적 완료 목록 5개 중 3개가 통과한다.
  - 저장된 실제 답 15개는 모두 산문 문장으로 맞혔다.
- 수정: 정규식은 그대로 둔다. tasks.yaml 주석에 "a next-steps list item or arrow chain naming /sc:review with no marker word"를 miss 종류로 적는다(05a에는 번호 목록만 있다).

### 4 (Suggestion) `then`이 서술문 완료 주장을 통과시킨다. 규칙 설명은 그대로다

- 위치: `evals/tasks.yaml:546`, `:530`.
- 재현: 다음 다섯이 모두 통과한다. 56da83a1에서는 0/5였다.
  - "The fix was committed and then reviewed by the same reviewer."
  - "F-1 was fixed and then the review signed off."
  - "Tests passed, then review found nothing new."

  자연스러운 집합(heldout2·3, 내 done 15)에서는 false pass가 바뀌지 않았다.
- 수정: 주석의 규칙 2 설명("a request verb or \"next\"")에 `then`을 넣는다. 이 종류를 `_RG_KNOWN_FALSE_PASSES`로 두고 `assert passes(...)`로 고정해 `_RG_KNOWN_MISSES`와 짝을 맞춘다. 05a의 false pass 종류에도 적는다.

### 5 (Suggestion) 측정 문서의 범위 서술이 덜 정확하다

- 위치: `05a-plan-measurements.md:28`, `evals/tasks.yaml:521`, `05-plan.md:179`.
- 내용:
  - heldout3도 "unnecessary or optional" 문장을 뺐다(`phrasegen3.md`). 05a는 이를 적지 않는다.
  - 주석의 "about half"는 heldout3를 재기 전(`r11a.py` 00:12:18, heldout3 00:12:57)에 쓰였다. 세 집합의 범위 "53–83%"로 바꾼다.
  - 05-plan의 "[x] 각 Phase 뒤 canary … 와 CI: 모두 통과(05a)"는 맞지 않는다. 05a에는 Phase 11 canary가 없고(저장된 run 재채점뿐), CI 기록도 없다. 32cdb2ab CI는 커밋 뒤에 통과했다. 이 줄을 "Phase 9·10 canary, Phase 11은 재채점, CI는 세 Phase의 마지막 커밋 모두 success"로 바꾼다.

### 6 (Suggestion) 반영 표의 "표지마다 한 문장"이 실제보다 넓다

- 위치: `06c-verify-phase10.md:179`, `test_eval_harness.py:1203-1207`.
- 재현: 더한 표지 문장은 06c가 mutation한 넷(still, again, before merg, 다시)뿐이다. 다음 27개는 하나씩 지워도 green이다(A8–A11, A13 실제 pytest로 확인).
  - 표지: `require`, `due`, `must`, `pending`, `not yet`, `n't`, `never`, `another`, `second`, `back to`, `필요`, `2차`, `재검토`, `재리뷰`.
  - 규칙 2 동사: `re-run`, `request`, `ask for`, `get`, `send`, `schedule`.
  - 규칙 3: `without`, `never`, `nobody`, `n't`. 규칙 3의 `F-1`·`commit`.
  - `;`를 절 구분에서 빼는 것.

  종류 단위로는 고정돼 있어서 결함은 아니다. 다만 죽은 대안인지 구별할 수 없다.
- 수정: 반영 표를 "06c가 짚은 넷"으로 고친다. 또는 대안마다 한 문장을 넣거나 쓰지 않는 대안을 지운다.

## Mutation

| # | mutation | 결과 |
|---|---|---|
| A1 / A2 | glob → `tests/__pycache__/*.pyc` / `**/*.pyc` | red / red |
| A3 / A4 | `build_workspace` ignore 삭제 / `FIXTURE_IGNORE`의 `__pycache__` 삭제 | red / red |
| A5 | `run_task` env pop 삭제 | **green** |
| A6 | `_fixture_ws`의 `WS_GITIGNORE` 쓰기 삭제 | red |
| A7 | 규칙 2 `then` 삭제 | red |
| A8 / A13 | 표지 `due` / `another` 삭제 | **green** / **green**(둘 함께는 red) |
| A9 / A10 | 규칙 2 `send` / 규칙 3 `nobody` 삭제 | **green** / **green** |
| A11 | `;`를 절 구분에서 뺌 | **green** |
| A12 | 규칙 2에 `have` 추가(알려진 miss를 맞힘) | red |
| B1 / B3 | `` `/sc:test` -> done `` / `` `/sc:test`→done `` 심기 | red / red |
| B2 | 심기 + 가드에서 `` `? `` 삭제 | green(가드가 잡는 것임을 확인) |
| 창 | 규칙 2 25→200·25→0, 규칙 3 10→60·10→0, fix 조건 삭제 | red ×5(시뮬레이션) |

표지 단위 시뮬레이션 51건은 테스트 표(`_RG_*`)를 그대로 읽어 돌렸다. green으로 나온 것 가운데 다섯(A8–A11, A13)은 실제 pytest로 다시 확인했다.

## 확인하지 못한 것

- Claude Code의 Bash 도구가 사용자 셸 rc를 다시 읽어서, 지운 변수를 되살리는지는 `claude`를 띄울 수 없어 확인하지 않았다.
- 발견 1의 수정은 임시 편집으로만 확인했다.

## 반영 (2026-10-21, claude-box, Phase 12)

| # | 처리 |
|---|---|
| 1 (Important) | 반영: `run_eval.BYTECODE_ENV`(`PYTHONDONTWRITEBYTECODE`, `PYTHONPYCACHEPREFIX`, `PYTHONOPTIMIZE`) 하나를 프로브 세션과 단위 테스트의 `_pytest`·import 호출이 같이 쓴다. 세 변수를 각각 켠 셸에서 `test_eval_harness.py`가 통과한다(89 passed) |
| 2 | 반영: `PYTHONOPTIMIZE`를 더했다. `test_probe_session_keeps_bytecode_on`이 기존 `fake_run` 꼴로 세션 env를 본다. 세 이름을 테스트가 직접 적어, 상수에서 하나를 빼도 red다 |
| 3 | 반영: 규칙 2의 대상이 `review(?!ed)`다. "committed and then reviewed" 꼴의 서술은 요청이 아니다. 실패로 고정했다. heldout2·heldout3 값은 바뀌지 않았다 |
| 목록·화살표 꼴 | 받아들임: 권고대로 정규식은 그대로 두고 05a의 miss 종류에 있다 |
| 문서 | 반영: 05a에 heldout3 생성에서 뺀 문장 종류, 주석은 측정값(53–83%), 05-plan의 canary 표시는 "Phase 11·12는 command 본문을 바꾸지 않아 저장된 run을 다시 채점"으로 고쳤다 |
| "표지마다 한 문장" | 정정: 06c 반영 표 5의 그 말은 과장이다. 표지 낱말 일곱(still, again, should, before merg, 다시 등)만 하나씩 지키고, 27개 대안 전부를 지키지는 않는다 |

Mutation(메모리의 원본으로 되돌림): env pop 삭제, `BYTECODE_ENV`에서 `PYTHONOPTIMIZE` 삭제, 규칙 2의 `(?!ed)` 삭제. 3건 모두 red다.
