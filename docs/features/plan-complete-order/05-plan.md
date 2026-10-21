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
- [ ] Commit Phase 4: `refactor: one statement per rule after the patchwork audit; Plan-Close sends to /sc:implement; --through left open`

## Integration (커밋 아님)

- [ ] 전체 suite, `make lint`, `ruff format --check`, `make typecheck`
- [ ] 독립 검증(headless opus)과 그 반영, Critical·Important가 없을 때까지
- [ ] 누더기 감사(소유자 지시 2026-10-22): v4.34.1 이후 미출하 작업 전체를 최종 상태로 다시 읽는 독립 감사(headless opus). 반복 수정으로 덧댄 문구, 중복, 예외, 검증기 맞춤 과적합을 찾는다. 보고서는 `docs/analysis/patchwork-audit-ajitta-2026-10-22.md`. 반영 뒤 다시 검증한다
- [ ] master 병합과 push. 릴리스는 하지 않는다

## Measurements

- 바꾸기 전(Phase 1 커밋 00607b12의 src, Linux, sonnet, low, 한 번씩, `$TMPDIR/pco/before/b1`): `implement-proof-fail` 6/6, `implement-proof-green` 3/5(계획과 README를 `complete`로 바꿔 두 check 실패, `Result:`는 녹색으로 적음), `reflect-plan-close` 5/5, `reflect-plan-close-review-due` 5/5. reflect 두 프로브는 바꾸기 전에도 통과한다: 옛 reflect는 상태를 쓰지 않았다. 두 프로브는 새 Plan-Close 단계가 headless에서 쓰지 않는지 지키는 회귀 check다.

## Deviations

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
