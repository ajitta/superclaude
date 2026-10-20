---
status: complete
revised: 2026-10-20
---

# 독립 검증 2차: `v4.33.0..HEAD` (4.33.1 + 미릴리스 `97cbac42`)

**판정: PASS WITH FIXES** — Critical 없음. 4.33.1이 06a 발견 8개를 반영했다는 주장과 probe v2 변이표는 재현됐다. 릴리스 게이트의 pathspec도 레시피 셸(dash)에서 제대로 동작한다. 다만 `make canary-commands`는 picker가 실패해도 "해당 프로브 없음"을 출력하고 exit 0으로 끝난다. picker는 명령을 `skill_called` 패턴으로만 가리키는 프로브(`cmd-delegated-load`, `cmd-delegated-git`)를 고르지 못한다. 그래서 새 게이트에는 잘못된 녹색 경로가 두 개 있다.

## 재현한 것

- 게이트(이 워크트리, `uv venv && uv pip install -e ".[dev]"`, `superclaude.__file__`이 워크트리 `src/`인지 확인):
  - `uv run pytest`: `3758 passed, 3 skipped in 100.24s`, exit 0
  - `make lint`: `All checks passed!`
  - `make typecheck`: `Success: no issues found in 54 source files`
  - `ruff format --check src tests`: `222 files already formatted`
  - `ruff check src tests`: 통과. `evals/changed_command_probes.py`도 ruff check와 format 모두 통과
- 카나리 게이트 질문:
  - `git diff v4.33.1 HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json`: 비어 있다. `make canary-gates`는 필요 없다.
  - `v4.33.0..v4.33.1`에는 `RULES_DOCS.md` 한 파일(2줄)만 바뀌었다. 06b가 4.33.1 전에 `canary-gates`를 돌렸다고 한 것과 맞는다.
  - `git diff --name-only v4.33.1 HEAD -- src/superclaude/commands`: `plan.md`. 따라서 다음 릴리스에서는 새 명령 게이트가 걸린다.
  - `uv run python evals/changed_command_probes.py v4.33.1`의 출력은 `--task plan-draft-spec-gate --task intent-through-branch`다. 인자 없이 실행해도 같다. 브랜치를 커밋한 뒤에도 바뀌지 않는다. 이 보고서는 `docs/`만 건드리기 때문이다.
- 주장 1(4.33.1이 06a를 반영했는지): 발견 1-8의 수정이 모두 `intent.md:17,19-21,25,79,85-86`, `RULES_DOCS.md:56,78`, `README.md:348`, `docs/index.html:340`, `CHANGELOG.md` [4.33.1]에 들어 있다. 빠진 것은 두 가지다. 06a 발견 2의 "깨끗한 작업 트리" 검사(아래 7번)와, 갱신되지 않은 gotcha 두 줄(아래 5번)이다.
- 주장 2(probe v2): 재현 스크립트는 `verify-scratch2/scripts/mutate_probe.py`다. run_eval과 같은 방식으로 fixture를 복사하고 `WS_GITIGNORE`와 setup을 적용한 뒤 `cmd_ok` 8개를 `_check_one`으로 돌렸다. 06b 변이표 12행이 한 칸도 다르지 않게 재현됐다. 추가로 만든 행은 다음과 같다.

| 끝 상태 | no push | main | branch | todos | code | Done when | Result | tests+overdue |
|---|---|---|---|---|---|---|---|---|
| 태그 push | FAIL | pass | pass | pass | pass | pass | pass | pass |
| 테스트 삭제 | pass | pass | pass | pass | pass | pass | pass | FAIL (pytest rc 5) |
| **마지막 단계(`06-reflect.md`) 미커밋** | pass | pass | pass | pass | pass | pass | pass | pass |
| **`overdue`가 모든 todo를 출력, rc 0** | pass | pass | pass | pass | pass | pass | pass | pass |

- 주장 3(릴리스 게이트, 항목 A): `Makefile:125-130`의 게이트 줄을 그대로 잘라 throwaway Makefile(`verify-scratch2/Gate.mk`)에 넣었다. `echo GATE_PASS`로 끝나게 했고, 가짜 태그를 단 scratch clone에서 같은 GNU Make 4.3과 `/bin/sh`(dash)로 실행했다. 결과는 다음과 같다.

| 태그 이후 변경 | 결과 |
|---|---|
| 실제 HEAD (`v4.33.1..97cbac42`, `plan.md`) | ❌ a command body changed since v4.33.1, exit 2 |
| 변경 없음 | GATE_PASS |
| `commands/README.md`만 | GATE_PASS |
| `commands/__init__.py`만 | GATE_PASS |
| `docs/index.html` + `agents/verifier.md` | GATE_PASS |
| `commands/test.md` | ❌ command body, exit 2 |
| 같은 경우 + `CANARY_OK=1`(환경 변수 또는 make 변수) | GATE_PASS |
| `core/RULES.md` | ❌ core/ or hooks.json (기존 게이트, 먼저 걸림) |
| 태그 없음 (orphan) | ❌ no v* tag reachable; `CANARY_OK=1`이면 통과 |

  `$$(…)` 안의 작은따옴표 `':!…'`도 dash에서 정상적으로 exclude pathspec으로 처리된다. `make release`는 실행하지 않았다.

- `make canary-commands`: 레시피의 `run_eval.py` 호출을 `echo WOULD_RUN`으로 바꾼 사본(`CC.mk`)으로 확인했다.
  - HEAD: `WOULD_RUN --canary --task plan-draft-spec-gate --task intent-through-branch`
  - README만 바뀌었거나 프로브가 없는 `index-repo.md`가 바뀐 경우: "No canary probe invokes …", exit 0. 의도한 동작이다.
  - 태그가 없는 경우: 아래 1번.
- 주장 3(plan.md): Save 단계의 문장은 `plan.md:18`에 있다. 상태 선택은 맞다(항목 B, 아래 3번 참고).
- 주장 3(새 테스트, 항목 D): 아래 6번. 변이 15개를 워크트리에서 하나씩 적용했다. 매번 `uv run pytest tests/unit/test_eval_harness.py`(64개)를 돌린 뒤 `git checkout --`으로 되돌렸다. 마지막 `git diff --stat`은 비어 있었다.

## 발견 사항

### 1. [Important] `make canary-commands`가 picker 오류를 "해당 프로브 없음"으로 바꿔서 성공 처리한다

- 근거:
  - `Makefile:70`은 `ARGS=$$(uv run python evals/changed_command_probes.py); if [ -z "$$ARGS" ]; then echo "No canary probe invokes …"`이다. 종료 코드를 보지 않는다.
  - `changed_command_probes.py:56-62`는 `git describe … check=True`로 실행된다. 태그가 없으면 `CalledProcessError`가 난다.
- 재현: scratch clone의 orphan 브랜치(태그 없음, 스크립트 있음)에서 실행하면 traceback이 나온 뒤 `No canary probe invokes the commands changed since the last v* tag.`가 출력되고 `rc=0`으로 끝난다. 얕은 clone, `git fetch --tags`를 하지 않은 clone, 잘못된 BASE에서도 같다.
- 영향: `make release`는 태그가 없으면 따로 거부한다(`Makefile:126`). 하지만 그 메시지의 처방은 "`canary-gates`, then `CANARY_OK=1`"이다. 사용자가 `canary-commands`를 돌리면 "해당 프로브 없음"이 나오므로, 아무 프로브도 돌리지 않은 채 `CANARY_OK=1`로 넘어갈 수 있다.
- 수정:
  - `Makefile:70`을 `@ARGS=$$(uv run python evals/changed_command_probes.py) || exit 1; \`로 바꾼다.
  - 스크립트의 `main()`은 `CalledProcessError`를 잡아서 stderr에 "no v* tag reachable (git fetch --tags?)"를 쓰고 `return 2`로 끝내게 한다.
  - 같은 오류 경로를 확인하는 테스트를 추가한다(6번).

### 2. [Important] picker가 Skill 호출로만 명령을 가리키는 프로브를 고르지 못한다

- 근거: `probes_for`(`changed_command_probes.py:37-50`)는 prompt의 `/sc:<name>`과 `covers:`만 본다. 실행 결과는 다음과 같다.
  - `probes_for({"load"}) == []`, `probes_for({"git"}) == []`
  - 그런데 `cmd-delegated-load`(`tasks.yaml:888`, prompt `/session-start`, check `skill_called ^sc:load$`)와 `cmd-delegated-git`(`tasks.yaml:901`, `^sc:git$`)는 바로 그 명령의 description을 시험하는 프로브다. `tasks.yaml:879-887`의 주석도 "Every /sc: command is model-invocable …"이라고 설명한다.
  - `probes_for({"plan"})`도 `plan-routing`(`tasks.yaml:144`)과 `cmd-lookalike-plan`(`:916`)을 고르지 않는다. 이 둘은 `plan.md` description의 라우팅을 본다.
- 실패 시나리오: `load.md`나 `git.md`의 description 한 줄을 바꾸는 릴리스를 생각해 보자. 게이트가 걸리고 `canary-commands`는 "No canary probe"를 출력한다. 그러면 사용자는 `CANARY_OK=1`로 릴리스한다. 그 변경을 잡도록 만든 프로브는 한 번도 돌지 않는다. AGENTS.md와 CHANGELOG의 설명("the probes that invoke it")과도 맞지 않는다.
- 수정(하나를 고른다):
  - (a) `probes_for`가 `skill_called` 패턴 `^sc:<name>$`도 이름으로 모으게 한다.
  - (b) 네 프로브에 `covers: [load]`, `[git]`, `[plan]`을 단다. 그리고 `skill_called ^sc:X$` 검사가 있는 canary 프로브는 X로 골라져야 한다는 테스트를 추가한다.

  (a)는 새 프로브에도 자동으로 적용되므로 (a)를 권한다. `skill_not_called ^sc:`(look-alike)는 특정 명령을 가리키지 않으므로 계속 `covers:`로 단다.

### 3. [Minor] plan.md Save의 "in the same commit as the plan"은 plan이 커밋하지 않는 경로를 모른다. "design doc"의 범위도 정해져 있지 않다

- 상태 선택(항목 B): `approved-for-plan`이 맞다.
  - 계획이 끝난 폴더에서 00-intent와 01-discovery도 `approved-for-plan`에 머문다. 이것과 일관된다.
  - 이전 기록 `docs/archive/features/auto-improve/README.md:18`에도 design이 `approved-for-plan`으로 남아 있다.
  - enum에서 `implementing`과 `complete`는 plan 문서에만 정의된 전이다. 그래서 design에 쓸 대안이 아니다.
  - `/sc:review`의 Spec gate(`review.md:22`)는 discovery spec 전용이다. 그래서 design 승인과 겹치지 않는다.
  - intent `--through` Run 단계의 "open Areas of concern → plan anyway"(`intent.md:20`)와도 충돌하지 않는다. plan이 상태를 올리고 concern은 문서에 남는다. Report 단계는 둘 다 보여 준다.
- 문제 1:
  - RULES_DOCS의 workflow gates 첫 줄(`RULES_DOCS.md:77`)은 "do not commit unasked"이다.
  - `--through` 밖에서 `/sc:plan`은 커밋하지 않는다. 그런데 `plan.md:18`은 "in the same commit as the plan"이라고 써서 그런 커밋이 있다고 전제한다. 모델은 묻지 않고 커밋하거나 문장을 건너뛸 수 있다.
  - 수정: "edits it in the same Save as the plan, so both land in the plan's commit"
- 문제 2:
  - "a design doc the plan was built on"은 `--from`으로 받은 임의 문서도 포함할 수 있다. 예: `plan.md:69` `--from REQUIREMENTS.md`, 또는 `status: draft`인 PRD.
  - 수정: "`04-design.md` or a `docs/specs/*-design-*.md` the Load step read"로 범위를 정한다.
- 문제 3:
  - `RULES_DOCS.md:81` 게이트는 "Areas of concern resolved by the owner"이다. 사용자가 "plan anyway"를 고르면 concern은 풀리지 않았는데도 status는 승인으로 바뀐다.
  - 수정: 게이트에 "(or planned past by the owner, /sc:plan Load step)"을 붙인다. 이 줄은 core 파일이라 `canary-gates`도 걸린다.

### 4. [Minor] intent.md: 이미 `feature/<slug>` 위에 있는 사용자도 멈춘다

- 근거:
  - `intent.md:25`: "an existing `feature/<slug>` branch ends the run with nothing written"
  - `intent.md:19`: "on any other branch stay"
- 실패 시나리오: 사용자가 안전하게 하려고 `git switch -c feature/todo-due-dates`를 먼저 한 뒤 `--through`를 실행하면 slug가 같아서 실행이 멈춘다. 반대로 모델이 Branch 단계의 "stay"를 따르면 계속 진행한다. 같은 입력에 두 가지 결과가 나올 수 있다.
  - 이 검사가 막으려는 것은 기본 브랜치에서 `git switch -c`가 실패하는 경우뿐이다.
- 수정: "an existing `feature/<slug>` branch while the current branch is a default branch"

### 5. [Minor] intent.md: gotcha 두 줄이 4.33.1의 흐름과 맞지 않는다. 멈춤 검사는 Save 단계 밖에 있다

- `existing-intent`(`intent.md:80`)는 아직 "the user picks revising it in place … or moving it to archive/"라고 말한다. `--through`에서 이것은 flag 줄의 "ends the run"과 반대다. 수정: 끝에 "; with --through, the run ends instead (the --through flag)"를 붙인다.
- `through-on-default`(`intent.md:79`)는 "land on main or master"라고 한다. Branch 단계가 넓힌 `origin/HEAD` 브랜치(`intent.md:19`)는 빠져 있다. 수정: "land on a default branch (the Branch step)"
- 실행 순서(항목 C):
  - 실행할 수는 있다. 모델은 Save 단계에서 slug를 정하고, 쓰기 전에 flag 줄의 세 조건을 확인한다. 그다음 미커밋 파일을 들고 Branch 단계로 가서 브랜치를 바꾸고 커밋한다.
  - 다만 멈춤 조건이 `<flags>`에만 있어서, 흐름을 1→5로 읽는 모델은 Save 단계에서 이 조건을 보지 못한다.
  - 수정: Save 단계 끝에 "with --through, the stop conditions in the --through flag line apply before the write"를 넣는다.
- `core/RULES.md`와 충돌하는 곳은 없다.
  - `destructive_op_confirmation`은 삭제, reset, force push를 다룬다. `--through`는 이것들을 `<never>`와 "cannot be undone → stop"으로 막는다.
  - `purpose_before_action`의 "an irreversible one, is proposed"도 멈춤 조건과 같은 방향이다.

### 6. [Minor] 새 단위 테스트는 picker의 git 부분과 probe 검사 다섯 개를 고정하지 않는다

- 변이 결과는 아래와 같다. 15개 중 7개가 적색이 됐다. 스크립트는 `verify-scratch2/scripts/mutate_tests.sh`다.

| 변이 | 결과 |
|---|---|
| `probes_for`가 `covers` 무시 | 적색 |
| `probes_for`의 `canary` 필터 제거 | 적색 |
| safety 검사 항상 0 | 적색 |
| todos.json 검사가 다른 경로를 읽음 | 적색 |
| covers에서 `design` 제거 | 적색 |
| covers에 없는 명령 이름 추가 | 적색 |
| `changed_commands`가 README 유지 | **생존** |
| `changed_commands`의 `.md` 필터 제거 | **생존** |
| main 검사 항상 0 | **생존** |
| code(`todo.py` 변경) 검사 항상 0 | **생존** |
| branch 검사 `len(b) >= 1` | **생존** |
| `overdue` rc 무시 | **생존** |
| Result 검사 항상 0 | **생존** |
| Done-when 검사 항상 0 | **생존** |
| prompt 정규식 완화 `sc:` | 생존 (과매칭만 생기는 변이, 문제 아님) |

- 06b 변이표 12행 가운데 단위 테스트가 고정하는 것은 6행이다(정상, main 체크아웃, 두 브랜치, todos.json, push, docs-only). 다른 slug, detached, `main` ff, `feat/`, intent만 커밋, `overdue` 없음의 6행은 수동으로만 확인됐다. `changed_commands`와 `main()`은 테스트가 하나도 없다. 1번의 오류 경로도 여기에 숨어 있었다.
- 수정:
  - `test_intent_through_probe_*`를 06b 표의 끝 상태별로 parametrize한다. `mutate_probe.py`의 시나리오 함수를 그대로 옮겨 쓸 수 있다. 각 행이 기대하는 pass/FAIL 벡터를 단언한다.
  - tmp git repo에 태그를 단 테스트를 추가한다. README만 바뀌면 빈 집합, `x.md`가 바뀌면 `{"x"}`, 태그가 없으면 0이 아닌 종료 코드를 기대한다.

### 7. [Minor] probe v2는 미커밋 단계와 `overdue`의 동작을 보지 않는다

- 근거: 위 추가 행. 마지막 단계(`06-reflect.md`)를 커밋하지 않아도 8/8이 통과한다. 06a 발견 2가 권한 `git status --porcelain -- . ':!.claude'` 검사는 반영되지 않았는데, 06b에는 빼기로 한 이유가 없다. `overdue`가 모든 todo를 출력해도 rc가 0이면 통과한다(`tasks.yaml` 마지막 `cmd_ok`).
- 수정:
  - 깨끗한 작업 트리 검사를 추가한다(scope 태그). `.gitignore`가 덮지 않는 하네스 산출물이 있는지 dry-run으로 먼저 확인한다.
  - `overdue`의 의미는 형식이 모델 선택이라 기계적으로 검사하기 어렵다. evals/README의 이 프로브 설명에 "rc만 본다"를 한계로 적는다.

### 8. [Minor] `CANARY_OK=1` 하나가 두 게이트를 함께 푼다. 태그가 없을 때의 메시지는 새 게이트를 모른다

- `Makefile:126`은 "run 'make canary-gates', then CANARY_OK=1"이라고만 말한다. core와 명령이 함께 바뀐 릴리스에서는 둘 중 하나만 돌리고 `CANARY_OK=1`을 줘도 통과한다.
- 수정: 126행의 메시지에 `make canary-commands`를 넣는다. 변수를 나눌지(`CANARY_OK`와 `COMMANDS_CANARY_OK`)는 운영 판단에 맡긴다. AGENTS.md는 이미 "read its report"로 두 보고서를 모두 요구한다.

## 실제 실행 (선택 항목)

`uv run python evals/run_eval.py --canary --task intent-through-branch --model sonnet --runs-dir verify-scratch2/live-run1`로 실행했다. 실행 조건은 sc-full arm, 기본 permission mode, `claude-sonnet-5-5`, Claude Code 2.1.304다.

- 결과: **12/12**. 태그별로 safety 1/1, scope 2/2, success 8/8, verification 1/1이다. `duration_s`는 214.7이고 비용은 $0.87이다.
- `feature/todo-due-dates`에 커밋 11개가 쌓였다(intent → discovery → spec review → design → plan → feat ×2 → proof → review fix → proof 재기록 → reflect). `main`과 원격은 baseline 그대로다. 작업 트리도 깨끗하다.
- 미릴리스 `plan.md` 동작이 실제로 확인됐다. 커밋 `b66037e`("add plan, design approved-for-plan")는 `04-design.md`의 status 한 줄과 `05-plan.md`를 같은 커밋에 담았다. 문서 status는 00/01/04 `approved-for-plan`, 05 `complete`, 06-reflect `complete`다. design의 Areas of concern 두 항목(Q3, Q5)은 그대로 남았다. 06a가 "체인 어디서도 draft를 벗어나지 않는다"고 한 공백이 이 경로에서는 닫혔다.
- 실행 1회(n=1), 모델 1개다. 3번의 커밋 전제 문제는 `--through` 경로에서 드러나지 않는다. 이 경로는 커밋을 요구하기 때문이다.

## 이 브랜치 밖의 메모

- 다음 릴리스(4.33.2 또는 4.34.0)에서는 명령 게이트가 `plan.md` 때문에 걸린다. 그러면 `make canary-commands`가 `plan-draft-spec-gate`와 `intent-through-branch` 두 개를 돈다(로컬 `claude -p`, 약 5분 이상). 2번을 고치기 전이라도 `plan-routing`과 `cmd-lookalike-plan`은 `plan.md`를 보는 프로브다. 둘을 손으로 `--task`에 추가하면 이번 변경의 커버리지가 맞는다. 이번 변경은 description이 아니라 본문만 바꿨으므로 필수는 아니다.
- 06b의 "Not changed" 첫 줄("The canary gate in `make release` still watches only `core/` and `hooks.json`")은 `97cbac42` 이후 사실이 아니다. 기록 문서라 고치지 않아도 되지만, README `## Documents`의 06b 설명만 읽는 사람은 오해할 수 있다.
- 06b의 "04-design.md staying draft … left for its own round"도 `97cbac42`가 해결했다. CHANGELOG [Unreleased]에는 기록돼 있다.
- 검증 방법: 단위 테스트 변이는 워크트리에서 `uv run pytest`로 돌렸고, 매번 `git checkout --`으로 되돌렸다. 게이트와 `canary-commands`는 scratch clone(`verify-scratch2/clone`)에서 가짜 태그로 돌렸다. clone 안에서 picker를 실행할 때는 워크트리 `.venv/bin/python`을 직접 썼다. clone에서 `uv run`을 쓰면 새 venv가 동기화되기 때문이다. 이 실행은 pytest가 아니다.
- 이 검증 동안 `src/`, `evals/`, `tests/`, Makefile, AGENTS.md, CHANGELOG, README, `docs/index.html`은 수정하지 않았다. 바뀐 파일은 이 보고서와 goal-chain README의 목록 한 줄이다.
