---
status: complete
revised: 2026-10-04
---

# 명령 전용 플래그 정의와 hook 오탐 수정 Implementation Plan

**Goal:** 모든 `/sc:` 명령의 `<syntax>` 플래그에 동작 정의를 붙이고, hook이 명령이 선언한 플래그를 오타로 경고하거나 같은 이름의 전역 지시문을 주입하지 않게 한다.

**Architecture:** 명령 본문에 `<flags>` 섹션(`- --name: 동작` 한 줄씩)을 둔다. 모델은 이 섹션을 정의로 읽고, hook은 그 명령이 소유한 플래그 목록으로 읽는다. `context_loader.py`는 프롬프트의 `/sc:<name>` 토큰마다 그 명령 파일의 `<flags>` 항목을 읽어, 해당 플래그를 오타 경고와 전역 실행 지시문에서 뺀다. 구조 테스트는 `<syntax>`와 `<flags>`를 서로 대조한다.

**Tech Stack:** Python(context_loader hook), pytest, 명령 마크다운

## 근거

- `implement.md:10`의 플래그 4개는 `<syntax>`와 예시 표(:32-35)에만 나온다. 2026-10-04 기준 33개 명령에 명령 전용 플래그가 99개 있다. 이 가운데 49개(28개 명령)는 표 밖 본문에 `--이름`으로 한 번도 나오지 않는다. 문자열 유무로 센 숫자라서, 접두사 없이 설명된 경우(`research.md:20-23`)와 정의가 아니라 사용 예일 뿐인 경우(`roadmap.md:47`)가 둘 다 섞여 있다.
- `resolve_flags("/sc:implement auth API --type api --safe --with-tests")`는 `--safe is not a recognized flag. Did you mean: --safe-mode?`를 낸다(`context_loader.py:454-459`). improve와 cleanup의 `--safe`도 같다.
- `_emit_execution_directives("/sc:implement --plan docs/plans/x.md")`는 전역 `--plan` 지시문("5줄 계획 후 승인 대기")을 출력한다(`context_loader.py:830-838`). implement의 `--plan`은 계획 문서 경로를 받는 플래그라서 뜻이 다르다.

## 범위 결정 (2026-10-04 사용자 결정)

- 정의가 없는 28개 명령 49개 플래그를 모두 다룬다. 테스트는 "`<syntax>`의 플래그는 모두 `<flags>`에 정의가 있어야 한다"를 예외 없이 검사한다. 이 테스트 때문에 본문에 정의가 이미 있는 플래그도 항목이 필요해서, 실제로 바뀌는 범위는 33개 명령 99개 플래그다.
- `--safe`는 cleanup 기준으로 통일한다. 기준은 `cleanup.md`의 `<auto_fix_threshold>`다. `<safe>` 등급(unused imports, dead variables, empty files)만 바로 바꾸고, `<approval_required>` 등급(exported functions, config files, shared modules)에 닿는 변경은 승인 없이 하지 않는다. 전역 `--safe-mode`(`FLAGS.md:35`, 최대 검증 + 보수 + `--uc`)와는 별개의 플래그다.
- implement `--plan`이 전역 지시문을 받는 문제도 이번 수정에 넣는다.

## 범위 밖

- `/sc:` 토큰 없이 플래그를 언급만 하는 경우. 지금처럼 경고가 붙는다. hook은 언급과 사용을 구분하지 못하고, 경고는 HTML 주석일 뿐이다.
- 명령이 선언하지 않은 플래그. 예: `/sc:review --plan`은 전역 `--plan` 지시문을 계속 받는다. review는 `--scope plan`을 쓰고 `--plan`은 선언하지 않기 때문이다. hook은 선언되지 않은 플래그의 뜻을 알 수 없다.
- TRIGGER_MAP의 문맥 주입. 예: `/sc:review --structured`는 `BUSINESS_SYMBOLS`를 불러온다(`context_loader.py:132`). 이 계획은 오타 경고와 실행 지시문만 다룬다.
- 선언 목록은 프롬프트에 있는 모든 `/sc:` 토큰의 합집합이다. 그래서 `/sc:implement --plan p.md`와 같은 프롬프트에 전역 뜻으로 친 `--plan`도 함께 빠진다.
- 명령 전용 플래그의 오타 제안(`--framwork`).
- 전역 뜻 그대로 쓰는 전역 플래그(brainstorm `--vs`/`--delegate`, roadmap·task `--delegate`, analyze `--focus`, spec-panel `--iterations`)의 재정의. SSOT는 `core/FLAGS.md`다.
- 플래그 삭제. 포크 사용자가 쓰는 플래그 문법은 그대로 둔다.

## Phase 0: 브랜치

- [x] master에서 `git switch -c fix/command-local-flags`. 이 계획서(현재 untracked)는 Phase 1 커밋에 함께 넣는다.

## Phase 1: hook이 명령이 선언한 플래그를 건너뜀 (커밋 1개)

### Task 1.1: hook 동작 테스트

**Files:** Test: `tests/unit/test_context_loader.py` (새 클래스 `TestCommandDeclaredFlags`)

- [x] Step 1: 실패하는 테스트를 쓴다. `tmp_path/fake.md`를 `encoding="utf-8"`로 쓰고 내용은 `<syntax>/sc:fake [--safe] [--plan path]</syntax>`와 `<flags>\n- --safe: x\n- --plan <path>: y\n</flags>`로 한다. `monkeypatch.setattr(cl, "_command_dirs", lambda: (tmp_path,))`로 연결한다. 지시문 테스트에서는 `TestContext7HasNoDocOnlyAFlag._emit`(:608-615)처럼 `get_loaded_contexts`, `mark_as_loaded`, `check_mcp_and_notify`를 막는다.
  - `/sc:fake build it --safe` → 알림 0개
  - `/sc:FAKE build it --safe` → 알림 0개 (명령 이름 소문자화)
  - `/sc:other --safe` (`other.md` 없음) → 알림 1개
  - `--safe go` → 알림 1개
  - `/sc:fake --instrospect` → 알림 1개 (전역 오타는 명령 안에서도 잡힘)
  - `/sc:fake --plan docs/x.md` → `sc-directive flag="--plan"` 없음
  - `/sc:other --plan docs/x.md` → `sc-directive flag="--plan"` 있음
- [x] Step 2: `uv run pytest tests/unit/test_context_loader.py -k CommandDeclared -q`를 실행한다. `_command_dirs`가 아직 없으므로 `AttributeError`로 실패해야 한다.

### Task 1.2: context_loader 구현

**Files:** Modify: `src/superclaude/scripts/context_loader.py` (:406-461 `resolve_flags`, :474-491 `_known_command_names`, :842-859 `_emit_execution_directives`)

- [x] Step 3: 최소 구현.
  - `_command_dirs()`는 `(claude_base() / "commands" / "sc", BASE_PATH / "commands")`를 반환한다. `_known_command_names()`도 이 함수를 쓰도록 바꾼다.
  - `flag_entries(text) -> set[str]`: `<flags>(.*?)</flags>`(`re.S`) 안에서 `^\s*- --([a-z][\w-]*)`(`re.MULTILINE`)에 맞는 이름을 모은다. Phase 2 구조 테스트도 이 함수를 쓰므로 hook과 테스트가 같은 파서를 공유한다.
  - `_command_flags(name)`: `_command_dirs()` 순서대로 처음 존재하는 `<dir>/<name>.md`를 `read_text(encoding="utf-8")`로 읽어 `flag_entries`에 넘긴다. 다른 파일 읽기(:755, :952)와 같은 방식이다. `(OSError, UnicodeDecodeError)`가 나면 빈 집합을 돌려준다(fail-open). cp949 같은 로캘에서 기본 인코딩으로 읽으면 `→ ≥ —`가 든 명령 파일에서 hook이 죽기 때문이다.
  - `_declared_flags(scannable)`: `_COMMAND_TOKEN_RE`로 찾은 이름을 소문자로 바꿔(`resolve_command_name` :519-520과 같음) 각각의 `_command_flags`를 합친다.
  - `resolve_flags`: `CC_NATIVE_PASSTHROUGH` 검사 다음, retired 검사 앞에 `if flag in declared: continue`를 넣는다. `declared`는 처음 인식하지 못한 플래그를 만났을 때 한 번만 계산하므로, 평범한 프롬프트에는 파일 읽기가 붙지 않는다.
  - `_emit_execution_directives`: 패턴이 맞으면 `match.group(0)`에서 플래그 이름을 꺼내고, `_declared_flags(scannable)`(처음 매치될 때 한 번 계산)에 들어 있으면 건너뛴다.
- [x] Step 4: `uv run pytest tests/unit/test_context_loader.py -q`가 통과하고, 이어서 `uv run pytest`가 exit 0인지 확인한다.
- [x] Step 5: `make format` 후 이 계획서와 함께 커밋한다: `fix(hook): skip command-declared flags in typo notice and global directives`

## Phase 2: `<flags>` 계약과 33개 명령 정의 (커밋 1개)

### Task 2.1: 구조 테스트와 실제 파일 회귀 테스트

**Files:** Test: `tests/unit/test_command_structure.py` (새 클래스 `TestCommandFlagsAreDefined`), `tests/unit/test_context_loader.py`

- [x] Step 1: 실패하는 테스트를 쓴다.
  - `test_every_syntax_flag_is_defined`: `<syntax>` 플래그에서 `VALID_FLAGS`를 뺀 집합이 `flag_entries(content)` 안에 모두 들어 있어야 한다.
  - `test_every_defined_flag_is_in_syntax`: `flag_entries(content)`가 `<syntax>` 플래그의 부분집합이어야 한다. syntax에서 사라진 플래그의 정의가 남는 것을 막는다.
  - 실제 파일 회귀 테스트 2개: `_command_dirs`를 `(CONTENT_ROOT / "commands",)`(`test_context_loader.py:340`)로 바꿔 끼운다. `BASE_PATH`는 설치 콘텐츠 디렉터리(`claude_base()/"superclaude"`, :77-96)라서 `commands/`가 없으므로 쓰면 안 된다. 기대 결과: `/sc:implement auth API --type api --safe --with-tests` → 알림 0개, `/sc:implement --plan docs/plans/x.md` → `--plan` 지시문 없음.
- [x] Step 2: 실행하면 명령 33개와 회귀 테스트 2개가 실패해야 한다.

### Task 2.2: 작성 규칙

**Files:** Modify: `.claude/rules/command-authoring.md` (XML Template, XML Rules의 규칙과 "Optional:" 줄, Checklist)

- [x] Step 3: 템플릿에서 `<flow>` 바로 다음에 `<flags>` 블록(`- --flag-name <value>: behavior.`)을 넣고, "Optional:" 목록에 `<flags>`를 추가한다. XML Rules에 다음 규칙을 넣는다. "`<syntax>`의 플래그 중 `core/FLAGS.md` 전역 플래그가 아닌 것은 모두 여기에 정의한다. 한 줄에 하나씩 쓰고, 파싱되는 부분은 `- --name`이다. 다른 섹션에 이미 정의가 있으면 항목은 그 섹션을 주제 이름으로 가리키기만 하고 내용을 다시 쓰지 않는다. 전역 플래그 이름을 다른 뜻으로 쓸 때도 여기에 정의한다. 그러면 이 명령에서는 hook이 그 이름의 전역 지시문을 주입하지 않는다." Checklist 1번에도 반영한다.

### Task 2.3: 명령별 `<flags>` 작성

**Files:** Modify: `src/superclaude/commands/*.md` 33개 (`<flow>` 바로 다음에 삽입)

- [x] Step 4: 한 플래그의 정의는 한 곳에만 둔다(`content-quality.md` 4번).
  - 아래 표에 있는 플래그는 표의 정의를 그대로 넣는다. ★는 본문 근거가 없거나 근거를 넘어서는 뜻이다.
  - 표에 없는 43개는 본문에 이미 정의가 있다(flow 단계, `<outputs>`, `<patterns>`, `<depth>`, gotcha, frontmatter description). 항목은 그 정의를 주제 이름으로 가리키는 한 줄로 쓰고, 원래 문장은 손대지 않는다. 예: `- --tdd: cycle in the TDD pattern.`
  - business-panel: 이미 `- --flag:` 형식인 `<options>`를 `<flags>`로 이름만 바꿔 `<flow>` 다음으로 옮긴다. `--mode` 항목을 추가해 `<modes>` 섹션을 가리키고, `--focus` 항목 끝에 "unrelated to the global --focus"를 붙인다.
  - review: `scope-flag-local` gotcha(:65)를 `--scope` 항목으로 옮기고 gotcha는 지운다. `--structured`(:37)와 `--audit-delegated`(flow 8)는 가리키는 항목으로 쓴다.
  - help: 기존 `<flags>` 산문을 `- --flags:` 항목 하나로 바꾼다.
  - test: `<does>`에 "root-cause fixes when --fix is given"을 추가해 `--fix` 정의와 bounds가 서로 어긋나지 않게 한다.
- [x] Step 5: `uv run pytest tests/unit/test_command_structure.py tests/unit/test_context_loader.py -q`가 통과하고, 이어서 `uv run pytest`가 exit 0인지 확인한다. 가장 긴 명령(`prompt.md`, 134줄)도 200줄 목표 안에 있어야 한다.
- [x] Step 6: 커밋한다: `docs(commands): define every command-local flag in <flags>`

| 명령 | 플래그 | 정의 (본문에 그대로) | 근거 |
|---|---|---|---|
| analyze | `--depth quick\|deep` | quick reports the top findings from one pass; deep covers the whole target and ties every finding to file:line evidence | ★ ex:60 |
| auto-improve | `--budget <dur>` | wall-clock limit for the whole loop (default 8h) | cli.py:68 |
| auto-improve | `--smoke-cmd <sh>` | health check run at the start of each cycle; a failing check logs `smoke_fail` and skips that cycle | coordinator.py:98 |
| auto-improve | `--cycle-timeout <sec>` | timeout for each smoke, mutate and eval step (default 600) | cli.py:74 |
| auto-improve | `--dry-run` | record the baseline metric only; no mutations | cli.py:86 |
| auto-improve | `--scope <glob>` | glob limiting the files the mutator edits (advisory, default `**`); unrelated to the global --scope | cli.py:82 |
| brainstorm, roadmap | `--strategy systematic\|agile\|enterprise` | systematic works through every requirement area in order; agile splits the work into parallel streams (e.g. frontend, backend, security) and iterates; enterprise adds compliance and validation requirements throughout | brainstorm ex:56-58, roadmap ex:41-43 |
| roadmap | `--depth shallow\|normal\|deep` | detail per workflow step: shallow brief, normal balanced, deep adds acceptance criteria and risks | ★ brainstorm.md:14 확장 |
| build | `--clean` | delete the output directory of the chosen --type (dist-dev/, dist/ or dist-test/) before building; nothing outside it, and never git clean | ★ outputs:23-25, never:56 |
| build | `--verbose` | run the build tool in its verbose mode and report the full output, not a summary | ★ |
| cleanup | `--safe` | change only the safe tier of the auto-fix threshold (unused imports, dead variables, empty files); list approval-required items (exported functions, config files, shared modules) without changing them; unrelated to the global --safe-mode | ★ auto_fix_threshold, 사용자 결정 |
| cleanup | `--aggressive` | also change approval-required items, each after the user approves it; remove code with no static reference only after a search for dynamic references (string lookups, reflection, config) finds none | ★ ex:58-60 |
| cleanup | `--interactive` | show each change group and apply it only after the user accepts it; under --dry-run nothing is applied and the accepted groups form the preview | ★ ex:52, :43 |
| design | `--format diagram\|spec\|code` | diagram: Mermaid diagram; spec: written specification; code: interface definitions (types, signatures) with no implementation | ex:45-48 |
| document | `--style brief\|detailed` | brief: purpose and usage only; detailed: adds parameters, return values, errors and examples | ex:42-43 |
| estimate | `--type effort\|complexity` | effort: relative size with a confidence level, by category; complexity: risks and a dependency map | ex:31-33 |
| estimate | `--breakdown` | split the estimate per sub-task instead of giving one total | ★ ex:31-32 |
| explain | `--level basic\|intermediate\|advanced` | audience level that flow step 2 otherwise infers: basic assumes no domain knowledge, advanced assumes the reader knows the domain | ex:31-34, flow:14 |
| explain | `--context <domain>` | domain that frames the explanation (e.g. react, security); for a library, look up its current docs first | ex:32,34 |
| explain | `--format text\|examples\|interactive` | text: prose; examples: lead with runnable examples; interactive: explain in steps with one comprehension question between steps | ★ |
| git | `--smart-commit` | draft a conventional-commit message from the staged diff and show it before committing | ex:57 |
| git | `--interactive` | walk through the operation step by step and confirm each decision (e.g. conflict resolution) with the user | ex:58 |
| implement | `--plan <path>` | implement from this plan doc in its task order; unrelated to the global --plan, whose 5-line-plan directive does not apply | flow:13 |
| implement | `--type …` | selects the lead agent: component → frontend-architect, api and service → backend-architect, feature → multi-agent coordination | ex:32-34 (service는 ★) |
| implement | `--framework …` | follow this framework's conventions and look up its current docs (Context7) before writing framework-facing code | ex:35 |
| implement | `--safe` | build the feature without changing existing exported functions, config files or shared modules; a change the feature needs there is shown first and waits for approval; unrelated to the global --safe-mode | ★ cleanup 등급, 사용자 결정 |
| implement | `--with-tests` | write tests for the new behavior with the code and run them in the Validate step | ex:33-34 |
| improve | `--type …` | dimension to improve; performance needs a measured baseline first, else stop and point to /sc:analyze --focus perf | ex:24-26 |
| improve | `--safe` | change nothing that code outside the target depends on: changes to exported functions, config files or shared modules are listed as proposals, not applied; unrelated to the global --safe-mode | ★ cleanup 등급, 사용자 결정 |
| improve | `--interactive` | present each improvement and apply it only after the user accepts it | ★ |
| index | `--format md\|json\|yaml` | md writes the files in the outputs table; json or yaml writes the same stem with that extension (e.g. docs/reports/API.json) | ★ outputs:23-25 |
| load | `--type project\|config\|deps\|checkpoint` | what to load: project memory and structure, configuration files, dependency manifests, or the saved checkpoint the target names (e.g. session_123) | ★ ex:39,41,46 |
| load | `--refresh` | re-read sources and replace loaded memory instead of reusing it | ★ ex:41 |
| load | `--analyze` | on top of the structure flow step 4 always reports, assess the project's state: test status, open TODOs and recent changes | ★ ex:39 |
| plan | `--output <path>` | write the plan to this path instead of the convention path | ex:57 |
| plan | `--phases N` | preferred phase count; a hint applied only when the work splits that way naturally | ex:59 |
| pm | `--strategy …` | force the strategy flow step 2 otherwise picks | flow:15 |
| pm | `--verbose` | report each sub-agent dispatch and result as it happens, not only the final summary | ★ |
| promote-feature | `--from <path>` | promote this one file as the primary doc instead of scanning by slug; its slug must still match <slug> | ex:45, never:70 |
| prompt | `--out <path>` | (구현 시 대조 결과 본문 `<tools>` Write가 이미 정의 → 가리키는 항목으로 씀: destination for saving the rewritten prompt, per the Write entry in tools) | prompt.md `<tools>` Write |
| recommend | `--estimate` | add an effort estimate for the recommended command sequence | ★ |
| recommend | `--alternatives` | list other viable commands with a one-line trade-off each | ★ |
| recommend | `--expertise …` | explanation depth per the expertise adaptation section | recommend.md:39 |
| reflect | `--type task\|session\|completion` | task: the current task's goal alignment; session: all work this session; completion: done-ready judgment | ex:26-28 |
| reflect | `--analyze` | goal alignment: compare the work done against the task's stated goal, item by item | ex:26 (세부는 ★) |
| reflect | `--validate` | quality check of the delivered work: verification actually run, claims backed by evidence, gaps named; unrelated to the global --validate | ex:27 (세부는 ★) |
| research | `--depth …` | hops and validation per the depth profiles section | research.md:20-23 |
| research | `--strategy …` | planning, intent and unified as defined in modes/RESEARCH_CONFIG.md (unified is the default) | RESEARCH_CONFIG.md:7,21 |
| save | `--summarize` | also write a summary of the session's work and learned patterns | ex:60 |
| select-tool | `--analyze` | show the complexity score and the decision-matrix rule that picked the tool | ★ ex:35 |
| select-tool | `--explain` | explain the choice in plain terms, including why the runner-up loses | ★ ex:36 |
| task | `--strategy …` | force the execution order flow step 3 otherwise picks | flow:15 |
| test | `--type unit\|integration\|e2e\|all` | which suite runs; e2e runs Playwright browser tests; all runs every suite | outputs:24-25, ex:48 |
| test | `--coverage` | collect coverage and report it against the thresholds (line ≥80%, branch ≥70%) | test.md:23 |
| test | `--watch` | run the project's watch mode, re-running affected tests on change | test.md:38 |
| test | `--fix` | on failure, find the root cause as /sc:troubleshoot --type bug would and fix the code, then re-run; never edit a test just to make it pass | ★ ex:49,55 (`<does>` 수정 동반) |
| troubleshoot | `--type …` | problem class: bug starts from reproduction and stack trace, build from compiler and dependency output, performance from a measurement, deployment from environment and config | ex:34-37 |
| troubleshoot | `--trace` | trace the data flow and execution path up to the failure before naming a cause | flow:14, ex:34,37 |

## Phase 3: 설치본 동기화와 실제 hook 확인 (커밋 없음)

hook은 원본을 그대로 복사한 설치본 `.claude/commands/sc/`를 먼저 읽는다. 그래서 동기화하기 전에는 Phase 2의 `<flags>`가 hook에 보이지 않는다.

- [x] Step 1: `superclaude doctor --scope local`로 local scope 설치 상태를 확인한다(2026-10-04에 healthy 확인함). 그다음 `superclaude install --force --scope local`을 실행한다. user scope는 동기화하지 않는다(`sync-scope-creates`).
- [x] Step 2: hook을 직접 실행해 확인한다. 실행할 때마다 새 `session_id`(`verify-1`부터 `verify-4`까지)를 넣는다. `session_id`가 없으면 공용 fallback 캐시(:62-73)를 쓰게 되고, 앞선 실행에서 찍힌 지시문 표시가 남아 있으면 "지시문 없음" 확인이 거짓으로 통과한다.
  - `{"prompt":"/sc:implement auth API --type api --safe --with-tests","session_id":"verify-1"}` → `not a recognized flag`가 없어야 한다.
  - `{"prompt":"/sc:implement --plan docs/plans/x.md","session_id":"verify-2"}` → `sc-directive flag="--plan"`이 없어야 한다.
  - 대조군 `{"prompt":"/sc:analyze --plan docs/plans/x.md","session_id":"verify-3"}` → `sc-directive flag="--plan"`이 있어야 한다.
  - `{"prompt":"--safe go","session_id":"verify-4"}` → `Did you mean: --safe-mode?`가 나와야 한다.
  - 각 줄은 `echo '<json>' | superclaude hook context_loader`로 실행한다.
- [x] Step 3: `git checkout master && git merge --no-ff fix/command-local-flags`를 한 명령으로 실행해 병합한다(`editable-tool-branch-switch`). push한 뒤 master CI를 확인한다.

## 위험

- editable install이라서 이 작업 트리가 곧 실행 중인 hook 코드다. Phase 1에서 예외가 나면 UserPromptSubmit hook이 실패한다. exit 1이라 프롬프트를 막지는 않을 것으로 보지만 Claude Code에서 확인하지는 않았다. 그래서 `_command_flags`가 읽기·디코딩 예외를 잡게 했다.
- ★ 정의는 이 계획에서 정한 뜻이다. `--safe` 세 개는 사용자 결정에 따라 cleanup의 `<approval_required>` 목록을 공통 경계로 쓴다. implement 예시 표(:33)의 "security agents"는 `--safe`가 아니라 auth 도메인에서 나오는 결과로 보고 손대지 않는다.
- `<flags>`에 전역 이름을 정의하면 그 명령 안에서는 전역 지시문이 꺼진다. implement `--plan`에서는 의도한 동작이고, command-authoring.md 규칙에 적어 실수로 정의하는 일을 막는다.
- 새 `.py` 파일이 없으므로 `codex-module-count-drift`에는 영향이 없다.
- 이 계획서는 15KB 목표를 넘는다. 정의 표와 그 표를 쓰는 작업을 한 문서에 두려고 그렇게 했다.

## 완료 기준

- `uv run pytest` exit 0
- `TestCommandDeclaredFlags` 7개, 실제 파일 회귀 테스트 2개, `TestCommandFlagsAreDefined` 2개 × 명령 수가 모두 통과
- Phase 3 Step 2의 hook 출력 4건이 기대한 대로 나옴(대조군 포함)
