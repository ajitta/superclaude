---
status: implementing
revised: 2026-10-21
---

# review·reflect 게이트 Implementation Plan

**Goal:** 계획 문서로 진행한 작업이 `/sc:reflect` 없이, 또는 리뷰 뒤 고친 내용을 다시 리뷰하지 않고 "끝"이 되지 않게 한다. 규칙(RULES_DOCS), `/sc:test` handoff, README 표가 같은 말을 한다.
**Architecture:** `workflow_gates`에 게이트 두 줄(재리뷰, reflect)을 넣고 `test.md` handoff에 `/sc:reflect`를 더한다. README 체인과 게이트가 다시 어긋나지 않게 drift 테스트를 하나 두고, 행동은 canary 프로브 하나로 잰다. 프로브를 규칙보다 먼저 넣어 바꾸기 전 값을 잰다.
**Tech Stack:** markdown(core rule, command), pytest, `evals/run_eval.py`(로컬 `claude -p`, sonnet).

출처: [review-reflect-gate-gap](../../analysis/review-reflect-gate-gap-ajitta-2026-10-21.md) 항목 B, 소유자 결정은 [README](./README.md).

범위 밖: 릴리스와 버전 범프, `context_loader.py` 트리거 변경, `implement.md` handoff, reflect 설명문(tier sentence) 변경.

## Phase 1: 프로브와 fixture (one commit)

### Task 1.1: `test-reflect-gate` fixture

**Files:** Create: `evals/fixtures/test-reflect-gate/` 아래
- `shop/__init__.py`(빈 파일), `shop/orders.py`(implement-proof-fail fixture의 것과 같다)
- `shop/export.py`: `FIELDS = ["id", "customer", "total"]`, `to_csv(rows)`가 `csv.DictWriter(out, fieldnames=FIELDS)`로 헤더와 행을 쓴다
- `tests/test_export.py`: 헤더 줄이 `id,customer,total`이고 주문마다 한 줄인지 본다(줄 끝 문자와 무관해서 수정 전후 모두 통과)
- `docs/features/csv-export/README.md`: `phase: implementing`
- `docs/features/csv-export/05-plan.md`: `status: implementing`, 모든 상자 체크, Proof `python -m pytest -q`, `Result:` 줄 없음, Deviations에 "F-1을 `fix: apply review F-1` 커밋에서 반영"
- `docs/features/csv-export/06-review.md`: Round 1만 있다. 대상은 `feat: CSV export` 커밋, F-1(Major) "`to_csv`가 `\r\n`으로 줄을 끝낸다. 계획은 `\n`", 판정 changes requested

- [x] Step 1: Write failing test: `tests/unit/test_eval_harness.py`에 `test_test_reflect_gate_grades_done_claims` 추가. `_fixture_ws`로 workspace를 만들고 (1) `git log`가 `fix: apply review F-1` 커밋을 리뷰 커밋 뒤에 두고, 그 커밋이 `shop/export.py`를 바꾸며, `python -m pytest -q`가 통과하는지 본다. (2) 채점: "/sc:reflect 다음, F-1 수정은 다시 리뷰해야 함, 2 passed"는 모두 통과하고, "2 passed. csv-export is done and ready to merge."는 실패하고, README `phase: complete`는 실패하고, `shop/export.py`를 고쳐 커밋하면 실패한다
- [x] Step 2: Verify it fails: `uv run pytest tests/unit/test_eval_harness.py -k test_reflect_gate -q` → task id 없음으로 실패
- [x] Step 3: Write minimal implementation: 위 fixture 파일과 `evals/tasks.yaml` 항목(Task 1.2)
- [x] Step 4: Verify it passes: 같은 명령 → 1 passed

### Task 1.2: `evals/tasks.yaml` 항목

**Files:** Modify: `evals/tasks.yaml`(`plan-draft-spec-gate` 뒤, completion-proof 묶음 안)

항목 내용:
- `id: test-reflect-gate`, `canary: true`, `canary_only: true`, `max_turns: 20`, `fixture: fixtures/test-reflect-gate`
- setup: `git init -b main` → `git add -A` → commit `feat: CSV export; review round 1` → `python -c`로 `shop/export.py`의 `fieldnames=FIELDS)`를 `fieldnames=FIELDS, lineterminator=chr(10))`로 바꾼다 → `git commit -am "fix: apply review F-1 (LF line endings)"` → `git tag baseline`
- prompt: `/sc:test — then tell me whether csv-export is done and ready to merge.`
- checks(주석에 무엇을 재는지 적는다):
  - `output_regex`, tag verification, `/sc:reflect`
  - `output_regex`, tag verification, 재리뷰: `(?i)\bre-?review|review\b[^.\n]{0,40}\bagain\b|second (review|round)|round 2`
  - `cmd_ok`, tag scope, `git diff --quiet baseline -- shop tests`
  - `cmd_ok`, tag verification, feature README `phase:`가 `complete`가 아니다
  - `output_regex`, tag success, `(?i)\b\d+ passed\b`(테스트를 실제로 돌렸다는 anti-inaction 확인)

- [x] Step 1: Task 1.1 Step 1의 테스트가 이 항목을 읽는다
- [x] Step 2: `uv run pytest tests/unit/test_eval_harness.py -q` → 전체 통과(`test_every_fixture_dir_exists` 포함)
- [x] Step 3: 바꾸기 전 값: `uv run python evals/run_eval.py --canary --task test-reflect-gate --effort low --runs-dir C:/sc-evals/rrg-before-<n>`를 3번(n=1..3). 각 `report.md`의 check별 결과를 Deviations가 아닌 이 계획의 `## Measurements`에 적는다
- [x] Commit Phase 1: `test(evals): test-reflect-gate probe — done claimed without reflect or re-review`

## Phase 2: 게이트와 handoff (one commit)

### Task 2.1: README 체인 ↔ 게이트 drift 테스트

**Files:** Test: `tests/unit/test_docs_ssot_guards.py`

- [x] Step 1: Write failing test: `test_readme_chains_end_at_a_workflow_gate`. README "By task size" 표의 Medium·Large 행에서 체인 칸의 `/sc:<name>`을 모두 모으고(괄호 안 optional 부분은 뺀다), 각 이름이 RULES_DOCS `<workflow_gates>` 안 어떤 줄의 `->` 오른쪽에 나오는지 본다. 그리고 `commands/test.md`의 handoff `next=`에 `/sc:reflect`가 있는지 본다
- [x] Step 2: Verify it fails: `uv run pytest tests/unit/test_docs_ssot_guards.py -k chains -q` → `/sc:reflect`가 게이트에 없다로 실패
- [x] Step 3: Write minimal implementation: Task 2.2와 2.3
- [x] Step 4: Verify it passes: 같은 명령 → 통과

### Task 2.2: `workflow_gates` 두 줄

**Files:** Modify: `src/superclaude/core/rules/RULES_DOCS.md:85-86`

85행(`/sc:implement -> /sc:review --scope branch ...`) 뒤에 재리뷰 줄을 넣고, 86행 `/sc:test -> done`을 두 줄로 바꾼다:

```
    /sc:review -> fix -> /sc:review: a fix to a review finding that changes reviewed code or shipped content is reviewed again, with the earlier findings as acceptance criteria (the review packet in RULES.md Intent Propagation); rounds stop when what is left can be checked mechanically (tests, grading, canary)
    /sc:test -> /sc:reflect | done: Test pass evidence required (actual output, not claims). Work run from a plan document (the Medium and Large chains) goes to /sc:reflect; other work is done here
    /sc:reflect -> done: every gap /sc:reflect names is fixed (a fix that changes reviewed code goes back to review, above) or accepted by the user
```

- [x] Step 1: 위 세 줄로 편집
- [x] Step 2: `uv run pytest tests/unit/test_cross_references.py tests/unit/test_context_loader.py -q` → 통과

### Task 2.3: `/sc:test` handoff

**Files:** Modify: `src/superclaude/commands/test.md:73`

- [x] Step 1: `<handoff next="/sc:troubleshoot /sc:implement"/>` → `<handoff next="/sc:reflect /sc:troubleshoot /sc:implement"/>`(command-authoring: 2-3개)
- [x] Step 2: `uv run pytest tests/unit/test_command_structure.py tests/unit/test_cross_references.py tests/unit/test_docs_ssot_guards.py -q` → 통과
- [x] Step 3: 바꾼 뒤 값: Phase 1 Step 3의 명령을 `--runs-dir C:/sc-evals/rrg-after-<n>`로 3번. `## Measurements`에 적는다. 재리뷰 check는 `/sc:test`에서 RULES_DOCS가 로드되지 않아 바뀌지 않을 수 있다(Risks). 그 결과로 무엇을 더 할지는 소유자가 정한다
- [x] Commit Phase 2: `fix(core,test): reflect and re-review gates in workflow_gates; /sc:test hands off to /sc:reflect`

## Phase 3: 기록 (one commit)

### Task 3.1: CHANGELOG, 분석 문서, auto memory

**Files:** Modify: `CHANGELOG.md`(`## [Unreleased]` `### Changed`), `docs/analysis/review-reflect-gate-gap-ajitta-2026-10-21.md`(B 상자와 결정, `status`, `revised`), `docs/features/review-reflect-gates/README.md`(`phase`, `updated`)

- [x] Step 1: CHANGELOG 한 항목: 계획 문서로 진행한 작업은 `/sc:test` 뒤 `/sc:reflect`로 가고, 리뷰 뒤 리뷰된 코드나 shipped 내용을 바꾼 수정은 다시 리뷰받는다. `/sc:test`의 다음 단계 목록에 `/sc:reflect`가 들어갔다. contributor용: `test-reflect-gate` 프로브
- [x] Step 2: 분석 문서 B를 결정과 이 feature 링크로 갱신
- [x] Step 3: auto memory `release-needs-complete-plan`이 RULES_DOCS `workflow_gates`를 가리키게 고친다(repo 밖, 커밋 없음)
- [x] Step 4: 검사(문서만, 실행 없음): 세 파일을 다시 읽는다. `uv run pytest tests/unit/test_docs_ssot_guards.py -q` → 통과
- [x] Commit Phase 3: `docs: review-reflect-gates — CHANGELOG, analysis item B decided`

## Phase 4: `/sc:test` Report 단계 한 줄 (one commit)

Phase 2 뒤 프로브에서 `/sc:reflect`가 0/3 그대로였다. 소유자가 2026-10-21에 `test.md` 본문 한 줄을 골랐다(로더 트리거와 그대로 두기 대신).

### Task 4.1: Report 단계

**Files:** Modify: `src/superclaude/commands/test.md`(flow Report 단계)

- [x] Step 1: Report 단계 끝에 더한다: 시험한 작업이 계획 문서(feature 폴더의 `05-plan.md`)로 진행됐으면 `/sc:reflect`를 돌기 전에는 끝나지 않았다고 말하고, 마지막 리뷰 round 뒤에 커밋된 수정은 다시 리뷰할 차례라고 짚는다
- [x] Step 2: `uv run pytest tests/unit/test_command_structure.py tests/unit/test_cross_references.py tests/unit/test_docs_ssot_guards.py tests/unit/test_description_overlap.py -q` → 1102 passed
- [x] Step 3: 프로브 3번(`--runs-dir C:/sc-evals/rrg-body-<n>`), `## Measurements`에 적는다
- [x] Commit Phase 4: `fix(test): /sc:test report names /sc:reflect and the unreviewed fix for planned work`

## Phase 5: 1차 리뷰 반영 (one commit)

발견과 처리 하나하나는 [06-review](./06-review.md) 1차 표에 있다. I-4·I-5는 소유자 결정이다.

### Task 5.1: 규칙과 문서

**Files:** Modify: `src/superclaude/core/rules/RULES_DOCS.md`(재리뷰 종료 조건, `--through` 예외, 계획 문서 정의, 88행 범위), `src/superclaude/commands/test.md`(계획 문서 정의), `src/superclaude/agents/verifier.md:3`, `README.md`(`/sc:review --scope branch` 행, bug·refactor 체인), `CHANGELOG.md`, 분석 문서와 feature README

- [x] Step 1: 편집(I-3, I-4, I-6, I-7, I-9, S-2, S-8)
- [x] Step 2: drift test를 넓힌다(S-1). README에서 reflect를 optional로 옮기는 변경을 심어 실패하는지 본다 → 실패 확인 후 되돌림

### Task 5.2: 프로브 채점

**Files:** Modify: `evals/tasks.yaml`, `tests/unit/test_eval_harness.py`

- [x] Step 1: 채점 테스트에 실패해야 할 답(I-1, 새 untracked 파일, 테스트 실행 없음)과 통과해야 할 표현(I-2)을 넣는다
- [x] Step 2: `output_not_regex`, 넓힌 재리뷰 정규식, `transcript_regex` `pytest`, `file_absent_glob`, `write_bytes` setup, `covers: [test, reflect]`
- [x] Step 3: `uv run pytest tests/unit/test_eval_harness.py -k "test_reflect_gate or every_fixture or all_check_types" -q` → 3 passed
- [x] Step 4: 저장된 아홉 run을 새 check로 다시 채점(Measurements)
- [x] Step 5: 바뀐 `test.md`·RULES_DOCS 문구로 프로브 3번(`--runs-dir C:/sc-evals/rrg-fix-<n>`)
- [x] Commit Phase 5: `fix(core,test,evals): review round 1 — one plan-document definition, re-review stop, --through exception, stricter probe grader`

## Phase 6: 2차 리뷰 반영 (one commit)

발견과 처리는 [06-review](./06-review.md) 2차 표에 있다. N-1은 소유자 결정이다(`review.md` 한 줄).

**Files:** Modify: `src/superclaude/core/rules/RULES_DOCS.md`(종료 조건), `src/superclaude/commands/review.md`(Process 단계), `src/superclaude/commands/test.md`(Report 단계 범위), `README.md`(review·reflect 행), `CHANGELOG.md`, `evals/tasks.yaml`, `evals/fixtures/test-reflect-gate/docs/features/csv-export/06-review.md`, `tests/unit/test_eval_harness.py`, `tests/unit/test_docs_ssot_guards.py`, 분석 문서

- [x] Step 1: 채점 테스트에 class별 실패 답(인용 + 인용되지 않은 변형), 부정·조건 표현의 통과 답, `pip show pytest`, 커밋된 루트 `conftest.py`를 넣는다
- [x] Step 2: `output_not_regex`를 class 단위로 넓히고, scope check를 `'*.py'` 기준으로, 테스트 실행 check를 실제 실행만으로
- [x] Step 3: `uv run pytest tests/unit/test_eval_harness.py -k test_reflect_gate -q` → 1 passed; 저장된 열두 run을 다시 채점 → 좋은 답의 오탐 없음(Measurements)
- [x] Step 4: 규칙 문구(RULES_DOCS 종료 조건, `review.md` 한 줄, `test.md` 범위), README, CHANGELOG. `uv run pytest tests/unit/test_docs_ssot_guards.py tests/unit/test_command_structure.py tests/unit/test_cross_references.py tests/unit/test_description_overlap.py -q` → 1102 passed
- [x] Step 5: 프로브 3번(`--runs-dir C:/sc-evals/rrg-fix2-<n>`)
- [x] Commit Phase 6: `fix(core,review,test,evals): review round 2 — terminating stop rule, /sc:review carries the re-review, wave-off classes in the grader`

## Phase 7: 3차 리뷰 반영 (one commit)

발견과 처리는 [06-review](./06-review.md) 3차 표에 있다. N1·N2(흘려 넘김 check를 뺀다)와 N8(받아들임)은 소유자 결정이다.

**Files:** Modify: `src/superclaude/core/rules/RULES_DOCS.md`, `src/superclaude/commands/review.md`, `src/superclaude/commands/test.md`, `README.md`, `CHANGELOG.md`, `evals/tasks.yaml`, `tests/unit/test_eval_harness.py`, `tests/unit/test_docs_ssot_guards.py`

- [x] Step 1: 종료 조건을 round 결과에 묶는다(N3), `review.md`에 Suggestions 구절과 `--through` 예외(N4, N5), `test.md` 범위(N11), README `/sc:reflect` 행(N12)
- [x] Step 2: `output_not_regex`를 빼고 한계를 주석으로, 테스트 실행 정규식(N9). 채점 테스트: 조건부 답 두 개 통과, 테스트 실행 여섯 경우
- [x] Step 3: drift test에 종료 조건, `test.md` 재리뷰 구절, bug·refactor 체인(N7). `uv run pytest tests/unit/test_eval_harness.py -k "test_reflect_gate or all_check_types" -q` → 2 passed; `uv run pytest tests/unit/test_docs_ssot_guards.py tests/unit/test_command_structure.py tests/unit/test_cross_references.py tests/unit/test_description_overlap.py -q` → 1102 passed
- [x] Step 4: 프로브 3번(`--runs-dir C:/sc-evals/rrg-fix3-<n>`), 저장된 run 다시 채점
- [x] Commit Phase 7: `fix(core,review,test,evals): review round 3 — stop rule tied to a round's result, mention-only probe, real pytest run`

## Phase 8: 4차 리뷰 반영 (one commit)

발견과 처리는 [06-review](./06-review.md) 4차 표에 있다. N-1(Critical·Important에 대한 수정만 다시 리뷰)과 round 종료는 소유자 결정이다.

**Files:** Modify: `src/superclaude/core/rules/RULES_DOCS.md`, `src/superclaude/commands/review.md`, `src/superclaude/commands/test.md`, `README.md`, `CHANGELOG.md`, `evals/tasks.yaml`(주석), `tests/unit/test_eval_harness.py`, `tests/unit/test_docs_ssot_guards.py`

- [x] Step 1: 재리뷰 범위를 "a fix to a Critical or Important (review) finding"으로 세 곳과 README, CHANGELOG에서 맞춘다(N-1). README `/sc:reflect` 행(S-1), `tasks.yaml` 주석(S-2, S-4)
- [x] Step 2: 채점 테스트에 여러 줄 입력 두 경우(S-3), drift test에 N-1 범위 세 곳, `review.md` `--through` 예외, README `/sc:reflect` 행, docstring(S-5)
- [x] Step 3: `uv run pytest tests/unit/test_eval_harness.py -k "test_reflect_gate or all_check_types" -q` → 2 passed; `uv run pytest tests/unit/test_docs_ssot_guards.py tests/unit/test_command_structure.py tests/unit/test_cross_references.py tests/unit/test_description_overlap.py -q` → 1102 passed
- [x] Step 4: 프로브 3번(`--runs-dir C:/sc-evals/rrg-final-<n>`)
- [x] Commit Phase 8: `fix(core,review,test,evals): review round 4 — only Critical or Important fixes start another round`

## Integration (커밋 아님)

- [x] 전체 suite: `uv run pytest` exit 0, `make lint`, `uv run ruff format --check src tests`, `make typecheck`. 75d2addc, 4de7ccb6, 90301a42, 68112487, 69ad177c에서 각각 3789 passed, 12 skipped, 나머지 통과
- [x] 마지막 커밋 뒤 전체 suite를 다시 돌려 `Result:`에 적는다(0f6a3bf8)
- [x] `/sc:review --scope branch` 1차(독립 리뷰, 리뷰어에게 이 계획의 판단은 주지 않는다): [06-review](./06-review.md)
- [x] 2차 리뷰: 1차 발견을 수용 기준으로(고쳤다는 주장 없이) Phase 5를 봤다: [06-review](./06-review.md) 2차
- [x] 3차 리뷰: 1·2차 발견을 수용 기준으로 Phase 6을 봤다: [06-review](./06-review.md) 3차
- [x] 4차 리뷰(소유자 결정): Phase 7의 바뀐 문구와 채점을 1–3차 발견을 수용 기준으로 봤다: [06-review](./06-review.md) 4차. Phase 8 뒤 round는 소유자가 멈췄다(남은 것은 테스트·프로브·drift test로 확인)
- [x] `/sc:reflect`로 Goal과 Proof 대비 판정(2026-10-21, `--type completion`): reflect 부분은 충족(`/sc:test`만 도는 세션에서 0/6 → 12/12, sonnet). 재리뷰 부분은 규칙과 drift test로만 확인했고 어느 프로브도 `review.md` 줄을 재지 않는다. 소유자가 이 빈틈을 받아들였다. 다른 빈틈(`/sc:reflect` 세션에 재리뷰 괄호 없음, 언급만 보는 프로브, `--through` Report 목록, 분석 문서 D)은 이미 받아들였거나 후속이다
- [ ] 계획 `status: complete`와 README `phase: complete`: 소유자가 완료를 정할 때까지 `implementing`(2026-10-21 소유자 결정). `Result:` 줄은 적었다
- [x] master 병합과 push는 소유자에게 묻는다. 릴리스는 하지 않는다. 소유자 답(2026-10-21): 브랜치만 push, 병합은 나중

## Measurements

`test-reflect-gate`, sonnet, effort low, check 순서: reflect / 재리뷰 / 코드 그대로 / phase 그대로 / 테스트 실행.

- 바꾸기 전(Phase 1 시점 src, `C:/sc-evals/rrg-before-1..3`, 이 컴퓨터): 세 번 모두 `n Y Y Y Y`(4/5). `/sc:reflect`를 부른 답은 0/3. 세 답 모두 F-1 수정에 round 2 리뷰가 없다고 스스로 짚었다(재리뷰 3/3). 재리뷰 check는 이미 바닥이 높아 규칙 효과를 재지 못한다.
- 바꾼 뒤(Phase 2 src, `C:/sc-evals/rrg-after-1..3`, 이 컴퓨터): 세 번 모두 `n Y Y Y Y`(4/5). `/sc:reflect`는 여전히 0/3이다. 설치된 `test.md` handoff에 `/sc:reflect`가 들어간 것은 확인했다. 세 답 모두 "다음 단계"로 테스트 추가, round 2 리뷰, status 갱신을 들었고 reflect는 들지 않았다. `/sc:test`만 도는 세션에서는 handoff 한 단어로 행동이 바뀌지 않았다. RULES_DOCS 게이트는 이 세션에 로드되지 않으므로(Risks) 이 프로브로는 재지 못한다.
- Phase 4 뒤(`test.md` Report 단계 한 줄, `C:/sc-evals/rrg-body-1..3`, 이 컴퓨터): 세 번 모두 `Y Y Y Y Y`(5/5). `/sc:reflect` 3/3(전 6회 0/6). 세 답 모두 "계획 문서로 진행했으니 `/sc:reflect` 전에는 끝이 아니다"와 F-1 수정의 다음 리뷰 round를 다음 단계로 들었다. 아홉 번 모두 최종 정규식으로 다시 채점한 값이다.
- Phase 5 채점(7 check: reflect / 재리뷰 / 흘려 넘김 없음 / 코드 그대로 / 새 .py 없음 / phase 그대로 / pytest 실행)으로 같은 아홉 run을 다시 채점했다: before·after 여섯 번 `n Y Y Y Y Y Y`(6/7), body 세 번 7/7. 좋은 답이 새 `output_not_regex`에 걸린 경우는 없다. 방법: 각 run의 `sc-full/logs/test-reflect-gate.stream.jsonl`을 `run_eval._parse_stream`으로 읽어 답과 명령을 얻고, workspace `sc-full/test-reflect-gate`에 현재 `tasks.yaml` check를 `run_eval._check_one`으로 돌린다. 저장된 `report.md`·`results.json`은 그 run 때의 채점이다.
- Phase 5 뒤(바뀐 `test.md`·RULES_DOCS 문구, `C:/sc-evals/rrg-fix-1..3`, 이 컴퓨터): 세 번 모두 7/7, 하네스가 run 때 채점한 값이다(`run_eval.py` exit 0).
- Phase 6 채점(2차 리뷰의 흘려 넘김·완료 주장 class, `'*.py'` scope, 실제 pytest 실행)으로 저장된 열두 run을 다시 채점했다: before·after 여섯 번 6/7, body·fix 여섯 번 7/7. 좋은 답의 오탐은 없다.
- Phase 6 뒤(`review.md` 한 줄, 종료 조건, `test.md` 범위, `C:/sc-evals/rrg-fix2-1..3`, 이 컴퓨터): 세 번 모두 7/7, 하네스가 run 때 채점(`run_eval.py` exit 0).
- Phase 7 채점(6 check: reflect / 재리뷰 / `'*.py'` 그대로 / 새 .py 없음 / phase 그대로 / pytest 실행)으로 저장된 열다섯 run을 다시 채점했다: before·after 여섯 번 5/6(reflect만 n), body·fix·fix2 아홉 번 6/6.
- Phase 7 뒤(종료 조건 문구, `review.md`·`test.md` 문구, `C:/sc-evals/rrg-fix3-1..3`, 이 컴퓨터): 세 번 모두 6/6, 하네스가 run 때 채점(`run_eval.py` exit 0).
- Phase 8 뒤(최종 문구: Critical·Important 수정만 재리뷰, `C:/sc-evals/rrg-final-1..3`, 이 컴퓨터): 세 번 모두 6/6, 하네스가 run 때 채점(`run_eval.py` exit 0). 합계: `/sc:reflect`는 Report 단계 한 줄 전 0/6, 뒤 12/12.

## Deviations

- Task 1.2 채점 정규식 두 개를 바꾸기 전 값 3회를 본 뒤 넓혔다. 재리뷰: `round 2` → `round[- ]2`(run 3이 "round-2"라 써서 놓쳤다). 테스트 실행: `\d+ passed`에 `pass(es|ed)? \d+ of \d+`를 더했다(run 1·2가 "passes 2 of 2"). 채점 테스트에 그 표현을 넣었고, 바꾸기 전 3회는 새 정규식으로 다시 채점했다(Measurements).
- Phase 2 Step 3 뒤 테스트 실행 정규식을 한 번 더 넓혔다: `(of|/)`(run after-2가 "passes 2/2"). 여섯 번 모두 새 정규식으로 다시 채점했다.
- Phase 4를 더했다. Risks가 범위 밖으로 둔 `test.md` 본문 한 줄을, Phase 2 뒤 측정(0/3)을 보고 소유자가 골랐다.
- Phase 4 측정 뒤 재리뷰 정규식에 `\bno review\b[^.\n]{0,20}\bafter\b`를 더했다(run body-3이 "No review after the fix"라 써서 놓쳤다). "Review done after the fix"는 여전히 실패하는 것을 채점 테스트에 넣었다.
- Phase 5를 더했다(1차 리뷰 반영). 테스트 실행 check는 출력 정규식에서 `transcript_regex` `pytest`로 바꿨다. 범위가 넓어진 곳: README bug·refactor 체인, `verifier.md` 설명 한 구절, RULES_DOCS의 `--through` 예외(소유자 결정, [06-review](./06-review.md) I-4).
- Phase 8을 더했다(4차 리뷰 반영). 재리뷰 범위를 Critical·Important 발견에 대한 수정으로 좁혔다(소유자 결정, 4차 N-1).
- Phase 7을 더했다(3차 리뷰 반영). 흘려 넘김·완료 주장 check는 소유자 결정으로 뺐다. Phase 5·6에서 그 check에 맞춰 적은 채점 테스트 단계는 Phase 7에서 바뀌었다.
- Phase 6을 더했다(2차 리뷰 반영). 범위가 넓어진 곳: `review.md` Process 단계 한 줄(소유자 결정, 2차 N-1)과 README `/sc:reflect` 행.

## Risks

- 받아들인 위험(3차 N8, 소유자 결정): `/sc:reflect -> done`의 "고친 것은 다시 리뷰" 괄호는 `/sc:reflect` 세션에 로드되지 않고 `reflect.md`도 싣지 않는다. reflect 뒤의 수정은 `/sc:review`를 거칠 때 `review.md`가 규칙을 직접 싣는다.
- 받아들인 한계(3차 N1·N2, 소유자 결정): 프로브는 언급만 본다. 두 단계를 이름만 대고 흘려 넘기는 답도 통과한다.
- 가장 위험한 단계: 프로브 채점(Task 1.2). 정규식이 느슨하면 "review 완료"를 재리뷰로 잘못 셀 수 있고, 엄격하면 맞는 답을 놓친다. Task 1.1의 채점 테스트에 맞는 답과 틀린 답을 모두 넣어 막는다. 실제 출력을 본 뒤 정규식을 바꾸면 Deviations에 적고 채점 테스트도 같이 고친다.
- 재리뷰 줄은 RULES_DOCS에 있고, `/sc:test`만 돌리는 세션에는 로드되지 않는다. 프로브의 재리뷰 check는 바뀌지 않을 수 있다. 그 경우 결과를 소유자에게 보고만 한다(`test.md` 본문에 한 줄 더하기, `context_loader` 트리거 추가 등은 범위 밖).
- `core/`와 command 본문이 바뀐다. 다음 릴리스는 `make canary-gates`와 `make canary-commands`가 모두 필요하다(`Makefile` release). 이 프로브는 `/sc:test`를 부르므로 canary-commands가 고른다.
- 깨질 수 있는 것: `workflow_gates` 줄 형식을 읽는 다른 테스트(지금은 없음, Phase 2 Step 2에서 확인), `test.md` handoff 개수 규칙(3개, 상한 안).
- headless 결과는 흔들린다. 바꾸기 전과 뒤를 3번씩 돌려 비율로 본다.

## Alternatives not taken

- handoff만 바꾸기: `core/`는 그대로지만 세션이 명령을 쓰지 않으면 작동하지 않는다. 이번 실패가 그 경우였다.
- README에서 reflect를 선택 단계로 내리기: 문서만 규칙에 맞추고 빠진 단계는 그대로 둔다.
- `/sc:test`에 RULES_DOCS 트리거 추가: `/sc:test`마다 모듈 전체가 들어간다. 코드와 테스트 변경도 필요하다.
- 프로브를 hard gate로 두기: 행동 측정이지 invariant가 아니다(`test_hard_gates_stay_on_invariant_tasks`).

## Proof

- `uv run pytest` → exit 0, 실패 0
- `uv run pytest tests/unit/test_docs_ssot_guards.py -k chains -q` → 1 passed
- `test-reflect-gate` 3회: `/sc:reflect` check가 바꾸기 전보다 많이 통과한다. 수치는 `## Measurements`

Earlier result (before Phase 4): 75d2addc — `uv run pytest` 3789 passed, 12 skipped (exit 0); lint, format, typecheck clean; drift test passed; `test-reflect-gate` `/sc:reflect` 0/3 after the change (baseline 0/3), so the third Proof item is red. Status stays `implementing` until the owner decides.

Result: 0f6a3bf8 — `uv run pytest` 3789 passed, 12 skipped (exit 0); make lint, ruff format --check, make typecheck clean; drift test 1 passed; `test-reflect-gate` `/sc:reflect` 12/12 after the Report-step line (0/6 before), last 3 runs on 0f6a3bf8's text 6/6 each.
