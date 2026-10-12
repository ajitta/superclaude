---
status: complete
revised: 2026-10-12
---

# Phase F: 리뷰 발견 수정

Index: [05-plan.md](./05-plan.md). 입력: `master..feature/serena-removal` (a0583fba..02ac4f90) 독립 리뷰의 Important I1~I4와 사용자가 고른 Suggestion 6개. 줄 번호는 `02ac4f90` 기준이며, 각 task는 grep으로 위치를 다시 잡는다.

## Decisions

- I1 가드 확장: 한다. 가드가 이름(`serena`)에 더해 도구 이름 6개 `write_memory`, `read_memory`, `list_memories`, `find_symbol`, `get_symbols_overview`, `find_referencing_symbols`도 막는다. 근거: 리뷰가 찾은 흔적 두 줄은 이름만 보는 가드를 통과했다. `02ac4f90`에서 `src/superclaude/` 안의 해당 토큰은 I1의 두 줄뿐이라 오탐이 없다
- I2 방향: save가 `last_session`/`next_actions`를 쓴다. load가 이름으로 읽는 키(`pm_context`, `last_session`, `next_actions`)는 project-manager 에이전트의 키와 같다. save가 이 두 파일을 쓰면 save·load·project-manager 셋이 같은 이름을 쓴다. `session_[date]`와 `learnings_[topic]`은 이력으로 그대로 남고 load의 Glob이 목록을 보여 준다. `pm_context`는 project-manager가 쓴다
- I3 숫자: docstring 숫자를 `COMPOSITE_FLAGS` 길이에 묶는 테스트를 둔다. 손으로 고친 숫자는 다음 서버 변경 때 다시 낡는다 (`core/rules/RULES_DOCS.md`의 "Pin a derived value to its source")
- 제외 (master부터 있던 문제, 별도 작업): README `:108`/`:326`의 `--servers tavily playwright` 예시, picker의 범위 밖 숫자·중복 처리

### Task F1: 도구 이름 흔적 (I1)

**Files:** Modify: `tests/unit/test_shipped_content_server_neutral.py`, `src/superclaude/core/rules/RULES_QUALITY.md:34`, `src/superclaude/modes/MODE_Task_Management.md:27`

- [x] Step 1: 가드 확장
  - `FORBIDDEN = "serena"`를 토큰 튜플로: `("serena", "write_memory", "read_memory", "list_memories", "find_symbol", "get_symbols_overview", "find_referencing_symbols")`. 줄마다 casefold 후 각 토큰을 검사하고, 실패 메시지는 `path:line: token`
  - 모듈 docstring: 이름뿐 아니라 그 서버의 메모리·심볼 도구 이름도 막는다는 문장 추가
  - 테스트 이름 `test_shipped_content_names_no_server` 유지
- [x] Step 2: `uv run pytest tests/unit/test_shipped_content_server_neutral.py -v` → FAIL, 실패 목록이 정확히 `RULES_QUALITY.md:34`와 `MODE_Task_Management.md:27` 두 줄
- [x] Step 3: 편집
  - RULES_QUALITY `:34` Right 칸: `symbol overview → definition query (targeted Grep when no symbol-aware tool is connected)`. 나머지 칸 그대로
  - MODE_Task_Management `:27` Response 칸: `Load: Glob .claude/memories/ -> read plan -> ID current phase -> resume from last checkpoint`
- [x] Step 4: Step 2 명령 → PASS

### Task F2: save와 load의 메모리 이름 (I2)

**Files:** Modify: `tests/unit/test_session_memory_folder.py`, `src/superclaude/commands/save.md:14,46`, `src/superclaude/agents/project-manager.md:22`

- [x] Step 5: 테스트 `test_every_key_load_reads_has_a_writer` 추가
  - load.md `<flow>` 1단계 줄에서 `Read ` 와 ` when present` 사이의 키 목록을 뽑는다 (지금 `pm_context, last_session, next_actions`). 목록이 비면 실패
  - 각 키가 save.md에 `.claude/memories/<key>.md`로 나오거나, project-manager.md의 `Session end:` 문장에 `.claude/memories/<key>.md`로 나와야 한다
- [x] Step 6: `uv run pytest tests/unit/test_session_memory_folder.py -v` → 새 테스트 FAIL (`pm_context`, `last_session`, `next_actions` 모두 writer 없음)
- [x] Step 7: 편집
  - save `:14` 2단계: `2. Persist (memory folder): Write .claude/memories/session_[date].md (context) → .claude/memories/learnings_[topic].md (insights) → overwrite .claude/memories/last_session.md (this session's summary) and .claude/memories/next_actions.md (open items); flat basename only, no path segments; create the folder when absent`
  - save `<outputs>` session 행의 Memory folder 칸: `session_[date], last_session, next_actions`
  - project-manager `:22` `Session end: persist summary to `.claude/memories/`, review completeness.` → `Session end: persist summary to `.claude/memories/last_session.md`, open items to `.claude/memories/next_actions.md` and project state to `.claude/memories/pm_context.md`, review completeness.` (Memory keys·Storage 문장 그대로)
- [x] Step 8: Step 6 명령 → PASS

### Task F3: 합성 플래그 docstring 숫자 (I3)

**Files:** Modify: `tests/unit/test_context_loader.py` (TestTriggerMapPaths 안), `src/superclaude/scripts/context_loader.py:14`, `docs/features/serena-removal/05b-plan-loader-flag.md` Deviations

- [x] Step 9: 테스트 `test_module_docstring_counts_match_composite_flags` 추가: `context_loader.__doc__`에서 `--frontend-verify (N MCP)`, `--all-mcp (N MCP)`의 N을 정규식으로 뽑아 `len(COMPOSITE_FLAGS[flag])`와 비교. 두 패턴 중 하나라도 못 찾으면 실패
- [x] Step 10: `uv run pytest tests/unit/test_context_loader.py -k docstring_counts -v` → FAIL (3 ≠ 2, 6 ≠ 3)
- [x] Step 11: context_loader `:14` → `- Composite flags: --frontend-verify (2 MCP), --all-mcp (3 MCP)`
- [x] Step 12: 05b Deviations의 "Not changed: the `context_loader.py:14` docstring counts ..." 줄을 바로잡는다: "`context_loader.py:14` docstring counts were not changed in this phase. `--frontend-verify (3 MCP)` was right before it and went stale when the server left; `--all-mcp (6 MCP)` was already off. Both fixed in Phase F (Task F3)."
- [x] Step 13: Step 10 명령 → PASS, `uv run pytest tests/unit/scripts -o addopts=` exit 0

### Task F4: picker 번호 테스트 (I4)

**Files:** Modify: `tests/unit/test_install_mcp_interactive.py`

- [x] Step 14: 테스트 보강
  - `test_interactive_menu_lists_every_server_without_default`: 이름만 보는 루프를 `for i, info in enumerate(install_mcp.MCP_SERVERS.values(), 1): assert f"{i}. {info['name']}" in out`로 바꾸고 `assert prompt_kwargs.get("show_default") is False` 추가
  - 새 테스트 `test_interactive_selection_reaches_the_last_server`: prompt가 `str(len(MCP_SERVERS))`를 돌려주고 `check_prerequisites`·`install_mcp_server`를 stub. 설치 호출이 마지막 서버 하나뿐
- [x] Step 15: 지금 코드에서는 PASS다 (동작은 이미 맞음). 회귀를 잡는지 변이로 확인한다
  - `install_mcp.py`의 메뉴 루프를 첫 서버만 번호를 붙이도록 임시로 고친다 (나머지는 `   - name` 형태) → `uv run pytest tests/unit/test_install_mcp_interactive.py` → 두 테스트 FAIL
  - `git restore src/superclaude/cli/install_mcp.py`로 되돌리고 `git diff --stat src/superclaude/cli/install_mcp.py`가 비었는지 확인 → PASS

### Task F5: 리뷰 Suggestion 6개

**Files:** Modify
- `src/superclaude/mcp/README.md:70`, `src/superclaude/cli/install_mcp.py:37`, `src/superclaude/scripts/context_loader.py:200`, `tests/unit/test_context_loader.py:256`
- `src/superclaude/commands/select-tool.md:27,30,40`, `src/superclaude/modes/MODE_Orchestration.md:17`, `src/superclaude/core/PRINCIPLES.md:19`
- `src/superclaude/mcp/MCP_Tavily.md:22`, `src/superclaude/commands/research.md:42`
- `.claude/rules/agent-authoring.md:157,229-230`
- `src/superclaude/commands/save.md:17`

- [x] Step 16: core/plugin 잔재
  - mcp/README `:70`: "for core servers" → "for the servers `superclaude mcp` offers"
  - install_mcp `:37` 주석: "Tavily MCP is opt-in (plugin):" → "Tavily MCP is optional:"
  - context_loader `:200` 주석: "Playwright/DevTools are plugin-install-only (docs still loaded)" → "docs load whether or not the servers are installed"
  - test_context_loader `:256` docstring: "(1 core + 2 plugin)" → "(Tavily, Playwright, Chrome DevTools)"
- [x] Step 17: 용어 통일 "symbol-aware tool (LSP or code index)"
  - select-tool `:27`: `- Symbol ops: symbol-aware tool (LSP or code index) when connected (rename, references)`
  - select-tool `:30`: `- Threshold >0.6: symbol-aware tool when connected (accuracy)`
  - select-tool `:40` 예시 출력: `Symbol-aware tool (LSP rename) when connected`
  - PRINCIPLES `:19` Right-Altitude 행: Before `"ALWAYS use a symbol-aware tool for ALL code reads"` / After `"Use a symbol-aware tool when exploring unfamiliar code"`
- [x] Step 18: MODE_Orchestration `:17` 포인터와 용어. FLAGS `<mcp>`에는 심볼 항목이 없으므로 예시에서 symbol ops를 포인터 밖으로 뺀다: `full routing in core/FLAGS.md mcp section (e.g., docs → Context7, browser → Playwright, web → Tavily); symbol ops → symbol-aware tool (LSP or code index) when connected`. 괄호 안 나머지 항목은 원문 그대로 둔다
- [x] Step 19: explicit-only 커맨드 가리킴
  - MCP_Tavily `:22`: `→ synthesize → suggest /sc:save.`
  - research `:42`: `- /sc:save (suggest to the user; explicit-only): cross-session research memory (`.claude/memories/`)`
- [x] Step 20: agent-authoring
  - `:157` 템플릿: Proceed 줄에서 Symbolic-First 문장을 빼고 (`- Proceed: actions to do freely.`), 그 바로 다음 줄에 `- Symbolic-First: full or light form (see Code Exploration below).`를 둔다. 실제 에이전트처럼 Proceed와 Ask First 사이의 별도 줄
  - `:229-230` 표의 Tier 칸을 실제 배치로
    - Full: "Reads and changes source (system/backend/frontend architects, python-expert, quality/performance/security engineers, refactoring-expert, root-cause-analyst, repo-index, self-review)"
    - Light: "Touches code to configure, plan, document or teach (devops-architect, requirements-analyst, project-manager, project-initializer, technical-writer, learning-guide, socratic-mentor)"
- [x] Step 21: save `:17`: `4. Verify: Glob .claude/memories/*.md + Read MEMORY.md confirms both stores`

### Task F6: 검증과 커밋

- [x] Step 22: `uv run pytest` exit 0, `uv run pytest tests/unit/scripts -o addopts=` exit 0, `make lint` 통과
- [x] Step 23: 커밋 두 개
  - F1~F4: `fix(serena-removal): guard tool-name traces, align save/load memory keys, pin composite-flag counts, pin picker numbering`
  - F5: `docs(serena-removal): drop core/plugin leftovers and align symbol-aware wording`

## Risks

- 가장 위험한 단계: F2. /sc:save가 매번 `last_session.md`와 `next_actions.md`를 덮어쓴다. 같은 프로젝트를 여러 세션이 동시에 저장하면 마지막 저장이 이긴다. 이력은 `session_[date].md`에 남는다
- F1 가드의 `find_symbol`은 부분 문자열 검사라 `find_symbols` 같은 일반 단어도 막는다. 지금 `src/`에는 없다
- F5 Step 18은 `MODE_Orchestration.md`가 always-loaded가 아닌 mode 파일이라 영향이 작다. 괄호 안 다른 항목을 바꾸지 않는다
- F4 Step 15의 변이는 작업 트리를 잠시 바꾼다. 되돌린 뒤 diff가 비었는지 확인한다

## Alternatives not taken

- I2를 load 쪽에서 해결 (load가 최신 `session_*`, `learnings_*`, `context_*`도 읽음): project-manager 키와 save 이름이 두 체계로 남는다
- 가드에 `onboarding` 추가: "first-session onboarding" 같은 일반 영어와 충돌한다
- R17의 "(LSP or code-index MCP)"까지 통일: 사용자가 고른 범위(select-tool, MODE_Orchestration, PRINCIPLES)에 없다. 의미 차이가 없어 그대로 둔다
- docstring 숫자만 손으로 고치기: 다음 서버 변경 때 다시 낡는다

## Proof

1. `uv run pytest tests/unit/test_shipped_content_server_neutral.py tests/unit/test_session_memory_folder.py tests/unit/test_install_mcp_interactive.py -v` → PASS
2. `uv run pytest tests/unit/test_context_loader.py -k docstring_counts -v` → PASS
3. `git grep -n -E "write_memory|read_memory|list_memories|find_symbol|get_symbols_overview|find_referencing_symbols" -- src/` → 출력 없음
4. `git grep -n -i -E "core servers|opt-in \(plugin\)|plugin-install-only|1 core \+ 2 plugin" -- src/ tests/unit/test_context_loader.py` → 출력 없음
5. `uv run pytest` exit 0, `uv run pytest tests/unit/scripts -o addopts=` exit 0, `make lint` → All checks passed!

## Deviations

- Step 15: the display-only mutation (only server 1 numbered) fails only the menu test, because selection indexing does not read the menu text. A second mutation (selection cut to the first server) failed `test_interactive_selection_reaches_the_last_server` as well (2 failed, 3 passed). Both were reverted with `git restore`, and the `:37` comment edit was made after the restore.
- Step 10: the new test collects both mismatches and asserts once, so its failure shows 3≠2 and 6≠3 together.
- Step 18: the parenthesis keeps its original items (`web → Tavily skills, perf → DevTools`) per the step's "원문 그대로" note; the plan's sample text had shortened it to `web → Tavily`.
- Step 20: the Tier cells hold the plan strings without a "Full:"/"Light:" prefix, since the Directive column already starts with those words. The lists match the 11 full and 7 light agents.
- Step 23: F1-F4 and F5 were split at hunk level where a file had both (`save.md`, `context_loader.py`, `test_context_loader.py`); the F1-F4 commit passed the full suite on its own.
- W1 (re-review): Step 5의 OR 조건을 키별 소유자 검사로 강화. save.md는 load가 읽는 키 중 `pm_context`를 뺀 전부를, project-manager의 Session end 문장은 `pm_context`를 쓴다 (테스트 안 `PROJECT_MANAGER_ONLY_KEYS = {"pm_context"}`). save.md에서 `last_session`/`next_actions` 쓰기를 뺀 메모리 변이로 새 테스트 FAIL 확인 (이전 OR 조건은 PASS).
