---
status: draft
revised: 2026-10-05
---

# clone 없이 설치 (uv tool CLI + Claude Code plugin) Implementation Plan

**Goal:** 사용자가 저장소를 clone하지 않고 SuperClaude를 설치하게 한다. 1단계는 `uv tool install` 한 줄로 CLI를 설치하는 것이고, 2단계는 `/plugin install sc@ajitta-socratic`으로 content와 hooks를 받는 것이다.

**Architecture:**
- 1단계는 README만 바꾼다. 설치 소스는 모두 패키지 안에서 읽히므로(`cli/install_paths.py:143-150` `_get_package_root()`) git URL로 설치한 non-editable 패키지에서도 `superclaude install`이 동작해야 한다. 이것은 Phase 1에서 먼저 검증한다.
- 2단계는 `src/superclaude`(패키지 레이아웃)를 plugin 루트로 쓴다. 이 레이아웃은 context_loader가 이미 content 루트로 받는다(`tests/unit/test_context_loader.py:340`이 `SUPERCLAUDE_PATH=src/superclaude`로 실행함). 그래서 빌드 트리나 복사본이 필요 없다.
  - hook 명령은 지금처럼 `superclaude hook <name>`이고, 런타임은 1단계 CLI다.
  - plugin은 CLAUDE.md를 로드하지 못한다. 그래서 core(FLAGS/PRINCIPLES/RULES)는 새 SessionStart hook `core_inject`가 plugin 모드에서만 출력한다.

**Tech Stack:** uv tool, Claude Code plugin(`.claude-plugin/plugin.json`, marketplace), Python hook(stdlib만), pytest

## 근거

조사일: 2026-10-04.
- README 설치 절(`README.md:62-105`)은 `git clone` 다음 `make deploy`(`uv tool install --force --editable .`)만 안내한다. 루트 `install.sh`도 clone을 전제한다.
- 안내할 Python은 `-p 3.13`(소문자 `-p` = `--python`. 대문자 `-P`는 `--upgrade-package`)이다.
  - `requires-python = ">=3.10"`에 상한이 없다. 그래서 `-p`가 없으면 uv가 찾은 Python을 쓰는데, 이 PC에서는 어디서도 테스트하지 않은 시스템 3.14.7이 잡힐 수 있다.
  - 3.13은 실제로 쓰이는 버전이다. 개발 `.venv`가 3.13이고, 지금 hook을 실행하는 `superclaude` tool도 CPython 3.13.7이다.
  - 그런데 CI matrix(`.github/workflows/test.yml:17`)는 `["3.10", "3.11", "3.12"]`라서 3.13을 검사하지 않는다. 안내하는 버전을 CI가 검사하도록 Task 1.2에서 matrix에 추가한다.
- PyPI의 `superclaude` 이름은 upstream SuperClaude-Org가 쓰고 있다(4.3.0). 포크는 같은 이름으로 배포할 수 없어 git URL로 설치한다. 버전 `4.20.0+ajitta`는 PEP 440 local version이라 PyPI가 받지 않지만 git 설치에는 문제가 없다.
- 모든 hook이 `superclaude hook <name>`이고(`hooks/hooks.json`), hook 스크립트는 stdlib과 `superclaude.utils`만 import한다. 따라서 어떤 방식으로 배포하든 `superclaude` 패키지가 PATH에 있어야 한다.
- Claude Code plugin 규격(code.claude.com/docs/en/plugins/manifest-reference, components, hooks):
  - plugin 루트의 `CLAUDE.md`는 로드되지 않는다. 항상 지켜야 할 규칙은 hook으로 넣으라고 안내한다.
  - SessionStart hook의 stdout은 context에 들어가며, 문자열 하나당 10,000자에서 잘린다. hook마다 따로 센다.
  - `commands/<f>.md`는 `/<plugin>:<f>`가 된다. plugin 이름을 `sc`로 하면 `/sc:analyze`가 그대로 유지된다.
  - agent는 `sc:<name>`이 된다. plugin agent는 `memory`를 지원하고(components 739행), `permissionMode`/`hooks`/`mcpServers`/`initialPrompt`는 무시한다. SC agent 23개는 무시되는 필드를 쓰지 않는다.
  - `hooks/hooks.json`은 자동으로 로드된다. hook 프로세스는 `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_PROJECT_DIR`를 받는다. settings hooks에는 `CLAUDE_PLUGIN_ROOT`가 없다.
  - `${CLAUDE_PLUGIN_ROOT}`는 command/agent 본문에서 그 자리에서 치환된다.
  - plugin.json의 `commands`/`agents`/`outputStyles`는 기본 폴더 스캔을 대체한다. `hooks` 키는 `hooks/hooks.json`에 더해 로드된다.
  - plugin hooks와 settings hooks는 중복 제거되지 않는다(hooks 412행). plugin과 scope 설치를 같이 하면 hook이 두 번 돈다.
  - `version`은 형식 검사가 없는 문자열이다. `once`는 skill frontmatter의 hook에서만 적용된다.
- core 크기: FLAGS 4,391자 + PRINCIPLES 1,912자 + RULES 3,900자 = 10,203자. 한 hook으로 출력하면 10,000자를 넘는다.
- core 파일에는 cp949로 인코딩할 수 없는 문자(`— ⚡ 🔴` 등)가 있다. `print`로 쓰면 기본 로캘이 한국어인 Windows에서 hook이 죽는다.
- 이미 있는 plugin 기반:
  - `.claude-plugin/marketplace.json`(이름 `ajitta-socratic`)이 portable-skills plugin 2개를 싣고 있다. description은 "SuperClaude는 이 marketplace에서 설치하지 않는다"라고 적혀 있다.
  - `tests/unit/test_portable_skills.py:215`가 항목 집합이 portable skill 집합과 정확히 같은지 검사한다.

## 범위 결정 (2026-10-04 사용자 결정)

- "CLI 설치 + plugin 단계적" 방식을 택했다. CLI만 쓰는 방식(Serena 방식)과 CLI 없는 단독 plugin(사용자 PATH의 python3에 의존)은 택하지 않았다.
- 이전 포크의 plugin 검토 문서(`docs/archive/`)는 지금 코드와 구조가 달라 근거로 쓰지 않는다.

## 범위 밖

- PyPI 배포(다른 배포 이름 사용). git URL 설치로 충분하다. 외부 사용자가 늘면 검토한다.
- `superclaude doctor`의 plugin 감지. 중복 설치 경고는 매 세션 `session_init`이 낸다.
- content에 있는 agent 이름 참조 170곳을 `sc:<name>`으로 일괄 수정하는 일. Phase 4 probe가 실패할 때만 대응한다(아래 Task 4.2).
- `CLAUDE_PLUGIN_DATA`에 상태 저장. plugin 모드에서도 hook 상태는 `hook_state_dir()`(`~/.claude/.superclaude_hooks`)에 쓴다. 7일 지나면 정리된다.
- `superclaude context explain`, `verify-drift`, `uninstall`, `--list-all`의 plugin 지원. 이 명령들은 scope 설치 전용으로 README에 적는다.
- `install.sh` 정리. 이 작업에서는 건드리지 않는다.
- marketplace 이름 변경. 이름을 바꾸면 이미 설치된 socratic plugin의 id가 깨진다.

## Phase 0: 1단계 브랜치

- [ ] master에서 `git switch -c docs/uv-tool-install`. 이 계획 문서(현재 untracked)와 feature README는 Phase 1 커밋에 함께 넣는다.

## Phase 1: CLI만 설치 (README, 커밋 1개)

### Task 1.1: 현재 master가 git URL 설치로 동작하는지 먼저 확인

코드를 바꾸지 않는 단계다. 실제 dev tool 설치와 `~/.claude`를 건드리지 않도록 tool 디렉터리와 HOME을 scratchpad로 돌린다(gotcha `sync-scope-creates`, `venv-inherited-by-worktree`). Windows의 `Path.home()`은 `USERPROFILE`을 읽으므로 둘 다 설정한다.

- [ ] Step 1: 설치와 content 배치를 확인한다.
  ```bash
  S=<scratchpad>; export UV_TOOL_DIR="$S/tools" UV_TOOL_BIN_DIR="$S/bin"
  uv tool install -p 3.13 "git+file:///C:/Users/ajitta/Repos/ajitta/superclaude@master"
  H="$S/home"; mkdir -p "$H"
  env HOME="$H" USERPROFILE="$H" PATH="$S/bin:$PATH" superclaude install --scope user
  find "$H/.claude/commands/sc" -name '*.md' | wc -l    # 36
  find "$H/.claude/agents" -name '*.md' | wc -l         # 23
  grep -n "CLAUDE_SC.md" "$H/.claude/CLAUDE.md"         # import 줄 1개
  env HOME="$H" USERPROFILE="$H" PATH="$S/bin:$PATH" superclaude doctor --scope user
  env HOME="$H" USERPROFILE="$H" PATH="$S/bin:$PATH" superclaude verify-drift --scope user
  ```
- [ ] Step 2: `uv tool upgrade superclaude`가 git source에서 동작하는지 확인한다.
- [ ] Step 3: 하나라도 실패하면 README를 고치기 전에 원인을 찾아 이 계획에 Task를 추가한다. 예상 원인은 hatchling이 `.gitignore`를 따르면서 빠지는 파일이다.

### Task 1.2: README 설치 절

**Files:** Modify: `README.md` (:62-105 설치, :141-146 Update, Uninstall 절, :176-205 기여자 절), `.github/workflows/test.yml` (:17)

- [ ] Step 1:
  - "1. Install the CLI"를 `uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git`로 바꾼다. `superclaude`를 찾을 수 없으면 `uv tool update-shell`을 실행하라고 덧붙인다(설치기가 이미 같은 안내를 출력함, `install_components.py:337-340`).
  - Update 절: `uv tool upgrade superclaude` 다음 `superclaude update --scope <s>`.
  - Uninstall 절 끝에 `uv tool uninstall superclaude`.
  - `git clone` + `make deploy`는 기여자 절로만 옮긴다.
  - `4.20.0+ajitta` 문자열과 36/23 개수 표기는 그대로 둔다(`test_version_consistency.py:153`, README count lint).
- [ ] Step 2: `.github/workflows/test.yml:17` matrix에 `"3.13"`을 추가한다. README가 `-p 3.13`을 안내하므로 그 버전을 CI가 검사해야 한다. lint job(:68, `"3.10"`)은 바꾸지 않는다.
- [ ] Step 3: `uv run pytest`가 exit 0인지 확인한다.
- [ ] Step 4: `make format` 후 커밋한다: `docs: install the CLI from git with uv tool, no clone needed`. matrix 변경도 같은 커밋에 넣고, 본문에 3.13을 추가한 이유를 한 줄 적는다.
- [ ] Step 5: `git checkout master && git merge --no-ff docs/uv-tool-install -m "…"`를 한 명령으로 실행하고 push한 뒤 CI를 확인한다(gotcha `editable-tool-branch-switch`). 3.13 job이 새로 생기므로 Python 4개 버전 job이 모두 green이어야 한다. 3.13에서만 실패하면 README의 `-p`를 CI가 통과한 가장 높은 버전으로 낮추고 원인을 따로 기록한다.
- [ ] Step 6: push 뒤 실제 `git+https://github.com/ajitta/superclaude.git`로 Task 1.1 Step 1을 한 번 더 실행한다.

## Phase 2: plugin 모드 hook 런타임 (브랜치 `feature/sc-plugin`, 커밋 1개)

- [ ] master에서 `git switch -c feature/sc-plugin`.

### Task 2.1: `plugin_root()`와 `core_inject` hook

**Files:**
- Modify: `src/superclaude/utils/__init__.py` (`claude_base()` :120-147 근처)
- Create: `src/superclaude/scripts/core_inject.py`
- Modify: `src/superclaude/cli/hook_dispatch.py` (:36-55 주석과 `HOOKS`)
- Test: `tests/unit/test_plugin_manifest.py`(신규), `tests/unit/test_hook_dispatch.py`

- [ ] Step 1: 실패하는 테스트를 쓴다(`test_plugin_manifest.py`).
  - `plugin_root()`: `CLAUDE_PLUGIN_ROOT`가 없으면 None. 변수는 있지만 그 안에 `CLAUDE_SC.md`가 없으면 None. 있으면 그 경로를 반환.
  - `core_inject.main(["FLAGS"])`: 루트가 없으면 출력 0바이트, 반환 0.
  - 루트를 `src/superclaude`로 주면 stdout 바이트가 `<!-- {root}/core/FLAGS.md -->\n` + 파일 바이트와 정확히 같다(`capsysbinary`).
  - `CLAUDE_SC.md`의 `@core/*.md` import 이름 집합이 hooks.json의 `core_inject` 인자 집합과 같다.
  - 각 인자의 출력(주석 + 파일)이 10,000자 미만이다.
  - `uv run pytest tests/unit/test_plugin_manifest.py -q` → `ImportError`로 실패해야 한다.
- [ ] Step 2: 최소 구현.
  - `plugin_root() -> Path | None`: `CLAUDE_PLUGIN_ROOT`가 있고 `<root>/CLAUDE_SC.md`가 파일일 때만 `Path(root)`. docstring에 적을 내용: settings hooks에는 이 변수가 없어서 scope 설치에서는 항상 None이다. `CLAUDE_SC.md` 검사는 다른 plugin의 변수가 남아 있어도 경로를 바꾸지 못하게 한다.
  - `core_inject.main(argv, prog=None) -> int`: 루트가 None이면 0. 아니면 이름마다 `sys.stdout.buffer.write`로 주석 한 줄과 `(root / "core" / f"{name}.md").read_bytes()`를 쓴다. stdlib과 `superclaude.utils`만 import한다(click 금지, `test_hook_dispatch.py`가 import 그래프를 검사함).
  - `HOOKS`에 `"core_inject": ("superclaude.scripts.core_inject", True)`. 인자를 받지 않는 hook은 인자를 거부하므로(:96-104) 인자 전달형으로 등록한다. "insight_writer만 인자를 받는다"는 주석(:36-43)을 고친다.
- [ ] Step 3: `test_hook_dispatch.py`를 고친다. "ten hooks" docstring(:55)과 `test_only_insight_writer_takes_arguments`의 이름과 docstring을 바꾼다. 집합 비교는 hooks.json에서 계산하므로 assertion은 그대로 둔다.

### Task 2.2: hooks.json 등록

**Files:** Modify: `src/superclaude/hooks/hooks.json`, `src/superclaude/hooks/README.md`, `src/superclaude/scripts/README.md`, `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` §1

- [ ] Step 1: SessionStart에 matcher `startup|clear|compact` 항목을 하나 추가하고 그 안에 hook 3개를 둔다: `superclaude hook core_inject FLAGS`, `… PRINCIPLES`, `… RULES`. 각각 `timeout: 5`이고, `_comment`는 `[superclaude] plugin only: emits one core file into context (CLAUDE.md is not loaded from plugins); no-op for scope installs`. matcher에서 `resume`을 빼는 것은 `context_reset`(:25-38)과 같다. resume은 이전 대화 기록을 그대로 복원하기 때문이다.
- [ ] Step 2: hooks/README.md의 SessionStart 목록과 scripts/README.md 표에 `core_inject` 행을 추가한다.
- [ ] Step 3: 02_component_and_delivery_map.md §1(:31-32)의 숫자를 다시 센다. 예상값은 hook 스크립트 10→11, 등록 14→17, Python 모듈 52→53이다.
  - 모듈 수: `uv run python -c "from pathlib import Path; print(len(list(Path('src/superclaude').rglob('*.py'))))"`
- [ ] Step 4: `uv run pytest tests/unit/test_hook_dispatch.py tests/unit/test_plugin_manifest.py tests/unit/test_codex_component_map.py tests/unit/test_install_settings.py -q`

### Task 2.3: context_loader가 plugin 루트를 읽음

**Files:** Modify: `src/superclaude/scripts/context_loader.py` (:77-96 `_get_base_path`). Test: `tests/unit/test_context_loader.py`

- [ ] Step 1: 실패하는 테스트를 쓴다. :340, :361과 같은 subprocess 방식으로 실행한다. `BASE_PATH`가 import할 때 계산되므로 subprocess가 필요하다.
  - 환경: `CLAUDE_PLUGIN_ROOT=<CONTENT_ROOT>`, `SUPERCLAUDE_PATH`는 제거, `CLAUDE_PROJECT_DIR=<tmp>`, `<tmp>/.claude/superclaude` 없음.
  - 기대: `--brainstorm` 프롬프트의 출력에 `MODE_Brainstorming`이 있다.
- [ ] Step 2: 우선순위를 `SUPERCLAUDE_PATH` → `plugin_root()` → `claude_base() / "superclaude"`로 바꾸고 docstring의 우선순위 목록도 맞춘다. 지금 docstring은 이미 실제 동작과 다르다. `_command_dirs()`(:484-486)는 바꾸지 않는다. `BASE_PATH / "commands"`가 plugin의 `commands/`를 그대로 찾는다.
- [ ] Step 3: `uv run pytest tests/unit/test_context_loader.py -q`

### Task 2.4: session_init의 plugin 상태 줄

**Files:** Modify: `src/superclaude/scripts/session_init.py` (:18-56 `get_install_status`). Test: `tests/unit/test_session_init.py` (`TestInstallStatusLine`)

- [ ] Step 1: 실패하는 테스트를 쓴다. 고정 방법: `CLAUDE_PROJECT_DIR=<tmp>`를 설정하고 `<tmp>/.claude/superclaude` marker를 만들어 `claude_base()`가 개발자 홈으로 빠지지 않게 한다(gotcha `test-anchor-env`). plugin 루트는 `CLAUDE_SC.md`와 `.claude-plugin/plugin.json`이 있는 tmp 디렉터리로 한다.
  - plugin 모드이고 scope 설치가 없으면: "no commands installed"가 없고 plugin 버전 줄이 나온다.
  - `<tmp>/.claude/commands/sc/x.md`가 있으면 중복 설치 경고가 나온다. 경고에는 scope와 두 가지 해결 명령(`superclaude uninstall --scope <s>` 또는 `/plugin uninstall sc`)을 적는다.
  - plugin.json 버전이 `superclaude.__version__`과 다르면 버전 불일치 경고가 나오고 `uv tool upgrade superclaude`를 안내한다.
- [ ] Step 2: `plugin_root()`가 있으면 위 분기를 타고, 없으면 지금 동작을 그대로 둔다. 개수 셈은 지금의 `_count`를 다시 쓴다. 지금은 "no commands installed — run `superclaude install`"(:49-51)이 나와 사용자를 중복 설치로 이끈다.
  - 한계: 4.20.0 이하 CLI에는 이 분기가 없어서 불일치를 알릴 수 없다. 그래서 README에 최소 CLI 버전을 적는다(Task 3.3).
- [ ] Step 3: `uv run pytest` exit 0, `make format` 후 커밋한다: `feat(hooks): run as the sc plugin — core_inject, plugin content root, plugin status line`

## Phase 3: plugin manifest와 marketplace (커밋 1개)

### Task 3.1: manifest 테스트

**Files:** Test: `tests/unit/test_plugin_manifest.py`, `tests/unit/test_portable_skills.py` (:215), `tests/unit/test_version_consistency.py`

- [ ] Step 1: 실패하는 테스트를 쓴다.
  - `src/superclaude/.claude-plugin/plugin.json`의 `name`은 `sc`다.
  - `commands`, `agents`, `outputStyles` 목록이 `install_paths.shipped_md_names()`(:54-56)의 `./commands/<f>`, `./agents/<f>`, `./output-styles/<f>`와 같다. README.md는 빠진다.
  - `hooks` 키가 없다. 있으면 `hooks/hooks.json`과 함께 두 번 로드된다.
  - marketplace의 `sc` 항목은 `source == "./src/superclaude"`이고 `version`이 없다.
  - `test_version_consistency.py`: plugin.json `version`이 pyproject 버전과 같다.
  - `test_portable_skills.py:215`: portable skill 집합과 비교하는 대상을 `set(entries) - {"sc"}`로 바꾼다.

### Task 3.2: manifest와 marketplace 작성

**Files:** Create: `src/superclaude/.claude-plugin/plugin.json`. Modify: `.claude-plugin/marketplace.json`

- [ ] Step 1: plugin.json을 `portable-skills/plugin-manifests/*.json` 형식으로 쓴다.
  - 필드: `name: "sc"`, `displayName: "SuperClaude"`, `version`(현재 pyproject 값), `description`, `author {name, url}`, `license`, `homepage`.
  - `commands`, `agents`, `outputStyles`는 경로를 명시한 배열로 쓴다. 기본 폴더 안의 경로라서 "Default folder ignored" 경고가 나지 않는다.
- [ ] Step 2: marketplace에 `{"name": "sc", "source": "./src/superclaude", "description": …, "category": "development"}`를 추가한다. 최상위 description은 SuperClaude plugin과 Socratic skill 2개를 함께 소개하도록 새로 쓴다.
- [ ] Step 3: `uv run pytest tests/unit/test_plugin_manifest.py tests/unit/test_portable_skills.py tests/unit/test_version_consistency.py -q`
- [ ] Step 4: hatchling이 wheel에 `.claude-plugin/`을 넣어도 문제는 없다. 설치는 `COMPONENTS`만 복사하기 때문이다(`install_paths.py:27-38`). 확인만 하고 지나간다.

### Task 3.3: plugin에서 깨지는 content 경로와 README

**Files:** Modify: `src/superclaude/commands/init.md` (:76), `src/superclaude/core/RULES.md` (:32), `README.md`

- [ ] Step 1: `init.md:76` 템플릿 경로 뒤에 `(plugin install: ${CLAUDE_PLUGIN_ROOT}/templates/docs-scaffold/)`를 덧붙인다. plugin에서는 치환되고, scope 설치에서는 이름표가 붙은 글자 그대로 남는다.
- [ ] Step 2: `RULES.md:32` on_demand_modules note의 "installed under .claude/superclaude/core/rules/"를 "under core/rules/ beside this RULES.md"로 바꾼다. 이 파일의 경로는 scope 설치에서는 CLAUDE.md import 머리말이, plugin에서는 core_inject 주석 줄이 알려준다. always-loaded 파일이므로 문장을 늘리지 않는다.
- [ ] Step 3: README에 "Install as a Claude Code plugin" 절을 추가한다.
  - 선행 조건: Phase 1의 CLI. 최소 버전은 core_inject가 들어간 릴리스(4.21.0+ajitta).
  - 설치: `claude plugin marketplace add ajitta/superclaude` 다음 `claude plugin install sc@ajitta-socratic`(또는 `/plugin`).
  - plugin과 scope 설치 중 하나만 쓴다. 둘 다 있으면 hook이 두 번 돈다.
  - agent memory는 `memory: project`라서 프로젝트별로 저장된다.
  - `doctor`, `verify-drift`, `uninstall`은 scope 설치 전용이다.
  - 서드파티 marketplace는 자동 업데이트가 꺼져 있다. `/plugin`에서 켜거나 `claude plugin marketplace update`를 실행한다.
  - plugin과 CLI는 함께 올린다(`uv tool upgrade superclaude`).
- [ ] Step 4: `uv run pytest` exit 0, `make format` 후 커밋한다: `feat(plugin): ship src/superclaude as the sc plugin from the repo marketplace`

## Phase 4: 실제 Claude Code에서 확인 (커밋 없음)

저장소 밖 scratch 디렉터리에서 실행한다. 저장소 안에서 실행하면 모델이 이 계획 문서를 읽고 따라 하므로 결과가 오염된다(gotcha `probe-observer-effect`).

먼저 두 가지를 확인한다. PATH의 `superclaude`가 이 브랜치의 editable 설치여야 한다(`superclaude hook --help`에 `core_inject`가 있어야 함). `superclaude doctor --scope user`로 user scope 설치가 없는 것도 확인한다.

### Task 4.1: validate와 로딩

- [ ] `claude plugin validate src/superclaude`, `claude plugin validate .`(marketplace).
  - `_comment` 키가 거부되면 plugin 경로에서 그 키를 빼는 방법을 그때 정한다. 소유 판별은 `CONSOLE_HOOK_RE`가 하므로 `_comment`가 없어도 된다(`utils/__init__.py:155-223`).
- [ ] `claude -p --plugin-dir "$REPO/src/superclaude" --output-format stream-json --verbose --disallowedTools "Read Bash Glob Grep" "Quote the <mission> line of the flags component in your context, or say NONE."`
  - init 이벤트: `sc:*` 명령 36개, `sc:README` 없음, `sc:*` agent 23개, output style `sc:Plain Language`. init 이벤트에 목록이 나오지 않으면 대화형 `/help`, `/agents`로 확인한다.
  - SessionStart: core_inject 출력 3개가 비어 있지 않고 각각 10,000자 미만이며, 모델이 FLAGS mission을 인용한다.
- [ ] `/sc:help`가 실행되고, `--brainstorm …` 프롬프트의 UserPromptSubmit 출력에 `MODE_Brainstorming`이 있다.
- [ ] Windows hook PATH: 위 hook 출력이 나오면 Git Bash hook shell이 `superclaude`를 찾은 것이다. 이 PATH는 지금까지 측정한 적이 없다(gotcha `hook-path-inherits-launch-shell`). 결과를 gotcha에 적는다.

### Task 4.2: agent 이름 해석

- [ ] `claude -p --plugin-dir … 'Call the Agent tool once with subagent_type "repo-index" and prompt "reply OK"; print the tool result verbatim.'`를 실행한다.
  - 통과하면 content의 bare 이름 170곳은 그대로 둔다.
  - "not found"면 170곳은 고치지 않는다. 대신 core_inject의 RULES 주석 줄에 "SuperClaude agents are `sc:<name>` in plugin mode"를 넣고, Task 2.1 테스트의 기대 바이트를 함께 고친다.

### Task 4.3: scope 설치에서는 아무것도 안 함

- [ ] scratch git 프로젝트에서 `superclaude install --scope local` 다음 `claude -p --output-format stream-json --verbose "hi"`를 실행한다. core_inject hook은 돌지만 출력이 비어 있어야 한다. 이것으로 settings hooks에 `CLAUDE_PLUGIN_ROOT`가 없다는 것을 확인한다. 끝나면 `superclaude uninstall --scope local -y`.

### Task 4.4: 병합과 실제 설치

- [ ] `git checkout master && git merge --no-ff feature/sc-plugin -m "…"`(한 명령), push, CI 확인.
- [ ] `claude plugin marketplace update ajitta-socratic && claude plugin install sc@ajitta-socratic`를 실행한다. 이 개발 저장소는 local scope 설치가 있으므로 새 세션에서 session_init 중복 경고가 나와야 한다. 확인한 뒤 plugin을 user scope에 둘지는 사용자가 정한다.

## Phase 5: 4.21.0+ajitta 릴리스 (브랜치 `chore/version-4.21.0`)

core_inject가 없는 4.20.0 CLI와 구분하려면 버전을 올려야 한다.

- [ ] `pyproject.toml`, `src/superclaude/__init__.py`, README, `commands/sc.md`, `src/superclaude/.claude-plugin/plugin.json`을 `4.21.0+ajitta`로 바꾼다.
- [ ] CHANGELOG.md에 4.21.0 항목을 쓴다. Added: git URL로 CLI 설치(README), `sc` plugin, `core_inject`. Upgrade notes: plugin 사용자는 CLI 4.21.0 이상 필요, scope 설치 사용자는 `superclaude update --scope <s>`(새 hook 등록).
- [ ] `uv run pytest` exit 0, 병합, push, CI 확인, `superclaude update --scope local`로 개발 저장소 재동기화.

## 위험

| 위험 | 영향 | 대응 |
|---|---|---|
| Windows hook shell PATH에 `superclaude`가 없음 | plugin hooks가 exit 127로 조용히 빠짐(core 없음) | Task 4.1에서 측정. README 선행 조건에 `uv tool update-shell` |
| 4.20.0 이하 CLI + plugin | `core_inject`를 몰라 exit 1, core 없음, 불일치 경고도 없음 | README 최소 버전, Phase 5 버전 bump |
| plugin과 scope 설치 중복 | hook 두 번 실행(loop_guard 임계값이 사실상 절반, core 두 번, Stop 알림 두 번) | session_init 경고, README "하나만" |
| bare agent 이름이 `sc:<name>`으로 풀리지 않음 | `/sc:*` 위임 실패 | Task 4.2 probe, 실패 시 core_inject 한 줄 |
| `_comment`, `once` 키 | validate 경고나 거부 | Task 4.1에서 판단. `once`는 settings에서도 무시되므로 동작은 같음 |
| plugin 캐시에 `cli/`, `scripts/*.py`도 복사됨 | 용량만 늘고 실행되지 않음(hook은 uv tool 패키지가 실행) | 없음 |
| SessionStart `resume`에 core 재주입 안 함 | resume 뒤 core가 빠질 수 있음(기록 복원 방식에 따라 다름) | Task 4.1 뒤 `claude -p --resume`으로 확인. 빠지면 matcher에 `resume` 추가 |

## 완료 기준

- 1단계: README의 사용자 설치 경로에 clone이 없다. scratch에서 `git+https` 설치 → `superclaude install`의 결과가 명령 36개, agent 23개, doctor 통과다. `uv run pytest` exit 0, CI green(README가 안내하는 3.13 포함).
- 2단계: `claude plugin validate`가 통과한다. `--plugin-dir` probe에서 명령 36개(README 없음), agent 23개, core 3파일 주입, brainstorm mode 주입, agent 위임이 확인된다. scope 설치에서 core_inject 출력이 비어 있다. `uv run pytest` exit 0, CI green.
- 릴리스: 4.21.0+ajitta CHANGELOG 항목과 CI green.
