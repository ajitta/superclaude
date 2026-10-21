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

- [ ] Step 1: Write failing test: `test_implement_proof_fail_grades_status_against_the_red_proof`에 계획 Proof 아래 `Result:` 줄이 없으면, 녹색을 주장하면, "(accepted by user)"가 붙으면 실패하는 경우를 넣는다
- [ ] Step 2: Verify it fails: `uv run pytest tests/unit/test_eval_harness.py -k proof_fail -q`
- [ ] Step 3: check 추가: 계획 파일의 `Result:` 줄이 실패를 적는다(`fail|red|error`)
- [ ] Step 4: Verify it passes

### Task 1.2: `implement-proof-green`

**Files:** Modify: `evals/tasks.yaml`, `tests/unit/test_eval_harness.py`

- [ ] Step 1: Write failing test: `implement-proof-fail` fixture에서 legacy 테스트를 지운 workspace(녹색 Proof). 계획이 `complete`이면, README가 `complete`이면, `Result:`가 없으면 실패하고, `implementing` + `Result:` + 작업 완료면 통과
- [ ] Step 2: Verify it fails (task id 없음)
- [ ] Step 3: task 추가(`canary: true`, `canary_only: true`, `covers: [implement]`)
- [ ] Step 4: Verify it passes

### Task 1.3: `reflect-plan-close`와 `reflect-plan-close-review-due`

**Files:** Modify: `evals/tasks.yaml`, `tests/unit/test_eval_harness.py`

- [ ] Step 1: Write failing test: `test-reflect-gate` fixture 위에 (a) fix 커밋, `Result:` 줄(계획은 `implementing`), 리뷰 Round 2(Critical·Important 없음)를 둔 workspace와 (b) Round 2가 없는 workspace. 둘 다 계획·README가 그대로이고 `.py`가 바뀌지 않아야 통과. (a)는 `complete` 제안을 말해야, (b)는 다음 리뷰를 말해야 통과
- [ ] Step 2: Verify it fails
- [ ] Step 3: task 둘 추가(`covers: [reflect]`)
- [ ] Step 4: Verify it passes
- [ ] Step 5: 바꾸기 전 값: 새 프로브 셋을 지금 src로 한 번씩(sonnet, low). 05a 대신 이 계획의 Measurements에 적는다
- [ ] Commit Phase 1: `test(evals): implement-proof-green, reflect-plan-close probes; proof-fail reads the Result line`

## Phase 2: shipped 문구 (one commit)

**Files:** Modify: `src/superclaude/commands/implement.md`(Integrate), `src/superclaude/commands/reflect.md`(새 Plan-Close 단계, bounds), `src/superclaude/commands/intent.md`(Run, Report), `src/superclaude/core/rules/RULES_DOCS.md:58,88`, `README.md`(표 두 행, `--through` 문단), `tests/unit/test_docs_ssot_guards.py`(`_GATE_PHRASES`)

- [ ] Step 1: Write failing test: `_GATE_PHRASES`에 implement(녹색 Proof 뒤 `implementing`, 되돌림), reflect Plan-Close 세 조건과 사용자 답, intent Run·Report, RULES_DOCS 작성자 표기
- [ ] Step 2: Verify it fails: `uv run pytest tests/unit/test_docs_ssot_guards.py -k gate -q`
- [ ] Step 3: 문구 편집
- [ ] Step 4: Verify it passes; `uv run pytest tests/unit/test_command_structure.py tests/unit/test_cross_references.py tests/unit/test_description_overlap.py tests/unit/test_docs_ssot_guards.py -q`
- [ ] Commit Phase 2: `fix(core,implement,reflect,intent): a plan becomes complete on the user's yes to /sc:reflect, not on a green Proof`

## Phase 3: 기록 (one commit)

**Files:** Modify: `CHANGELOG.md`(`[Unreleased]` Changed + upgrade note, 거짓이 된 문장), `evals/tasks.yaml`·`tests/unit/test_eval_harness.py`의 거짓이 된 주석과 docstring, 분석 문서 D, feature README

- [ ] Step 1: 편집
- [ ] Step 2: `make canary-commands BASE=<merge-base>`와 새 프로브 셋 3회씩, Measurements에 적는다
- [ ] Commit Phase 3: `docs: plan-complete-order — CHANGELOG, upgrade note, measurements`

## Integration (커밋 아님)

- [ ] 전체 suite, `make lint`, `ruff format --check`, `make typecheck`
- [ ] 독립 검증(headless opus)과 그 반영, Critical·Important가 없을 때까지
- [ ] master 병합과 push. 릴리스는 하지 않는다

## Measurements

## Deviations

## Risks

- reflect 프로브는 headless라 사용자 답이 없다. 쓰지 않는 쪽만 잴 수 있다. 쓰는 쪽(사용자 답 뒤)은 문구와 drift test로만 확인한다.
- 제안 문장을 재는 정규식은 언급만 본다(review-reflect-gates의 알려진 한계와 같다).
- core가 바뀐다. 다음 릴리스는 `canary-gates`와 `canary-commands`가 모두 필요하다.

## Alternatives not taken

- A(뜻만 적기), C(그대로), D(게이트 상자): [04-design](./04-design.md)과 [04a](./04a-design-verify.md).

## Proof

- `uv run pytest` → exit 0
- 새 프로브 셋과 `implement-proof-fail`, `test-reflect-gate`, `test-reflect-gate-complete`가 3회씩 통과(sonnet, low)
