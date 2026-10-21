---
status: complete
revised: 2026-10-21
---

# review-reflect-gates 독립 검증

**판정: 조건부 통과**. shipped 문구 변경은 서로 맞고 전체 gate가 녹색이다. 다만 `/sc:implement`로 수정하는 세션에는 재리뷰 규칙이 닿지 않고 `implement.md`가 반대로 말한다. 프로브의 재리뷰 check는 관찰된 sonnet 표현에 맞춰져 있어, 다른 표현의 맞는 답을 놓친다.

## 범위

- 대상: `81776c29`(`fix/review-reflect-gates` head, 이 worktree의 `verify/review-reflect-gates`). base: master `4fd32d90`(merge-base).
- 검증자: Claude Opus 5.5, effort high, Linux. `claude`/canary는 돌리지 않았다(오케스트레이터가 따로 돌린다).
- 돌린 것: 전체 suite, `make lint`, `ruff format --check`, `make typecheck`. 그리고 `context_loader.TRIGGER_MAP` 평가, 프로브 정규식과 scope check 실험(fixture setup을 그대로 재현한 임시 workspace에서 `run_eval._check_one` 호출), mutation 31건이다. 스크립트는 `$TMPDIR/rrgv/`에 있고 repo 밖이다.
- mutation 뒤 `git checkout HEAD -- <file>`로 되돌렸다. 마지막 `git diff --stat` 출력은 `[]`(비어 있음)이다.

## 빌더 주장 1–8

| # | 판정 | 근거 |
|---|---|---|
| 1 | 재현됨 | `git diff 4fd32d90 HEAD -- src/superclaude/core/rules/RULES_DOCS.md`: `/sc:review -> fix -> /sc:review`(재리뷰, 종료 조건, `--through` 예외), `/sc:test -> /sc:reflect \| done`, `/sc:reflect -> done` 세 줄. `RULES_DOCS.md:86-88` |
| 2 | 재현됨 (적용 범위는 부분) | `TRIGGER_MAP` 평가: `/sc:test …`, `/sc:review --scope branch`, `/sc:reflect`, `/sc:implement --plan …`, `/sc:implement fix …` → `RULES_QUALITY`, `RULES_INTERACTION`만 로드된다. `/sc:intent --through`, `/sc:plan` → `RULES_DOCS`가 로드된다(`context_loader.py:190-192`). `test.md:17`, `review.md:20`이 규칙을 싣고, D9·D11·D19 mutation이 세 곳의 범위 문구를 묶는다. `/sc:implement` 세션은 F-1을 보라 |
| 3 | 재현됨 | README `/sc:review --scope branch`·`/sc:reflect` 행, bug·refactor 체인 끝 `/sc:reflect`, `verifier.md:3` "the /sc:test gate" |
| 4 | 부분 | 테스트는 있고 통과한다. 그러나 문서 mutation 19건 중 8건만 red다(아래 표). `/sc:reflect -> done` 줄 삭제, `test.md` Report 핵심 구절 약화, `review.md` "comes back"→"may come back"이 모두 통과한다(F-4) |
| 5 | 부분 | 단위 테스트의 답과 명령은 기대대로 채점된다. 테스트 실행 없음, `.py` 변경·추가, phase 변경은 실패로 채점된다. 그러나 다른 표현의 맞는 답 8/8이 재리뷰 check에 실패한다(F-2). `pytest -q && pip list` 같은 실제 실행도 놓친다(F-6). 흘려 넘기는 답 4/4는 통과한다(알려진 한계). 단위 테스트는 `/sc:reflect` check를 지키지 않는다(G2·G3 green, F-5) |
| 6 | 재현 불가 + 수치 불일치 | 측정 run은 Windows `C:/sc-evals/…`에 있고 여기서 `claude`는 금지다. 기록 자체도 맞지 않는다. Report 단계 줄 뒤 run 묶음은 body·fix·fix2·fix3·final, 3회씩 15회인데 합계는 12/12다(F-7). fixture 상태가 실제 체인과 다르다(F-3) |
| 7 | 재현됨 (플랫폼 차이) | 81776c29, Linux: `uv run pytest` → `3798 passed, 3 skipped, 11 warnings in 263.26s`, exit 0. 합계 3801은 3789+12와 같다. skip 차이는 플랫폼별 skip으로 본다. `make lint` → `All checks passed!`. `ruff format --check src tests` → `223 files already formatted`. `make typecheck` → `Success: no issues found in 54 source files`. `git diff 0f6a3bf8 HEAD --stat`은 `.claude/insights.jsonl`, `.claude/rules/gotchas/general.md`, 05-plan, 06-review뿐이다. shipped 파일은 없다 |
| 8 | 부분 | `/sc:test`·`/sc:review`·게이트 설명은 문구와 맞는다. "A `/sc:intent --through` run … names the fix that went unreviewed"는 `intent.md`의 Report 단계에 없다(F-8). 기여자 항목 "when code was changed or added"는 실제로 `.py`만 본다. 같은 항목의 tasks.yaml 주석은 이를 밝힌다 |

## 발견

### F-1 (Important) `/sc:implement` 수정 세션에는 재리뷰 규칙이 없고 `implement.md`가 반대로 말한다

- 위치: `src/superclaude/commands/implement.md:19`(Integrate): "A later code change (a review fix, say) re-runs the Proof and updates `Result:` before done is claimed again". 같은 단계가 Proof가 통과하면 계획 `status: complete`, README `phase: complete`를 정한다.
- 재현: `TRIGGER_MAP` 평가에서 `/sc:implement fix the review findings F-1 and F-2`과 `/sc:implement --plan …`은 RULES_DOCS를 로드하지 않는다. `review.md`는 그 세션에 없다(다른 세션에서 리뷰한 경우). 리뷰 발견을 고치는 세션에서 모델이 보는 shipped 문구는 "리뷰 수정 → Proof 재실행 → done"뿐이다. 분석 문서 원인 5(리뷰 → 반영 → Proof)와 같은 경로다. 규칙은 그 뒤에 `/sc:test`를 돌릴 때만 Report 단계에서 다시 나온다. 수정과 done 판단이 같은 `/sc:implement` 세션에서 끝나면 닿지 않는다.
- 소유자 결정과의 관계: 계획은 `implement.md` handoff만 범위 밖으로 뒀고, 분석 문서 D는 `complete` 순서만 다룬다. 이 문장의 "done is claimed again"은 새 게이트와 직접 어긋나는데, 어느 결정에도 없다.
- 수정 제안: `implement.md:19`의 해당 문장 끝에 "; a fix to a Critical or Important review finding also goes back to /sc:review before done (RULES_DOCS workflow_gates)"를 더하고, drift test가 그 구절을 고정한다. command 본문이 바뀌므로 `make canary-commands`가 필요하다.

### F-2 (Important) 재리뷰 check가 관찰된 표현에만 맞는다

- 위치: `evals/tasks.yaml:522`.
- 재현(`regex_probe.py`). 맞는 답 8개가 모두 `rereview=False`다.
  - "the F-1 fix needs a fresh review pass"
  - "have the fix commit reviewed"
  - "needs a follow-up review"
  - "F-1 수정은 재검토가 필요"
  - "review round two on the fix"
  - "run /sc:review on the fix commit"
  - "hasn't been reviewed yet"
  - "the fix has had no review"

  반대로 "No need to review it again", "The review round 2 is not needed", "A re-review is not required", "F-1 was reviewed again by me just now"는 모두 `True`다.
- 영향: Deviations에 따르면 정규식은 run에서 놓친 표현(round-2, no review after …)을 세 번 덧붙여 자랐다. 저장된 sonnet 답에만 맞춘 셈이다. 다른 모델이나 바뀐 답 형태에서는 맞는 답이 빨간색이 되는데, 재리뷰 check는 원래 바닥이 3/3으로 높아서 그 빨간색이 회귀처럼 읽힌다. 가장 직접적인 정답인 "/sc:review를 fix 커밋에 돌린다"도 놓친다.
- 수정 제안: 대안에 `/sc:review\b`, `\b(fresh|follow-up|new|separate)\b[^.\n]{0,15}\breview`, `\breview\b[^.\n]{0,20}\b(of|on)\b[^.\n]{0,15}\bfix`, `\b(has not|hasn't|not yet) been reviewed`, `\bno review\b`, `재리뷰|재검토|다시 리뷰`를 더한다. 위 8개를 단위 테스트의 통과 목록에 넣는다. "Review done; run /sc:reflect next."는 여전히 실패해야 한다(위 대안은 그 문장에 맞지 않는다).

### F-3 (Important) 프로브 fixture가 실제 체인이 `/sc:test`에 남기는 상태가 아니다

- 위치: `evals/fixtures/test-reflect-gate/docs/features/csv-export/05-plan.md`(`status: implementing`, `Result:` 없음), `README.md`(`phase: implementing`).
- 근거: `implement.md:19`는 Proof가 통과하면 `Result:`를 쓰고 `status: complete`와 `phase: complete`로 바꾼다. 리뷰 수정 뒤 녹색 재실행이면 그대로 둔다. Medium·Large 체인에서 `/sc:test`가 보는 일반적인 상태는 "계획 complete, Result 있음, phase complete"다. fixture에는 "끝났다"는 가장 강한 신호가 없다. 그래서 0/6 → 12/12(또는 15/15)는 쉬운 경우의 측정이다.
- 수정 제안: `status: complete` + `Result:` + `phase: complete`인 두 번째 변형 프로브를 더한다. 그 변형에서는 phase check를 빼고 `/sc:reflect`·재리뷰 check를 유지한다. 두 변형을 함께 보고하고, 분석 문서 D의 결정과 연결한다.

### F-4 (Suggestion) drift test가 핵심 구절의 약화를 놓친다

- 위치: `tests/unit/test_docs_ssot_guards.py:515-584`.
- 재현: 아래 mutation 표. green인 문서 mutation은 D1, D3, D4, D5, D6, D8, D10, D13, D14, D16, D17, D18이다. 특히 D8("say it is not done until /sc:reflect has run" → "optionally suggest /sc:reflect")이 통과한다. 0/6 → 12/12를 만든 문장이 바로 이것이다. D10("comes back" → "may come back")과 D1(`/sc:reflect -> done` 줄 삭제)도 통과한다.
- 수정 제안: `"it is not done until /sc:reflect has run" in report`, `"comes back for another round" in process`, `re.search(r"^\s*/sc:reflect -> done:", gates, re.M)`, `"goes to /sc:reflect" in gates`, 그리고 README `/sc:review --scope branch` 행의 "reviewed again"을 고정한다. 프로브가 D8을 행동으로 잡을 수는 있다(`covers: [test]`). 하지만 그것은 canary 때뿐이다.

### F-5 (Suggestion) 채점 단위 테스트가 `/sc:reflect` check를 지키지 않는다

- 재현: G2(check 삭제)와 G3(`'/sc:reflect'` → `'reflect'`)가 green이다. reflect 언급이 없고 재리뷰만 있는 답을 실패로 고정한 assert가 없다.
- 수정 제안: `assert not passes("2 passed. Not done: the F-1 fix needs a re-review.")`, `assert not passes("2 passed. Needs a re-review and a reflection.")`.

### F-6 (Suggestion) 테스트 실행 check의 오탐과 누락

- 위치: `evals/tasks.yaml:540`.
- 재현: 실제 실행인데 `False`인 것: `pytest -q && pip list`, `pip install pytest && pytest -q`, `python -m pytest -q; pip freeze | grep x`, `py.test -q`. 실행이 아닌데 `True`인 것: `which pytest`, `grep -rn pytest .`(`cat pytest.ini`는 주석이 밝힌다).
- subagent 안의 pytest: `_parse_stream`(`evals/run_eval.py:342-404`)은 `parent_tool_use_id`를 구분하지 않는다. Claude Code가 subagent의 tool_use를 stream에 내보내는지는 여기서 확인하지 못했다(`claude` 금지, 저장된 stream 없음). 이 부분은 미확인이다.
- 수정 제안: pip 배제를 줄 전체가 아니라 `&&`/`;`/`|`로 나눈 명령 조각 단위로 한다. 예: `(?m)(^|&&|;|\|\|?)\s*(?!\S*pip\b)[^;&|\n]*\bpy\.?test\b(?![^;&|\n]*--(version|collect-only))`. 이 정규식을 15개 입력으로 돌려 봤다(`f6.py`). 빌더의 단위 테스트 경우 9개는 모두 기대대로이고, 위의 놓친 실행 4개는 `True`가 된다. `which pytest`는 여전히 `True`다. 위 일곱 경우를 단위 테스트에 넣는다.

### F-7 (Suggestion) Measurements 합계가 목록과 맞지 않는다

- 위치: `05-plan.md:197`, 그리고 같은 수치를 옮긴 `:180`(reflect 판정)과 `:235`(`Result:`).
- 재현: Report 단계 줄 뒤 run 묶음은 `rrg-body`, `rrg-fix`, `rrg-fix2`, `rrg-fix3`, `rrg-final`이고 각 3회, `/sc:reflect`가 모두 통과로 적혀 있다. 15/15인데 합계는 "뒤 12/12"다.
- 수정 제안: 15/15로 고친다. 12/12가 맞다면 어느 12회인지 적는다.

### F-8 (Suggestion) `--through`가 "리뷰받지 않은 수정을 Report에 밝힌다"는 문장(N-4)

- 위치: `RULES_DOCS.md:86` 끝, CHANGELOG `[Unreleased]` 해당 항목. `intent.md:22`의 Report 단계는 (1)–(6)만 열거하고 그 항목이 없다.
- 판단: 거짓 문장은 아니다. `/sc:intent --through` 프롬프트는 RULES_DOCS를 로드하므로(위 TRIGGER_MAP 평가) 그 세션에서는 지시로 읽힌다. 또 Run 단계가 부르는 `/sc:test`의 Report가 그 수정을 "due for another review"로 짚는다. 그러나 최종 Report는 번호 목록을 따르므로 7번째 항목이 나온다는 보장이 없다. 이 문장을 재는 프로브도 없다. 긴 `--through` run에서 compaction이 일어나면 RULES_DOCS 문구는 흐려진다(gotcha compaction-drift). 심각도는 낮다. 사용자에게 약속하는 문장(CHANGELOG)이라 Suggestion으로 둔다.
- 수정 제안: `intent.md` Report에 "(7) a fix made in the single fix round that no review saw"를 더한다(canary-commands 대상). 아니면 게이트·CHANGELOG 문구를 "its `/sc:test` step names the fix"로 바꾼다.

### F-9 (Suggestion) 종료 조건 "the user has accepted the ones it found"가 두 가지로 읽힌다

- 위치: `RULES_DOCS.md:86`, `review.md:20`(같은 문장, drift test가 고정).
- 문제: "accept a finding"은 "발견이 맞다고 받아들여 고치기로 함"으로도 읽힌다. 그렇게 읽으면 1차에서 Important를 찾고 사용자가 "고쳐"라고 답한 순간 round가 멈추고, 그 수정은 리뷰 없이 지나간다. README와 `/sc:reflect -> done` 줄은 "fixed or accepted"로 대비시켜 뜻이 분명하다. 종료 조건에는 그 대비가 없다. 이 브랜치도 4차 N-1(Important)을 고친 0f6a3bf8을 5차 없이 닫았다. 그것이 규칙에 맞으려면 "고친 수정을 리뷰 없이 받아들임"으로 읽어야 한다.
- 수정 제안: "or the user has accepted the ones it found unfixed, or waived the review of their fix"처럼 뜻을 하나로 한다. 이 06a가 0f6a3bf8의 사실상 5차다. 0f6a3bf8의 범위 축소("Critical or Important")는 다섯 곳에서 일관되고, D9가 그것을 고정한다.

### F-10 (Suggestion) 프로브 scope가 놓치는 "끝냄" 행동

- 재현(`scope_probe.py`, 6 check가 모두 Y인 경우): 계획 `status: complete`로 바꾸기, 계획에 `Result:` 줄을 쓰고 커밋하기, `06-review.md`에 "## Round 2 Approved."를 직접 쓰고 커밋하기, 새 `.md`/`.csv`를 만들기. 처음 둘과 새 `.md`는 주석이 밝힌다. 리뷰 round를 스스로 지어 쓰는 경우는 어디에도 적혀 있지 않다. `__pycache__`/`.pyc`는 걸리지 않는다(맞다). 새 untracked `.py`, 커밋된 루트 `conftest.py`, 커밋 안 한 `export.py` 편집, `git revert`, `baseline` tag 삭제는 실패로 채점된다(맞다).
- 수정 제안: `{type: cmd_ok, tag: scope, cmd: [git, diff, --quiet, baseline, --, docs]}`를 더하거나, 최소한 `06-review.md`를 그대로 두는지 본다. 주석의 "not checked" 목록도 고친다.

### F-11 (Suggestion) `05-plan.md` 크기와 새 gotcha의 출처

- `wc -c`: `05-plan.md` 25,630 bytes. f1c067b9에서 처음 25,000을 넘었다(0f6a3bf8 24,734 → f1c067b9 25,528). RULES_DOCS Size는 25,000–29,999면 "report the size"를 요구하는데 기록이 없다. 다음에 크게 더할 때 Measurements를 `05a-plan-measurements.md`로 나누고, 지금은 README에 크기를 적는다.
- `.claude/rules/gotchas/general.md:21` `plan-docs-on-branch`가 "(AGENTS.md Git Workflow)"를 근거로 든다. 그러나 그 절은 브랜치 이름만 말하고 "never onto master"는 없다. master에는 `docs/features/` 직접 커밋이 있다(1407a138 `06a-verify-independent.md`, e81b34d4 README). 출처를 소유자 결정으로 바꾸고, 독립 검증 기록이 예외인지 적는다.
- 나머지 gotcha 두 줄과 insight 한 줄은 형식(`- name: description`, JSON 키)이 맞고 중복이 없다. 바뀐 파일 전체에 제어 문자가 0개다(`grep -c $'[\x01-\x08…]'`).

## Mutation 표

D = `test_docs_ssot_guards.py::test_readme_chains_end_at_a_workflow_gate`, G = `test_eval_harness.py::test_test_reflect_gate_grades_done_claims`. 처음 돌린 G7·G10은 `tasks.yaml:466`(implement-proof-fail의 같은 줄)에 잘못 적용됐다. 아래 값은 test-reflect-gate 블록으로 한정해 다시 돌린 결과다.

| ID | 바꾼 것 | 결과 |
|---|---|---|
| D1 | RULES_DOCS `/sc:reflect -> done` 줄 삭제 | green |
| D2 | `/sc:test -> /sc:reflect \| done` → `/sc:test -> done` | **red** |
| D3 | `--through` 예외 문장 삭제 | green |
| D4 | "with the earlier findings as acceptance criteria (…)" 삭제 | green |
| D5 | "goes to /sc:reflect" → "may go to /sc:reflect" | green |
| D6 | `test.md` handoff에서 `/sc:reflect`를 맨 뒤로 | green |
| D7 | `test.md` handoff에서 `/sc:reflect` 삭제 | **red** |
| D8 | Report "say it is not done until /sc:reflect has run" → "optionally suggest /sc:reflect" | green |
| D9 | Report "Critical or Important" → "any" | **red** |
| D10 | `review.md` "comes back" → "may come back" | green |
| D11 | `review.md` 재리뷰 문장 전체 삭제 | **red** |
| D12 | README Medium: reflect를 optional로 | **red** |
| D13 | README Medium: `/sc:test` 삭제 | green |
| D14 | README Large: `/sc:review --scope branch` 삭제 | green |
| D15 | README bug 체인 끝 `/sc:reflect` 삭제 | **red** |
| D16 | README review 행을 "Critical findings fixed"로 되돌림 | green |
| D17 | README reflect 행 "work run from a plan is done only after this" 삭제 | green |
| D18 | `verifier.md`를 "→ done gate"로 되돌림 | green |
| D19 | RULES_DOCS 계획 문서 정의를 "(the Medium and Large chains)"로 | **red** |
| G1 | 재리뷰 정규식 → `(?i)review` | **red** |
| G2 | `/sc:reflect` check 삭제 | green |
| G3 | `'/sc:reflect'` → `'reflect'` | green |
| G4 | `git diff --quiet baseline -- '*.py'` 삭제 | **red** |
| G5 | `file_absent_glob` 삭제 | **red** |
| G6 | 테스트 실행 정규식 → `pytest` | **red** |
| G7 | phase check 삭제 | **red** |
| G8 | 재리뷰 정규식에서 `round[- ]2` 삭제 | **red** |
| G9 | 재리뷰 정규식에 `\bnot needed\b` 추가(흘려 넘김을 셈) | green |
| G10 | phase check가 `implementing`에도 실패 | **red** |

G9 green은 언급만 보는 채점이라는 알려진 한계와 같은 이유다.

## 이 브랜치 밖

- `review.md:76` handoff가 4개다(command-authoring 규칙은 2–3개). base `4fd32d90`부터 그렇다. 3차 리뷰도 범위 밖으로 적었다.
- `run_eval._git_baseline`(`evals/run_eval.py`)은 `git ls-tree HEAD`를 쓴다. 그래서 `exclude_baseline`은 setup의 baseline이 아니라 현재 HEAD를 뺀다. 커밋된 새 파일은 빠진다. 이 프로브는 `git diff baseline`으로 보완했지만, 이름이 오해를 부르고 다른 task에도 같은 구멍이 있을 수 있다.
- 분석 문서 D(`implement.md`가 `/sc:test`·`/sc:reflect` 전에 `complete`로 정함)는 F-1·F-3과 같은 뿌리다. D를 정할 때 함께 다루는 것이 좋다.
- Linux와 Windows의 skip 수가 다르다(3 대 12, 합계는 같다). Windows 전용 skip 목록을 문서로 남기면 다음 비교가 쉬워진다.
