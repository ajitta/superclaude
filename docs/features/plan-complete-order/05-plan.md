---
status: implementing
revised: 2026-10-22
---

# 계획 `complete`의 위치 Implementation Plan

**Goal:** 계획(index)은 `/sc:implement`의 녹색 Proof로 `complete`가 되지 않는다. 리뷰·테스트·reflect 게이트를 지난 뒤 `/sc:reflect`가 제안하고 사용자가 답할 때 `complete`가 된다. 그 뒤 Critical·Important가 나오면 `implementing`으로 돌아간다.
**Architecture:** shipped 문구(`implement.md`, `reflect.md`, `intent.md`, `RULES_DOCS.md`, README) 변경과 프로브 셋. 상태 enum과 진입 조건(상자 전부, `Result:`)은 그대로다. 설계: [04-design](./04-design.md) 확정안 B′.
**Tech Stack:** markdown, pytest, `evals/run_eval.py`(로컬 `claude -p`, sonnet).

범위 밖: 릴리스와 범프(보류), 안 D(게이트 상자), `promote-feature.md`, 이미 `complete`인 계획의 이동.

## Phase 1: 프로브와 채점 테스트 (one commit)

### Task 1.1: `implement-proof-fail`이 red `Result:`를 본다

**Files:** Modify: `evals/tasks.yaml`, `tests/unit/test_eval_harness.py`

- [x] Step 1: Write failing test: `test_implement_proof_fail_grades_status_against_the_red_proof`에 계획 Proof 아래 `Result:` 줄이 없으면, 녹색을 주장하면, "(accepted by user)"가 붙으면 실패하는 경우를 넣는다
- [x] Step 2: Verify it fails: `uv run pytest tests/unit/test_eval_harness.py -k proof_fail -q`
- [x] Step 3: check 추가: 계획 파일의 `Result:` 줄이 실패를 적는다(`fail|red|error`)
- [x] Step 4: Verify it passes

### Task 1.2: `implement-proof-green`

**Files:** Modify: `evals/tasks.yaml`, `tests/unit/test_eval_harness.py`

- [x] Step 1: Write failing test: `implement-proof-fail` fixture에서 legacy 테스트를 지운 workspace(녹색 Proof). 계획이 `complete`이면, README가 `complete`이면, `Result:`가 없으면 실패하고, `implementing` + `Result:` + 작업 완료면 통과
- [x] Step 2: Verify it fails (task id 없음)
- [x] Step 3: task 추가(`canary: true`, `canary_only: true`, `covers: [implement]`)
- [x] Step 4: Verify it passes

### Task 1.3: `reflect-plan-close`와 `reflect-plan-close-review-due`

**Files:** Modify: `evals/tasks.yaml`, `tests/unit/test_eval_harness.py`

- [x] Step 1: Write failing test: `test-reflect-gate` fixture 위에 (a) fix 커밋, `Result:` 줄(계획은 `implementing`), 리뷰 Round 2(Critical·Important 없음)를 둔 workspace와 (b) Round 2가 없는 workspace. 둘 다 계획·README가 그대로이고 `.py`가 바뀌지 않아야 통과. (a)는 `complete` 제안을 말해야, (b)는 다음 리뷰를 말해야 통과
- [x] Step 2: Verify it fails
- [x] Step 3: task 둘 추가(`covers: [reflect]`)
- [x] Step 4: Verify it passes
- [x] Step 5: 바꾸기 전 값: 새 프로브 셋을 지금 src로 한 번씩(sonnet, low). 05a 대신 이 계획의 Measurements에 적는다
- [x] Commit Phase 1: `test(evals): implement-proof-green, reflect-plan-close probes; proof-fail reads the Result line`

## Phase 2: shipped 문구 (one commit)

**Files:** Modify: `src/superclaude/commands/implement.md`(Integrate), `src/superclaude/commands/reflect.md`(새 Plan-Close 단계, bounds), `src/superclaude/commands/intent.md`(Run, Report), `src/superclaude/core/rules/RULES_DOCS.md:58,88`, `README.md`(표 두 행, `--through` 문단), `tests/unit/test_docs_ssot_guards.py`(`_GATE_PHRASES`)

- [x] Step 1: Write failing test: `_GATE_PHRASES`에 implement(녹색 Proof 뒤 `implementing`, 되돌림), reflect Plan-Close 세 조건과 사용자 답, intent Run·Report, RULES_DOCS 작성자 표기
- [x] Step 2: Verify it fails: `uv run pytest tests/unit/test_docs_ssot_guards.py -k gate -q`
- [x] Step 3: 문구 편집
- [x] Step 4: Verify it passes; `uv run pytest tests/unit/test_command_structure.py tests/unit/test_cross_references.py tests/unit/test_description_overlap.py tests/unit/test_docs_ssot_guards.py -q`
- [x] Commit Phase 2: `fix(core,implement,reflect,intent): a plan becomes complete on the user's yes to /sc:reflect, not on a green Proof`

## Phase 3: 기록 (one commit)

**Files:** Modify: `CHANGELOG.md`(`[Unreleased]` Changed + upgrade note, 거짓이 된 문장), `evals/tasks.yaml`·`tests/unit/test_eval_harness.py`의 거짓이 된 주석과 docstring, 분석 문서 D, feature README

- [x] Step 1: 편집
- [ ] Step 2: `make canary-commands BASE=<merge-base>`와 새 프로브 셋 3회씩, Measurements에 적는다
- [x] Commit Phase 3: `docs: plan-complete-order — CHANGELOG, upgrade note, measurements`

## Phase 4: 정리 (one commit)

[06-verify](./06-verify.md)(Important 2, Suggestion 4)와 [누더기 감사](../../analysis/patchwork-audit-ajitta-2026-10-22.md)(Important 3, Suggestion 10)를 한 번에 반영한다. 소유자 결정(2026-10-22): 감사 권고 1–4 모두 ★안, 그리고 `/sc:intent --through`와 충돌하지 않게.

**Files:** Modify: `implement.md`, `reflect.md`, `review.md`, `intent.md`, `load.md`, `auto-improve.md`, `RULES_DOCS.md`, `CHANGELOG.md`, `evals/tasks.yaml`, `tests/unit/test_docs_ssot_guards.py`, `tests/unit/test_eval_harness.py`, 기록 문서

- [x] Step 1: shipped 문구: 감사 재작성안 1–5, Plan-Close의 회송을 `/sc:implement --plan`으로, 단독 계획의 README 절, 조건 (3)을 `/sc:review` round로, `complete` 계획의 되돌림을 Plan-Close와 RULES_DOCS 상태 규칙에도
- [x] Step 2: `--through`: implement의 재리뷰 문장에 single fix round 예외, intent Run은 Plan-Close가 지목한 단계를 Report로 넘기고, Report는 Plan-Close 결과와 남은 재리뷰를 적는다. `intent-through-*` 프로브에 "브랜치에 `complete` 없음" check
- [x] Step 3: `_GATE_PHRASES`(문장 23개) → `_GATE_ANCHORS`(낱말)와 약화어 검사. reflect `<never>`와 README `--through` 문단도 넣는다
- [x] Step 4: `reflect-plan-close` 성공 check를 제안 형태로, 거절 답 셋을 채점 테스트에. 재리뷰 채점 문장을 규칙마다 두세 개로, known misses는 05a로. 죽은 대입, `_probe_checks`의 YAML 재읽기, 주석의 발견 ID
- [x] Step 5: CHANGELOG 두 항목을 하나로, 기여자 항목 둘을 한 줄로. 분석 문서 B 완료, 이 README 과거형, review-reflect-gates 05-plan의 긴 `Result:` 측정을 05a로
- [x] Step 6: 변이 16건 모두 red(`$TMPDIR/pco/mutate_clean.py`). 저장된 `reflect-plan-close` run을 새 check로 다시 채점: 바꾼 뒤 3/3 통과, 바꾸기 전 1/1 실패
- [x] Commit Phase 4: `refactor: one statement per rule after the patchwork audit; Plan-Close sends to /sc:implement; --through left open`

## Phase 5: 06a 반영 (one commit)

[06a-verify-cleanup](./06a-verify-cleanup.md)(Important 3, Suggestion 7).

- [x] Step 1: Plan-Close 조건 (2)를 "no commit after its sha changes code"로. implement Load에 상자가 다 찬 계획의 Proof 재실행 진입. phase 파일 문장을 "only when all its boxes are checked"로
- [x] Step 2: `reflect-plan-close` check: 과적합한 부정 lookbehind를 빼고 주석을 실제 한계대로, `clos(?:e|ing)`
- [x] Step 3: 재리뷰 채점 문장 일곱 개 복귀·추가(06a 3). `through_left_open`의 README 상태
- [x] Step 4: 가드: 약화어 목록 확장, 앵커 다섯, `rules`는 Plan docs 줄만
- [x] Step 5: review 포인터를 acceptance criteria 문장으로, RULES_DOCS:58 괄호를 문장으로, README `--through`와 intent Run의 `Result:`, 기록, `import re`
- [x] Commit Phase 5: `fix: Plan-Close closes after a Proof re-run; honest proposal check; grading data guards each regex rule`

## Phase 6: 06b 반영 (one commit)

[06b-verify-round3](./06b-verify-round3.md)(Important 1, Suggestion 5).

- [x] Step 1: Plan-Close 조건 (2)의 사본 넷(RULES_DOCS 상태 규칙과 implement 게이트, README implement 행, CHANGELOG)을 reflect와 같은 뜻으로. 옛 문구("last code commit")를 shipped 본문 전체에서 막는 가드
- [x] Step 2: 앵커 아홉. `skill_called`에 `max`, `intent-through-*`는 `/sc:review` 두 번까지(저장된 run 열 개 모두 두 번)
- [x] Step 3: `reflect-plan-close`: "propose … complete" 갈래, 거절 guard(`output_not_regex`), 채점 답 셋
- [x] Step 4: Plan-Close가 실패 넷 모두에 단계를 준다. implement Load는 --plan 유무로 먼저 나눈다
- [x] Step 5: 재리뷰 채점 문장 규칙 주석 바로잡기, 규칙 3에 둘. 빈 줄, Deviations, README
- [x] Commit Phase 6: `fix: one wording for Plan-Close condition 2 in every copy; --through review count; refusal guard`

## Phase 7: 06c 반영 (one commit)

[06c-verify-round4](./06c-verify-round4.md)(Important 1, Suggestion 5).

- [x] Step 1: Plan-Close 조건 (3)이 열린 Critical·Important 발견도 본다(고쳤거나 사용자가 수락). 그 실패는 사용자에게. CHANGELOG도 같은 뜻으로
- [x] Step 2: `Result:` 줄이 없는 상자 다 찬 계획: Plan-Close와 implement Load가 `/sc:implement --plan`의 Proof 재실행으로
- [x] Step 3: 거절 guard에 "marked"·"setting"·"isn't". 재리뷰 채점 문장 넷. `--through` phase 파일 상태
- [x] Step 4: 앵커는 바뀐 절과 되돌림 동사까지만. 약화어 목록은 늘리지 않는다(Deviations)
- [x] Commit Phase 7: `fix: Plan-Close waits for open review findings; a plan with no Result: line goes back to implement`

## Phase 8: 06d 반영 (one commit)

[06d-verify-round5](./06d-verify-round5.md)(Important 1, Suggestion 4).

- [x] Step 1: `complete` 계획의 되돌림 계기를 사본과 같게: red `Result:` 또는 조건 (3) 실패. `Result:` 뒤 코드 커밋(다른 기능의 것 포함)은 Proof 재실행만
- [x] Step 2: Plan-Close의 근거에 리뷰 발견. CHANGELOG의 조건 (3)을 reflect와 같은 뜻으로
- [x] Step 3: `reflect-plan-close`: 제안 동사 commit·change·move, 부정어 `shouldn't`, 채점 답 셋, 주석
- [x] Step 4: 앵커를 짧게, `--through` 멈춤 조건 앵커, Deviations Phase 7의 가드 기록 바로잡기
- [x] Commit Phase 8: `fix: a complete plan reopens only on a red Result: or an open finding; Plan-Close reads the review findings`

## Phase 9: 06e 반영 (one commit)

[06e-verify-round6](./06e-verify-round6.md)(Important 1, Suggestion 3). 실제 run 하나(`$TMPDIR/pco/r8/x3`, review-due)가 조건 (3)을 "리뷰 파일이 다음 round를 요청하지 않는다"로 읽고 `complete`를 제안했다. 프로브는 그 답을 통과시켰다.

- [x] Step 1: 조건 (3)을 reflect 안에서 정의: last /sc:review round 뒤 리뷰된 코드나 shipped content를 바꾼 수정은 다른 round를 거쳤거나 사용자가 면제했다
- [x] Step 2: review-due 프로브에 "all three conditions hold" 거절 check. 성공 정규식의 `commit`은 `commit status: complete` 꼴로만
- [x] Step 3: 되돌림 문장: 수락되지 않은 red 또는 조건 (3) 실패만, 그 밖의 실패는 `complete` 그대로
- [x] Step 4: 앵커 넷(부정 "neither … nor", Proof 재실행 우회, 수락 규칙 둘)
- [x] Commit Phase 9: `fix: Plan-Close defines a fix waiting for review; review-due probe fails a closable verdict`

## Phase 10: 06f 반영 (one commit)

[06f-verify-round7](./06f-verify-round7.md)(Important 1, Suggestion 3). Important(조건문 "once all three hold"를 거절로 채점)와 Suggestion 3(목록 꼴 제안)은 510108c6이 이미 고쳤다. 06f의 문장 첫머리 정규식 대신 조건 낱말 lookbehind를 썼고, 저장된 run 마흔여덟 개로 쟀다(Deviations).

- [x] Step 1: Plan-Close (3)을 글자 그대로 성립하게: "has had a /sc:review round after it, or the user waived that round"
- [x] Step 2: Plan-Close 앵커 셋(Proof를 다시 돌리지 않음, 리뷰 대기 수정의 회송, "all three hold")
- [x] Step 3: Phase 9 Deviations의 review-due 수치는 510108c6의 재채점(22/23)으로 대체
- [x] Commit Phase 10: `fix: Plan-Close condition 3 reads literally; anchors for its routing`

## Integration (커밋 아님)

- [ ] 전체 suite, `make lint`, `ruff format --check`, `make typecheck`
- [ ] 독립 검증(headless opus)과 그 반영, Critical·Important가 없을 때까지
- [ ] 누더기 감사(소유자 지시 2026-10-22): v4.34.1 이후 미출하 작업 전체를 최종 상태로 다시 읽는 독립 감사(headless opus). 반복 수정으로 덧댄 문구, 중복, 예외, 검증기 맞춤 과적합을 찾는다. 보고서는 `docs/analysis/patchwork-audit-ajitta-2026-10-22.md`. 반영 뒤 다시 검증한다
- [ ] master 병합과 push. 릴리스는 하지 않는다

## Measurements

- 바꾸기 전(Phase 1 커밋 00607b12의 src, Linux, sonnet, low, 한 번씩, `$TMPDIR/pco/before/b1`): `implement-proof-fail` 6/6, `implement-proof-green` 3/5(계획과 README를 `complete`로 바꿔 두 check 실패, `Result:`는 녹색으로 적음), `reflect-plan-close` 5/5, `reflect-plan-close-review-due` 5/5. reflect 두 프로브는 바꾸기 전에도 통과한다: 옛 reflect는 상태를 쓰지 않았다. 두 프로브는 새 Plan-Close 단계가 headless에서 쓰지 않는지 지키는 회귀 check다.

## Deviations

- Phase 9 뒤 canary(c862806d, `$TMPDIR/pco/r9`): review-due 여섯 run 모두 올바르게 답했다(재리뷰를 지목하고 `complete`를 제안하지 않음). 그런데 새 거절 check가 둘을 떨어뜨렸다("Once all three conditions hold, I'll propose"). 조건문 뒤의 구절은 빼게 고쳤다. `reflect-plan-close` 하나는 올바른 제안("One docs-only commit that changes: `05-plan.md`: `status: complete`")이 동사 없이 떨어졌다. `` `status: complete` `` 꼴을 제안으로 센다. 저장된 run 마흔여덟 개로 다시 채점: 닫을 수 있는 답 23/23, review-due 22/23(떨어진 하나가 06e의 오독 run), 바꾸기 전 `reflect-plan-close` 0/1.

- Phase 9: 저장된 실제 run 서른여덟 개로 다시 채점(`reflect-plan-close*`): 닫을 수 있는 답 18/18 통과, review-due 답 17/18 통과이고 떨어진 하나가 06e의 오독 run(`r8/x3`)이다, 바꾸기 전 `reflect-plan-close` 0/1. 변이 9건 모두 red(`$TMPDIR/pco/mut9.py`).

- Phase 8: 06d 3의 거절 후보(부정어 `no`·`\w+n't`, 동사 commit·change·move)는 넣지 않았다. 저장된 실제 run 서른두 개로 다시 채점하자 올바른 제안 열여섯 중 열넷이 떨어졌다("No later code commits", "no feedback memories to propose", "haven't changed"). 검증자의 손으로 쓴 목록에서만 좋아진 패턴이다. 성공 쪽 동사만 넓히고 거절 쪽에는 `shouldn't` 하나를 더했다. 그 결과 저장된 run: 닫을 수 있는 계획의 답 15/15 통과, review-due 답(거절) 0/15 통과, 바꾸기 전 답 0/2 통과. 변이 7건 모두 red(`$TMPDIR/pco/mut8.py`, 되돌림 계기 앵커를 더한 뒤).

- Phase 7: 06c 4의 약화어 열세 개와 앵커 여섯은 넣지 않았다. 가드는 앵커가 있는 구절의 삭제, 목록 안 약화어, 되돌림 동사의 부정을 잡는다. 앵커 없는 절의 삭제는 잡지 않는다(06d M5, M12, M22). 문맥에 따른 약화("usually", "should")와 조건 덧붙임은 낱말 목록으로는 끝이 없고, round마다 검증자의 예를 목록에 더하는 것이 감사가 걷어낸 덧댐이다. 그 몫은 canary probe다.

- Phase 6: 06b가 제안한 거절 guard는 저장된 올바른 답 하나("did not re-run it, as the Plan-Close step says")를 거절로 읽었다. "Plan-Close"의 "Close"를 동사로 본 탓이다. 하이픈 뒤 낱말은 빼고, 그 답을 채점 테스트에 넣었다. 저장된 `reflect-plan-close` run 열 개를 다시 채점: 바꾼 뒤 9/9 통과, 바꾸기 전 1/1 실패. 변이 10건 모두 red(`$TMPDIR/pco/mut6.py`).

- Phase 4: review의 "with no claim that they are fixed"를 지웠다. inline round에서는 `RULES.md` Intent Propagation 포인터만 남는다(06b 6).
- Phase 5는 reflect의 조건 (2)만 바꾸고 같은 조건의 사본 넷을 그대로 두었다(06b 1). 규칙을 바꿀 때 사본을 함께 찾지 않은 탓이다. Phase 6에서 넷을 고치고 옛 문구 가드를 더했다.

- Phase 5 뒤 canary(e87f9aa0, `$TMPDIR/pco/r5/x3`): `reflect-plan-close`의 올바른 제안("sets `05-plan.md` to `status: complete`")이 성공 check에서 떨어졌다. 동사와 `complete` 사이의 파일 이름 점을 문장 끝으로 읽었다. 낱말 안의 점은 넘기게 고쳤다. 저장된 run 열 개를 다시 채점: 바꾼 뒤 9/9 통과, 바꾸기 전 1/1 실패.

- Phase 4에서 Deviations에 적지 않고 빠진 구절 둘(06a 10): "after the review, test and reflect gates"(Plan-Close 조건이 대신한다), 재리뷰 문장의 "before done"("goes back to /sc:review for another round"가 대신한다).

- 04-design B′ 표 6행의 "`Result:` 뒤 코드 커밋 → `/sc:test`"는 풀 수 없는 고리였다(06-verify 1, 감사 1). Phase 4에서 `/sc:implement --plan`(Proof 재실행, `Result:` 갱신)으로 바꿨다.
- 감사 재작성안의 implement 문장에서 "(linked from the phase file's header)", "`status: complete` with an open box is a defect", "before done is claimed again"이 빠졌다. 앞의 둘은 `test_plan_checklist.py`와 phase 파일 문장이 맡는다.

- Phase 1: 프로브와 채점 테스트를 한 번에 썼다. red는 `evals/tasks.yaml`을 HEAD로 되돌려 확인했다(4 failed).
- Phase 2: drift test의 단계 정규식이 `3.6.` 같은 하위 단계와 `Run (--through only):` 같은 괄호 라벨을 읽게 넓혔다. README `/sc:implement --plan` 행도 고정 대상에 넣었다.
- Phase 3의 CHANGELOG와 주석 편집은 Phase 2 커밋 바로 뒤 한 커밋이다.

## Risks

- reflect 프로브는 headless라 사용자 답이 없다. 쓰지 않는 쪽만 잴 수 있다. 쓰는 쪽(사용자 답 뒤)은 문구와 drift test로만 확인한다.
- 제안 문장을 재는 정규식은 언급만 본다(review-reflect-gates의 알려진 한계와 같다).
- core가 바뀐다. 다음 릴리스는 `canary-gates`와 `canary-commands`가 모두 필요하다.

## Alternatives not taken

- A(뜻만 적기), C(그대로), D(게이트 상자): [04-design](./04-design.md)과 [04a](./04a-design-verify.md).

## Proof

- `uv run pytest` → exit 0
- 새 프로브 셋과 `implement-proof-fail`, `test-reflect-gate`, `test-reflect-gate-complete`가 3회씩 통과(sonnet, low)
