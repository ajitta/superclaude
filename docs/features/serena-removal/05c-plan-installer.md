---
status: draft
revised: 2026-10-12
---

# Phase C: 설치기

Index: [05-plan.md](./05-plan.md). 결정 근거: 01-discovery Q3·P1·P2·P6·Open questions 3.

### Task C1: 실패하는 테스트

**Files:** Modify: `tests/unit/test_install_mcp_prerequisites.py:19,56-94`. Create: `tests/unit/test_install_mcp_interactive.py`

- [ ] Step 1: 기존 테스트 정리
  - `:19` stand-in docstring: "claude succeeds, node reports a version" (uv와 바이너리 점검 언급 삭제)
  - `:56-66` `test_every_registry_server_except_..._needs_node` → `test_every_registry_server_needs_node` (기대 dict에서 해당 항목 삭제)
  - `:69-79` 해당 서버만 고른 경우의 테스트 두 개 삭제
  - `:94` parametrize의 `["serena", "chrome-devtools"]` → `["chrome-devtools"]`
  - 새 테스트 `test_prerequisites_never_probe_uv`: 모든 서버를 골라 `check_prerequisites`를 부르고, stand-in에 들어온 argv 중 `uv`로 시작하는 호출이 없다
- [ ] Step 2: 새 파일 `test_install_mcp_interactive.py`
  - `test_registry_has_no_category_split`: `MCP_SERVERS`의 어떤 항목에도 `"category"` 키가 없다
  - `test_registry_has_no_removed_server`: `"serena" not in MCP_SERVERS`
  - `test_interactive_menu_lists_every_server_without_default`: `click.prompt`를 monkeypatch해서 kwargs를 기록하고 `""`를 돌려준다. `install_mcp_servers(selected_servers=None, dry_run=True)` → `(False, "No servers selected")`. 기록된 `default`가 `""`이고, 출력(capsys)에 `MCP_SERVERS`의 모든 `name`이 나온다
  - `test_interactive_selection_installs_only_chosen_numbers`: prompt가 `"1"`을 돌려주고 `install_mcp_server`를 monkeypatch해 호출을 기록한다. 첫 번째 서버만 설치 호출된다
- [ ] Step 3: `uv run pytest tests/unit/test_install_mcp_prerequisites.py tests/unit/test_install_mcp_interactive.py -v` → 새 테스트 FAIL

### Task C2: install_mcp.py

**Files:** Modify: `src/superclaude/cli/install_mcp.py:22-26,43-50,60,70,76,172-177,210-241,518-552,588-638,644`

- [ ] Step 4: 편집
  - `:22-26` 헤더 주석의 `category` 설명 블록 삭제
  - `:43-50` 해당 서버 항목 삭제. `:60,70,76`의 `"category": "plugin"` 줄 삭제
  - `check_prerequisites` docstring `:172-177`: "Checks are scoped to the selection: the Node.js check runs only when an npm-based server is selected." `:210-241` 해당 서버 전용 점검 블록 삭제
  - `list_available_servers` `:518-552`: `by_category`·제목을 없애고 서버마다 이름·설치 상태·설명을 한 목록으로 출력. docstring "List all available MCP servers." 마지막 `Total` 줄 유지
  - 대화형 선택 `:588-638`: 모든 서버를 `enumerate(MCP_SERVERS.values(), 1)`로 번호 매겨 출력 (API key 표시 유지). `click.prompt("Select servers to install (comma-separated numbers; empty to cancel)", default="", show_default=False)`. 빈 입력 → `servers_to_install = []`. 그 밖에는 기존과 같은 정수 파싱을 전체 목록 기준으로. plugin 안내 블록과 `0 = core 전부` 분기 삭제
  - `:644` 주석: "Check prerequisites (after selection so per-server checks stay scoped)"
- [ ] Step 5: `src/superclaude/cli/install_settings.py:391` 주석 "Third-party installers (e.g., ...)"에서 예시 괄호를 지운다 (동작 변화 없음, P8 허용 목록을 비우기 위함)

### Task C3: 설치 문서

**Files:**
- Modify: `src/superclaude/mcp/README.md:5-23,55`
- Delete: `docs/troubleshooting/serena-installation.md`
- Modify: `README.md:103-116,515`, `docs/PRD.md:56-58`

- [ ] Step 6: mcp/README
  - `:5-7` Content Delivery 문단: "Servers in the table below install via `superclaude mcp`: the interactive picker lists them all and installs only the numbers entered, or name them with `--servers`. Context7 + Tavily are externally provided — see their sections below."
  - `:11-23` Core 표와 Plugin 표를 "### Servers (`superclaude mcp`)" 아래 한 표로 합친다 (Playwright, Chrome DevTools, Tavily 행 그대로)
  - `:55` Last verified 줄: PyPI 언급과 두 번째 `curl` 예시를 지운다 (npm 3개만)
- [ ] Step 7: `git rm docs/troubleshooting/serena-installation.md`. `docs/troubleshooting/`에 다른 파일이 없으면 디렉터리는 git에서 사라진다
- [ ] Step 8: README
  - `:105` 사전 설치 안내 callout 삭제
  - `:107-114` 코드 블록에서 해당 서버 등록 줄 삭제. `superclaude mcp` 주석은 "interactive picker (installs only what you pick; default scope: user)"
  - `:116` 문제 해결 callout 삭제, `:515` 문제 해결 표 행 삭제
- [ ] Step 9: PRD `:56-58` → "6. **Curated MCP registration** — `superclaude mcp` writes server entries at the chosen scope for a small managed set. Nothing is pre-selected or auto-enabled."
- [ ] Step 10: `git grep -n "serena-installation"` → 출력 없음 (과거 기록 문서에 남은 링크가 있으면 그대로 둔다; P7)

### Task C4: 검증과 커밋

- [ ] Step 11: `uv run pytest tests/unit/test_install_mcp_prerequisites.py tests/unit/test_install_mcp_interactive.py tests/unit/test_cross_references.py -v` → PASS
- [ ] Step 12: `uv run superclaude mcp --list` → 제목 없는 한 목록. `printf '\n' | uv run superclaude mcp --dry-run` → 모든 서버 번호 목록 + `No servers selected`, exit 1
- [ ] Step 13: `uv run pytest` exit 0, `make lint` 통과
- [ ] Step 14: 커밋 `refactor(mcp): stop registering the symbol server; the picker pre-selects nothing`
