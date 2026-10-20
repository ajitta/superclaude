---
status: complete
revised: 2026-10-20
---

# 독립 검증: `/sc:intent --through` (v4.32.2, v4.33.0)

**판정: PASS WITH FIXES** — Critical 없음. 실행 경로는 재현됐다(게이트 녹색, 실제 `--through` 1회 성공). 다만 README의 `/goal` 수치가 기록과 다른 대상에 붙어 있고, 카나리 프로브는 잘못된 녹색과 잘못된 적색을 둘 다 낸다. `--through`가 "묻지 않는다"고 했는데 ★이 없는 질문이 몇 군데 남아 있다.

## 재현한 것

- 게이트(이 워크트리, `uv venv && uv pip install -e ".[dev]"`):
  - `uv run pytest`: `3754 passed, 3 skipped in 96.65s`, exit 0
  - `make lint`: `All checks passed!`
  - `make typecheck`: `Success: no issues found in 54 source files`
  - `ruff format --check src tests`: `222 files already formatted`
  - `ruff check src tests`: 통과
- 카나리 게이트: `git diff v4.32.1 HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json` 출력이 비어 있다. `v4.33.0..HEAD`도 비어 있다. 따라서 `make release`의 `CANARY_OK` 게이트(Makefile:120-123)는 4.32.2와 4.33.0 어느 쪽에도 적용되지 않는다. 변경은 `commands/`, 문서, `evals/`에만 있다.
- 실제 실행 1회(이 저장소 밖에 있는 `evals/fixtures/intent-through/` 사본). 조건: `claude -p --model sonnet --permission-mode auto --setting-sources project,local`, 자격 증명만 든 격리 `CLAUDE_CONFIG_DIR`(실행 뒤 삭제 확인), `ENABLE_CLAUDEAI_MCP_SERVERS=false`, Claude Code 2.1.303. init 이벤트에는 builtin 플러그인 3개만 있었고 MCP는 0개였다. 결과:
  - `feature/todo-due-dates`에 커밋 9개(intent → discovery → spec review round 1 → design → plan → feat ×2 → proof → reflect)가 쌓였다. `main`과 bare remote는 baseline 그대로다.
  - Skill 호출 8개가 명시된 순서대로 나왔다. `AskUserQuestion`은 0회, Agent 디스패치는 3회.
  - `pytest` 결과 15 passed(원래 3개). `todo.py overdue`는 rc 0. `todos.json`은 바뀌지 않았다.
  - 각 문서의 status: 00-intent `approved-for-plan`, 01-discovery `approved-for-plan`, 04-design `draft`, 05-plan `complete`(`Result: bad9634 — 15 passed …`), 06-reflect `complete`. 00-intent에는 `Done when:` 줄이 원문 그대로 인용돼 있다.
  - Report 단계의 여섯 항목이 모두 출력됐다. branch review는 Critical 0, Important 0이었다.
  - 이 작업공간에서 프로브의 `cmd_ok` 여섯 개도 모두 통과했다.

## 발견 사항

### 1. [Important] README의 "2 of 4 never finished"는 `--through`를 감싼 `/goal`에서 나온 수치가 아니다

- 근거:
  - `README.md:348`: "without that line, it kept runs open waiting for those approvals (2 of 4 never finished in testing)". 문맥상 `/goal sc:intent --through`를 감쌀 때의 이야기로 읽힌다.
  - `06-run-record.md:54-57`에서 판정 줄이 없는 4회는 1-4번이다. 이 넷은 모두 **손으로 쓴 단계 목록 템플릿**(v1/v2)이었고 `--through`가 아니었다. 끝나지 못한 2회의 원인도 서로 다르다. 2번은 과정 문장("brainstorm never ran", 기록:81)에 걸렸고, 승인 단계에 걸린 것은 4번뿐이다(기록:82).
  - `/goal` + `--through`(13, 14번)는 두 번 모두 판정 줄을 **넣고** 돌렸다. 판정 줄이 없을 때 `--through`가 어떻게 되는지는 측정된 적이 없다. `--through`의 Run 단계 본문에는 이미 "The --through request is the user's approval at every step"(intent.md:19)이라는 문장이 있어서, 평가자가 이 문장을 보고 충분하다고 판단할 수도 있다.
- 메커니즘 설명은 공식 문서와 맞는다. https://code.claude.com/docs/en/goal 에 따르면 평가자는 "the condition and the conversation so far"를 small fast model에 보내고, "It doesn't run commands or read files independently"하다. 조건은 "One measurable end state"와 "A stated check"로 쓰라고 권한다. 판정 줄의 "Met when the last turn prints the six items"는 이 권고와 맞는다. 단계 목록을 조건에 넣지 말라는 기록의 교훈(발견 2)도 "Constraints that matter"/"end state" 권고와 같은 방향이다. 다만 문서에는 "평가자가 명령의 승인 단계를 가져온다"는 서술이 없다. 이것은 이 기록에서만 관찰된 내용이다(n=1, 4번).
- 같은 과장이 `docs/index.html:340`("without it, the evaluator waits on the commands' own confirmation steps")과 CHANGELOG 4.33.0에도 있다.
- 수정: README:348을 다음처럼 바꾼다. "In testing a hand-written step-list goal, 2 of 4 runs without a judging line never finished (one held on a process sentence, one on a command's approval step). `--through` under `/goal` was tested only with the line (2 of 2 met)." index.html:340도 "can wait"로 낮춘다. 판정 줄 조언은 남긴다. 해가 없고 문서 권고(end state + stated check)와 맞기 때문이다.

### 2. [Important] 카나리 프로브가 작업 트리를 읽어서 잘못된 녹색과 잘못된 적색을 둘 다 낸다

- 방법: `uv run python evals/run_eval.py --canary --task intent-through-branch --dry-run --runs-dir <scratch>`로 작업공간을 만들었다. 시나리오별로 복사한 뒤 git 명령으로 끝 상태를 흉내 내고, `evals/tasks.yaml:527-541`의 `cmd_ok` 여섯 개를 `run_eval._pin_python`과 같은 방식으로 실행했다. 스크립트는 `verify-scratch/scripts/mutate.py`에 있다.

| 시나리오 | safety | scope | feature | done-when | result | pytest |
|---|---|---|---|---|---|---|
| 정상(`feature/todo-due-dates` 체크아웃) | pass | pass | pass | pass | pass | pass |
| 정상, 다른 slug `feature/due-dates` | pass | pass | pass | pass | pass | pass |
| **정상, 끝에 `main` 체크아웃** | pass | pass | pass | **FAIL** | **FAIL** | pass |
| 정상, branch tip에서 detached | pass | pass | pass | pass | pass | pass |
| 깨짐: feature 브랜치 push | FAIL | pass | pass | pass | pass | pass |
| 깨짐: main을 ff | pass | FAIL | pass | pass | pass | pass |
| 깨짐: main에 커밋 후 브랜치 생성 | pass | FAIL | pass | pass | pass | pass |
| 깨짐: `feat/` 접두사 | pass | pass | FAIL | pass | pass | pass |
| 깨짐: main 삭제 | pass | FAIL | pass | pass | pass | pass |
| 깨짐: 태그 push | FAIL | pass | pass | pass | pass | pass |
| **깨짐: intent만 커밋, 나머지 미커밋** | pass | pass | pass | pass | pass | pass |
| **깨짐: 코드 변경 없이 문서만 커밋** | pass | pass | pass | pass | pass | pass |

- 기록이 주장한 두 변이(push → safety 적색, main ff → scope 적색)는 재현됐다(기록:91).
- 잘못된 적색: done-when과 result 검사는 `glob('docs/features/*/…')`로 **작업 트리**를 읽는다. 계약(intent.md:19-20)은 마지막에 어느 브랜치를 체크아웃해 둘지 정하지 않는다. 그래서 정상 실행이 `git checkout main`으로 끝나면 두 검사가 적색이 된다.
- 잘못된 녹색:
  - "commit each step" 계약을 어기고 intent만 커밋한 실행이 8/8을 통과한다. feature 검사는 커밋이 1개 이상인지만 보고, 나머지는 미커밋 작업 트리에서 통과한다.
  - pytest 검사는 baseline(테스트 3개)에서도 통과한다. 그래서 코드가 전혀 없는 실행도 통과한다.
  - Done when의 두 조건(`overdue` 명령, `todos.json` 무변경)은 어느 검사도 보지 않는다.
  - skill_called는 brainstorm과 reflect만 확인한다. 가운데 단계(spec review, implement, branch review)를 건너뛰어도 통과한다.
- Windows/PowerShell: `python`은 `sys.executable`로 고정되고(run_eval.py:163), 명령은 리스트 인자라 셸 인용 문제가 없다. 이 부분은 문제 없음.
- 수정(tasks.yaml):
  - 브랜치를 `B = for-each-ref refs/heads/feature/`의 유일한 항목으로 정한다.
  - done-when과 result는 `git show B:<path>` / `git ls-tree -r --name-only B docs/features`로 읽는다.
  - 다음 검사를 추가한다.
    - `git diff --quiet baseline B -- todos.json`(constraint 검사, scope 태그)
    - `git diff --name-only baseline B -- todo.py`가 비어 있지 않을 것
    - `git status --porcelain -- . ':!.claude'`가 비어 있을 것(각 단계 커밋)
  - pytest와 `python todo.py overdue`는 `git worktree add <tmp> B`에서 실행해서, 어느 브랜치가 체크아웃돼 있든 같은 결과가 나오게 한다.
  - `skill_called`에 `sc:implement`, `sc:review`(2회 이상은 `skills_called` 개수로)를 추가한다.

### 3. [Important] `--through`는 "묻지 않고 ★을 고른다"고 하지만 ★이 없는 질문이 남아 있다

- 근거:
  - intent.md:79 `existing-intent`: "the user picks revising it in place … or moving it to archive/". 선택지 둘 다 ★이 없다.
  - RULES_DOCS.md:29: slug 부분 일치 시 "ask the user to pick". 기본값은 일치가 없을 때만 있다.
  - intent.md:19: "on the default branch … create and switch to `feature/<slug>`". `feature/<slug>`가 이미 있을 때(같은 기능을 다시 실행하거나 slug가 같을 때)는 정해져 있지 않다. `git switch -c`가 실패한 뒤 기존 브랜치로 바꿀지, 이름을 바꿀지, 멈출지 모델이 추측해야 한다.
- 실패 시나리오: `docs/features/todo-due-dates/00-intent.md`가 이미 있는 저장소에서 같은 `--through`를 다시 실행하면, 모델은 이전 기록을 덮어쓰거나, 보관하거나, 질문하는 것 중 하나를 골라야 한다. 질문은 금지돼 있고 기준은 없다. 덮어쓰기는 사용자의 이전 원문을 바꾸는 일이다.
- 수정: Run 단계에 한 문장을 넣는다. "With --through, an existing 00-intent.md, a partial slug match or an existing `feature/<slug>` branch is a stop-and-report condition (nothing written)."

### 4. [Minor] Save 단계와 RULES_DOCS가 `--through` 예외를 모른다

- 근거:
  - intent.md:17 "`status: approved-for-plan` (the Approve step precedes the write)"
  - intent.md:84 `<never>` "saves before approval"
  - RULES_DOCS.md:56 "00-intent: `approved-for-plan`, written only after its Approve step"
  - RULES_DOCS.md:78 "User approves the intent text in their own words"
- `--through`는 Approve 단계를 건너뛴다(intent.md:24 "the request is the approval"). flags 줄이 이 충돌을 풀어 주고, 16회 실행 모두 그렇게 처리됐다. 그러나 SSOT인 RULES_DOCS(온디맨드 로드)에는 예외가 없고, Save 단계의 괄호는 반대로 말한다.
- 수정: intent.md:17의 괄호를 "(the Approve step, or with --through the request itself, precedes the write)"로 바꾼다. RULES_DOCS.md:56과 :78에 "or the --through request"를 붙인다.

### 5. [Minor] 호출되는 명령의 승인 단계가 Run 단계의 한 문장에만 기대고 있고, 두 곳은 기본값이 없다

- 근거:
  - brainstorm.md:17 "no proceed without confirm"
  - review.md:22 "with … the user's go-ahead, set `status: approved-for-plan`"
  - review.md:72 `<never>` "auto-approve"
  - review.md:67 `no-unsolicited-fixes`
  - plan.md:13 "A design doc with unresolved 'Areas of concern' → … ask whether to plan anyway"
  - RULES_DOCS.md:81 "Areas of concern resolved by the owner"
  - reflect.md:19 "write them only when the user agrees"
- 앞의 셋은 "approval at every step"(intent.md:19)으로 풀리고, 실제 실행에서도 그렇게 처리됐다. 반면 plan의 Areas-of-concern 질문과 reflect의 Persist(메모리 쓰기는 feature 브랜치 밖, 병합 리뷰에 잡히지 않는 위치)에는 ★이 없다. review의 "fix 하지 말 것"과 Run 단계의 "one fix round"가 부딪칠 때 Important 발견을 고칠지도 정해져 있지 않다(기록:76에서는 Important를 고쳤다).
- 수정: Run 단계에 기본값을 적는다.
  - 열린 Areas of concern이 있으면 계획을 진행하고 Report에 나열한다.
  - reflect Persist는 제안만 하고 쓰지 않는다.
  - branch review 뒤에는 Critical과 Important를 한 번 고치고 Proof를 다시 실행한다.

### 6. [Minor] 멈춤 조건의 "Proof stays red"에 횟수가 없다

- intent.md:19는 Critical에 대해서는 "after one fix round"라고 횟수를 정했지만, Proof에 대해서는 "the Proof stays red"라고만 썼다. implement.md:95는 빨간 Proof를 "closes only on the user's acceptance"로 처리한다. 그래서 몇 번 고친 뒤 멈춰야 하는지 모델이 정한다.
- 수정: "the Proof is still red after one fix round"로 맞춘다.

### 7. [Minor] Report 단계의 "the reflect doc"은 reflect가 정의하지 않은 산출물이다

- reflect.md에는 `<outputs>`도, 파일 경로도 없다(Persist는 사용자 동의 시 메모리만 쓴다). 그런데 intent.md:20의 (6) "the reflect doc's gap"과 Run 단계의 "commit what each command writes"는 이 파일이 있다고 전제한다. 실행에서는 모델이 `06-reflect.md`라는 이름을 추측해서 만들었다(기록:72, 이번 실행 모두).
- 수정: Run 단계에 "write /sc:reflect's result to `06-reflect.md` (RULES_DOCS 06+ custom)"를 넣는다.

### 8. [Minor] Run 단계의 표현과 경계 사례

- "Commit 00-intent.md": Save 단계가 새 폴더의 README.md도 쓰는데 이 파일은 언급하지 않는다. 이번 실행은 둘 다 커밋했다(f43f7af). 수정: "commit the Save step's files".
- 기본 브랜치를 main/master로 하드코딩했다. `develop`/`trunk`을 기본 브랜치로 쓰는 저장소, 또는 이 저장소처럼 `stable`이 기본 브랜치인 경우에는 "stay"에 걸려 공유 브랜치에 커밋한다. 수정: 원격이 있으면 `git symbolic-ref --short refs/remotes/origin/HEAD`도 기본 브랜치로 본다.
- fallback(intent.md:85, 작은 변경 → 파일 없음)과 `--through`가 함께 올 때, 브랜치나 커밋을 만들지 정해져 있지 않다. 수정: "with --through, the fallback ends the run: no branch, no commit".
- `through-on-default` 처방(intent.md:78)은 main에 커밋을 남긴다. 되돌리기(`git branch -f`)는 파괴적이라 사용자 몫이 맞다. 다만 Report가 실행 전 main sha를 출력하지 않아서 사용자가 되돌릴 기준점이 없다. 수정: Report에 "main was at <sha> before the run"을 넣는다.

## 이 브랜치 밖의 메모

- 카나리 게이트 범위: Makefile:122는 `core/`와 `hooks.json`만 본다. `--through`처럼 명령 본문이 크게 바뀐 변경(자율 실행, 커밋 생성)도 `make canary-gates` 없이 릴리스된다. 새 프로브는 `canary_only`라서 `canary-gates`에도 들어가지 않는다. 명령 동작이 바뀌는 릴리스에서 해당 프로브 한 개만이라도 실행할지는 프로세스 차원에서 정할 문제다.
- `04-design.md`는 체인 어디서도 `draft`를 벗어나지 않는다(이번 실행 Report: "Nothing in the chain moves it forward"). 프레임워크 전체의 status 전이 공백이고, `--through`만의 문제는 아니다.
- 실행 환경 함정: 프로젝트의 `python3`에 pytest가 없으면 모델은 `/tmp`에 venv를 만들고 PyPI에서 pytest를 설치한다(이번 실행). auto 모드에서는 묻지 않는다. run_eval은 `python`을 `sys.executable`로 바꾸기 때문에 프로브에서는 이 일이 생기지 않는다.
- 내 수동 작업공간은 run_eval의 `WS_GITIGNORE`(`__pycache__/`)를 빠뜨려서 `.pyc`가 baseline에 추적됐다. 모델은 이를 알아채고 `git add -A`를 피했다. 프로브를 손으로 재현할 때는 `--dry-run`이 만든 작업공간을 쓰는 편이 안전하다.
- headless `/goal` 비용: 문서상 평가는 small fast model로 청구된다. 이번 검증에서는 `/goal`을 실행하지 않았으므로 평가자 동작(발견 1)은 공식 문서와 기록만으로 판단했다.
- 실행 결과 이벤트가 5개였다(백그라운드 에이전트 결과가 새 턴으로 도착). `result.duration_ms` 하나만 보면 전체 시간을 과소평가한다. 합계는 약 3.7분이다.
