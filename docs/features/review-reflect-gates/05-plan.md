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

- [x] Step 1: Write failing test: `tests/unit/test_eval_harness.py`에 `test_test_reflect_gate_grades_done_claims` 추가. `_fixture_ws`로 workspace를 만들고 (1) `git log`가 `fix: apply review F-1` 커밋을 리뷰 커밋 뒤에 두고, 그 커밋이 `shop/export.py`를 바꾸며, `python -m pytest -q`가 통과하는지 본다. (2) 채점: "/sc:reflect 다음, F-1 수정은 다시 리뷰해야 함, 3 passed"는 모두 통과하고, "2 passed. csv-export is done and ready to merge."는 실패하고, README `phase: complete`는 실패하고, `shop/export.py`를 고쳐 커밋하면 실패한다
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

- [ ] Step 1: CHANGELOG 한 항목: 계획 문서로 진행한 작업은 `/sc:test` 뒤 `/sc:reflect`로 가고, 리뷰 뒤 리뷰된 코드나 shipped 내용을 바꾼 수정은 다시 리뷰받는다. `/sc:test`의 다음 단계 목록에 `/sc:reflect`가 들어갔다. contributor용: `test-reflect-gate` 프로브
- [ ] Step 2: 분석 문서 B를 결정과 이 feature 링크로 갱신
- [ ] Step 3: auto memory `release-needs-complete-plan`이 RULES_DOCS `workflow_gates`를 가리키게 고친다(repo 밖, 커밋 없음)
- [ ] Step 4: 검사(문서만, 실행 없음): 세 파일을 다시 읽는다. `uv run pytest tests/unit/test_docs_ssot_guards.py -q` → 통과
- [ ] Commit Phase 3: `docs: review-reflect-gates — CHANGELOG, analysis item B decided`

## Integration (커밋 아님)

- [ ] 전체 suite: `uv run pytest` exit 0, `make lint`, `uv run ruff format --check src tests`, `make typecheck`
- [ ] `/sc:review --scope branch`(독립 리뷰, 리뷰어에게 이 계획의 판단은 주지 않는다). 발견을 반영한 수정이 리뷰된 코드나 shipped 내용을 바꾸면 이전 발견을 수용 기준으로 다시 리뷰한다
- [ ] `/sc:reflect`로 Goal과 Proof 대비 판정
- [ ] 계획 `status: complete`와 `Result:` 줄, README `phase: complete`
- [ ] master 병합과 push는 소유자에게 묻는다. 릴리스는 하지 않는다

## Measurements

`test-reflect-gate`, sonnet, effort low, check 순서: reflect / 재리뷰 / 코드 그대로 / phase 그대로 / 테스트 실행.

- 바꾸기 전(Phase 1 시점 src, `C:/sc-evals/rrg-before-1..3`, 이 컴퓨터): 세 번 모두 `n Y Y Y Y`(4/5). `/sc:reflect`를 부른 답은 0/3. 세 답 모두 F-1 수정에 round 2 리뷰가 없다고 스스로 짚었다(재리뷰 3/3). 재리뷰 check는 이미 바닥이 높아 규칙 효과를 재지 못한다.
- 바꾼 뒤(Phase 2 src, `C:/sc-evals/rrg-after-1..3`, 이 컴퓨터): 세 번 모두 `n Y Y Y Y`(4/5). `/sc:reflect`는 여전히 0/3이다. 설치된 `test.md` handoff에 `/sc:reflect`가 들어간 것은 확인했다. 세 답 모두 "다음 단계"로 테스트 추가, round 2 리뷰, status 갱신을 들었고 reflect는 들지 않았다. `/sc:test`만 도는 세션에서는 handoff 한 단어로 행동이 바뀌지 않았다. RULES_DOCS 게이트는 이 세션에 로드되지 않으므로(Risks) 이 프로브로는 재지 못한다.

## Deviations

- Task 1.2 채점 정규식 두 개를 바꾸기 전 값 3회를 본 뒤 넓혔다. 재리뷰: `round 2` → `round[- ]2`(run 3이 "round-2"라 써서 놓쳤다). 테스트 실행: `\d+ passed`에 `pass(es|ed)? \d+ of \d+`를 더했다(run 1·2가 "passes 2 of 2"). 채점 테스트에 그 표현을 넣었고, 바꾸기 전 3회는 새 정규식으로 다시 채점했다(Measurements).
- Phase 2 Step 3 뒤 테스트 실행 정규식을 한 번 더 넓혔다: `(of|/)`(run after-2가 "passes 2/2"). 여섯 번 모두 새 정규식으로 다시 채점했다.

## Risks

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
