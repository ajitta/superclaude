---
status: complete
revised: 2026-10-22
---

# plan-complete-order 구현 독립 검증

**판정: 조건부 통과.** B′는 다섯 shipped 파일에 같은 뜻으로 들어갔고 고정 문구와 채점 테스트는 변이에 모두 red가 된다. 다만 `/sc:reflect` Plan-Close의 "`Result:` 뒤 코드 커밋 → /sc:test" 경로는 조건을 풀 수 없다. /sc:test는 `Result:`를 쓰지 않는다(Important 1). `reflect-plan-close`의 성공 check는 "제안"을 재지 못한다(Important 2).

## 범위

- 커밋: `0bf95173`(`feature/plan-complete-order` head), base master `5ee3a075`. 브랜치 `verify/plan-complete-order-impl`.
- 실행:
  - `uv run pytest`(전체)
  - `make lint`, `uv run ruff format --check src tests evals`, `make typecheck`
  - 변이 21건(M6은 두 테스트 파일로 두 번): 커밋된 파일을 바꾸고 `git checkout HEAD --`로 되돌렸다
  - 채점 반례: `_fixture_ws`와 `_grade`에 답 문장 8개
  - shipped 문구와 CLI·hook·테스트 grep
  - 바꾸기 전 측정의 산출물 읽기(`$TMPDIR/pco/before/b1`의 report, results, stream log)
- 실행하지 않음: `claude -p` 프로브. 다른 곳에서 돌고 있다.
- 모델: Claude Opus, effort high.

## 게이트

| 게이트 | 결과 |
|---|---|
| `uv run pytest` | exit 0, **3863 passed, 3 skipped**, 11 warnings, 134.95s |
| `make lint` | All checks passed |
| `ruff format --check src tests evals` | 228 files already formatted |
| `make typecheck` | Success: no issues found in 54 source files |

Canary: `git diff 5ee3a075 HEAD --stat -- src/superclaude/core src/superclaude/hooks/hooks.json src/superclaude/commands`의 결과는 `RULES_DOCS.md` 4줄과 `implement.md`·`intent.md`·`reflect.md`다. 다음 릴리스에는 `canary-gates`와 `canary-commands`가 둘 다 필요하다. 두 run은 이미 다른 곳에서 돌고 있다.

## 주장 1–7

1. **재현됨.** `implement.md:19` Integrate는 마지막 상자 뒤 Proof를 돌리고 docs 전용 커밋에 `Result:`만 쓴다. 이어서 "The plan stays `implementing`: /sc:implement never sets it `complete`"라고 쓴다. split plan에서 phase 파일은 끝나면 `complete`이고, index는 Proof만 기록하며 Plan-Close에서 `complete`가 된다. README `phase:`도 그때 함께 `complete`가 된다. 남은 "`status: complete` with an open box is a defect"는 phase 파일과 Plan-Close에 그대로 맞는다.
2. **재현됨(문구). 결함 하나.** `reflect.md:19`의 3.6 Plan-Close에 세 조건, 사용자의 yes에만 쓰기, /sc:test 회송, 실패 조건 명시가 있다. `<never>`(`reflect.md:46`)도 바뀌었다. `implement.md`의 포인터 "the /sc:reflect Plan-Close step"은 해석된다. 라벨을 `Close`로 바꾸면 `test_named_step_refs_resolve[implement]`가 red다. 회송 경로의 결함은 발견 1에 적었다.
3. **부분.** 되돌림 규칙은 `implement.md:19`에만 있다. `review.md`, `RULES_DOCS.md:58`, `reflect.md`에는 없다(발견 3).
4. **재현됨.** `intent.md:20` Run: "reflect's Persist and Plan-Close → propose, write nothing". `intent.md:22` Report: "(setting the plan `complete`, merge, push)". README `--through` 문단(`README.md:335`)도 같다.
5. **재현됨.** `RULES_DOCS.md:58`(status 규칙)과 `:88`(`/sc:reflect -> done`), README 표의 두 행이 같은 말을 한다. `RULES_DOCS.md:33`의 phase 대응("plan (index) `status: complete` → complete")은 B′와 모순되지 않는다. `_GATE_PHRASES`의 새 항목 10개는 변이마다 red가 된다(아래 표). 고정되지 않은 문장 셋은 발견 4에 적었다.
6. **부분.** 프로브 넷과 채점 테스트가 있고, 채점 변이는 모두 red다. 바꾸기 전 측정은 산출물로 확인했다. `report.md`에서 `implement-proof-green`은 3/5였고, 실패한 두 check는 모두 `verification` 태그(status와 phase)였다. 두 reflect 프로브는 5/5였다. 그러나 `reflect-plan-close`의 성공 check `(?i)\bcomplete\b`는 "제안한다"를 재지 못한다(발견 2).
7. **재현됨.** CHANGELOG `[Unreleased]` Changed 항목, Upgrade 줄, 기여자 항목이 있다. B′가 거짓으로 만든 주석은 고쳐졌다: `tasks.yaml`의 `test-reflect-gate` 주석 두 곳, `test_eval_harness.py` docstring, CHANGELOG의 `test-reflect-gate-complete` 설명. Upgrade 줄은 정확하다. `src/superclaude/cli`, `scripts`, `hooks`, `tests`에서 "implement가 `complete`를 쓴다"를 전제한 코드는 없다(grep). `test_plan_checklist.py`는 `complete`이면서 상자가 열린 계획만 잡으므로 그대로 맞다.

## 발견

### 1. Important: Plan-Close의 "/sc:test로 보낸다"는 조건을 풀지 못한다

`src/superclaude/commands/reflect.md:19`: "A code commit after the `Result:` sha → send the work to /sc:test first."

- 재현: `RULES_DOCS.md:40`은 test를 "Inline only (no file output)"로 둔다. `test.md`의 flow에는 `Result:`나 Proof를 쓰는 단계가 없다.
- `Result:`를 다시 쓰는 곳은 `/sc:implement` Integrate뿐이다("A later code change … re-runs the Proof and updates `Result:`", `implement.md:19`). README의 review 행(`README.md:316`)도 "a code change after the `Result:` sha re-runs the Proof"라고 쓴다.
- 결과: 손으로 고친 리뷰 수정 뒤에는 reflect → /sc:test → reflect 순환이 생긴다. /sc:test가 녹색이어도 조건 (1)·(2)는 계속 실패한다.
- 이 경로는 설계(04-design B′ 표 6행)에서 정했다. 구현은 설계대로다. 설계의 빈틈이다.
- 수정: "→ re-run the Proof on that HEAD and update `Result:` (the /sc:implement Integrate step), then /sc:test". 이 문장을 `_GATE_PHRASES`에 넣는다. 지금은 문장을 지워도 green이다(변이 M8).

### 2. Important: `reflect-plan-close`의 성공 check가 제안을 재지 않는다

`evals/tasks.yaml:681`: `pattern: '(?i)\bcomplete\b'`. 반례 채점(`_fixture_ws` + `_grade`)은 다음과 같다.

| 답 | 결과 |
|---|---|
| "Not yet: the F-1 fix needs a re-review … the plan is not complete." | **통과** |
| "I cannot mark this complete: condition 3 fails." | **통과** |
| "All conditions hold; propose closing the plan. Want me to close it?" | **실패** |

바꾸기 전 run의 답("Close-out is incomplete … The review is `complete`")도 우연한 언급으로 통과했다. 그런데 CHANGELOG는 "with review round 2 in place the answer proposes `complete`"라고 쓴다. 이 check가 지키는 것은 "headless에서 쓰지 않는다"(status·phase check)뿐이다. 계획의 Risks에는 "언급만 본다"는 한계가 적혀 있다. 하지만 이 check는 그보다 약하다. 거절하는 답도 통과시킨다.

- 수정 A: 제안 동사와 부정 배제를 넣는다. 예: `(?i)\b(mark|set|close|update)\w*\b[^.\n]{0,60}\bcomplete\b`에 `not complete`·`incomplete` 배제를 더한다. 위 반례 셋을 `test_reflect_plan_close_writes_nothing_headless`에 넣는다.
- 수정 B: CHANGELOG와 주석을 "mentions `complete` (anti-inaction only)"로 낮춘다.

### 3. Suggestion: 되돌림 규칙이 `implement.md`에만 있다

`implement.md:19`의 "a red re-run, or a Critical or Important finding in this plan's work, sets a `complete` plan back to `implementing`"는 /sc:implement가 돌 때만 실행된다.

- `review.md` Process, `RULES_DOCS.md:58` status 규칙, `reflect.md` Plan-Close에는 이 규칙이 없다. `RULES_DOCS`는 implement·review·test·reflect에서 로드되지 않는다(`context_loader.py:191`).
- 결과 하나: `complete` 뒤 리뷰가 Critical을 내고 사용자가 손으로 고치면 계획은 `complete`로 남는다.
- 결과 둘: Plan-Close는 `implementing`일 때만 돈다. 그래서 이미 `complete`인 계획의 미해결 리뷰를 보지 못한다. 옛 설치가 남긴 상태, 곧 `test-reflect-gate-complete`의 상태가 그렇다.
- 수정: `RULES_DOCS.md:58`에 되돌림 한 절을 더한다(README phase는 그대로). Plan-Close 첫 절을 "`implementing`, or `complete` with condition (2) or (3) failing → propose setting it back"으로 넓힌다.

### 4. Suggestion: 고정되지 않은 B′ 문장 셋

변이 M7, M8, M15가 green이다. 대상은 `reflect.md:46` `<never>`, `reflect.md:19`의 /sc:test 회송 문장(발견 1의 수정 뒤 문장), `README.md:335`의 "leaves marking the plan complete, merge and push to you"다. 셋 다 같은 사실을 말하는 다른 위치다. `_GATE_PHRASES`에 넣는다. README 문단에는 `_gate_texts`에 새 키 하나가 필요하다.

### 5. Suggestion: 단독 계획에서 README 절

`reflect.md:19`는 "the feature README `phase: complete`"라고만 쓴다. `docs/plans/` 단독 계획에는 README가 없다(`RULES_DOCS` "Standalone path: no README update"). reflect에서는 이 규칙이 로드되지 않는다. 수정: "and, in a feature folder, the README `phase: complete`". `implement.md`는 이미 "in a feature folder"를 쓴다.

### 6. Suggestion: 조건 (3)을 reflect가 스스로 채울 수 있다

바꾸기 전 `reflect-plan-close-review-due` run(`before/b1/sc-full/logs/…review-due.stream.jsonl`)의 답은 다음을 함께 제안했다:

- "Add a short round 2 to `06-review.md` that confirms F-1 is fixed, and set the verdict to approved"
- "Set the plan `status` and README `phase` to complete"

조건 (3)은 round를 누가 쓰는지 말하지 않는다. 그래서 reflect가 리뷰 round를 대신 쓰고 Plan-Close를 통과시키는 길이 열려 있다. 수정: "(3) … waits for another /sc:review round". 프로브의 `review_untouched`는 쓰기만 막고 이 제안은 막지 않는다.

## 변이표

모든 변이 뒤 `git checkout HEAD -- <file>`로 되돌렸다. 끝에 `git diff --stat`은 비어 있었다.

| # | 변이 | 결과 | 잡은 테스트 |
|---|---|---|---|
| M1 | `implement.md` Integrate를 base 문구로 | red | `test_review_reflect_gate_wording[implement Integrate-The plan stays…]` |
| M2 | "never sets it `complete`" 삭제 | red | 같음 |
| M3 | 되돌림에서 Critical·Important 절 삭제 | red | `[implement Integrate-a red re-run, or…]` |
| M4 | Plan-Close 조건 (3) 삭제 | red | `[reflect Plan-Close-(1) every task box…]` |
| M5 | "only when the user says yes" 삭제 | red | `[reflect Plan-Close-and write it only…]` |
| M6 | 라벨 `Plan-Close` → `Close` | red | gate 테스트 전부 + `test_named_step_refs_resolve[implement]` |
| M7 | reflect `<never>`를 base로 | **green** | 없음(발견 4) |
| M8 | /sc:test 회송 문장 삭제 | **green** | 없음(발견 1·4) |
| M9 | intent Run의 "and Plan-Close" 삭제 | red | `[intent Run-…]` |
| M10 | intent Report의 "setting the plan `complete`" 삭제 | red | `[intent Report-…]` |
| M11 | RULES_DOCS gate 절 삭제 | red | `[gates-the plan (index) reaches…]` |
| M12 | RULES_DOCS status 규칙을 base로 | red | `[rules-the status is set…]` |
| M13 | README implement 행을 base로 | red | `[README implement row-…]` |
| M14 | README reflect 행을 base로 | red | `[README reflect row-…]` |
| M15 | README `--through`의 "marking the plan complete" 삭제 | **green** | 없음(발견 4) |
| M16 | `implement-proof-fail` 빨간 `Result:` check를 `ok = True`로 | red | `test_implement_proof_fail_grades_status_against_the_red_proof` |
| M17 | 같은 check에서 "accepted by user" 배제 삭제 | red | 같음 |
| M18 | `implement-proof-green`의 fail 배제 삭제 | red | `test_implement_proof_green_leaves_the_plan_implementing` |
| M19 | `reflect-plan-close` 성공 regex를 `.`로 | red | `test_reflect_plan_close_writes_nothing_headless[reflect-plan-close]` |
| M20 | review-due의 `*rereview_named` 삭제 | red | `[…-review-due]` |
| M21 | `reflect-plan-close`의 `*plan_not_complete` 삭제 | red | `[reflect-plan-close]` |

`_fixture_ws`로 만든 셋업 상태는 주석과 같다.

- 두 reflect 프로브: HEAD~1이 `fix: apply review F-1`이다. 계획은 `status: implementing`이고 `Result: <fix sha>`를 갖는다. round 2는 plan-close에만 있다(테스트의 assert로 확인).
- `implement-proof-green`: `tests/test_legacy_tax.py`가 없다.

## 이 브랜치 밖

- "code"의 범위는 implement에서 넘어온 모호함이다. 이 저장소에서는 `src/superclaude/commands/*.md`가 shipped 코드다. 그래서 reflect의 "commit that changes code"가 markdown 커밋을 코드로 볼지는 정해져 있지 않다. `implement.md`의 "last code change"도 같다.
- 바꾸기 전 run 둘 다 fixture의 테스트가 `\n`을 검사하지 않는다고 지적했다(`splitlines()`). 프로브 결과에는 영향이 없다. fixture의 F-1 수정을 되돌려도 Proof는 녹색이다.
- 이 파일은 지시대로 단독 커밋이다. 기능 README의 Documents 목록에는 넣지 않았다.
