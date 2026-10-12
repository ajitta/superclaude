---
status: complete
revised: 2026-10-12
---

# Phase B: MCP 문서, 주입, 플래그, fallback

Index: [05-plan.md](./05-plan.md). 결정 근거: 01-discovery Q4·Q5·P3·P9.

### Task B1: 실패하는 테스트

**Files:** Modify: `tests/unit/test_context_loader.py` (MCP_Context7.md 제거 확인 테스트 옆, 현재 `:686-693`)

- [x] Step 1: Context7 선례와 같은 모양의 테스트를 추가한다
  - `mcp/MCP_Serena.md` 파일이 없다
  - 그 경로가 `TIER_0_MAP`, `INSTRUCTION_MAP`, `TRIGGER_MAP`, `COMPOSITE_FLAGS`의 어느 값에도 없다
  - `"serena"`가 `VALID_FLAGS`, `superclaude.hooks.mcp_fallback.MCP_FALLBACKS`, `superclaude.utils.CURRENT_MCP_SERVERS`에 없다
  - `resolve_flags("analyze --serena x")` → `("analyze --serena x", [])`
- [x] Step 2: `uv run pytest tests/unit/test_context_loader.py -k removed -v` → FAIL

### Task B2: 문서 삭제와 loader

**Files:**
- Delete: `src/superclaude/mcp/MCP_Serena.md`
- Modify: `src/superclaude/scripts/context_loader.py:13,110-114,200,203,210-213,216-224,243,357,702,870-871`
- Modify: `src/superclaude/hooks/mcp_fallback.py:31`, `src/superclaude/utils/__init__.py:421`

- [x] Step 3: `git rm src/superclaude/mcp/MCP_Serena.md`
- [x] Step 4: context_loader 편집
  - `:13` 모듈 docstring: "(Tavily gets a Tier 1 INSTRUCTION_MAP string due to behavioral patterns)"
  - `:110-114`: TRIGGER_MAP의 해당 행 전체 삭제. `/sc:load`, `/sc:save`, `lsp`, `symbol ops` 키워드는 더 이상 아무 문서도 주입하지 않는다
  - `:200`: `--frontend-verify` 목록에서 해당 항목 삭제 (Playwright + DevTools만 남음)
  - `:203`: `--all-mcp` 목록에서 해당 항목 삭제
  - `:210-213`, `:243` 주석: "Behavioral MCPs (Tavily)"로
  - `:216-224`: INSTRUCTION_MAP의 해당 항목 삭제
  - `:357`: VALID_FLAGS에서 `"serena"` 삭제
  - `:702` 주석 예시: `"mcp/MCP_Tavily.md"`
  - `:870-871`: 삭제된 directive를 설명하는 주석 두 줄 삭제
- [x] Step 5: mcp_fallback `:31` 항목 삭제. utils `:421` `CURRENT_MCP_SERVERS`에서 `"serena"` 삭제. 기존 사용자의 fallback ledger에 남은 항목은 기존 `prune_fallback_ledger`가 roster 밖이라 지운다

### Task B3: 플래그와 나머지 콘텐츠

**Files:** Modify
- `src/superclaude/core/FLAGS.md:19,23`
- `src/superclaude/mcp/MCP_Playwright.md:38`, `src/superclaude/mcp/MCP_Chrome-DevTools.md:24`, `src/superclaude/mcp/README.md:61`
- `src/superclaude/commands/recommend.md:42`
- `src/superclaude/cli/main.py:968,980`
- `docs/codex/prompting_session_raw/02_component_and_delivery_map.md:29`

- [x] Step 6: 편집
  - FLAGS `:19` 줄 삭제. `:23` → `--frontend-verify: UI test, frontend debug → Playwright + DevTools`
  - MCP_Playwright `:38` → `- Frontend-Verify (--frontend-verify): Playwright:interaction + DevTools:metrics.` / MCP_Chrome-DevTools `:24` → `... Playwright:interact + DevTools:profile.`
  - mcp/README `:61` 표 행 → `| --frontend-verify | Playwright + DevTools |`
  - recommend `:42`: python 행 삭제 (그 목록에 남은 행이 python을 다른 플래그로 다루지 않으면 그대로 둔다)
  - cli/main.py `:968` docstring 예시 → `superclaude context explain "--tavily research this"`, `:980` → `'PROMPT is required, e.g. "--tavily research this"'`
  - component map `:29`: `mcp/MCP_*.md | 4` → `3`

### Task B4: 기존 테스트를 남은 서버로 옮기기

**Files:** Modify
- `tests/unit/test_context_loader.py:71-72,98-99,111,134,146,161,200-205,272-277,454`
- `tests/unit/test_cli_context.py:134-151,214,226,236-288,302,367`
- `tests/unit/test_mcp_fallback.py:89,151-152,168,185-194`
- `tests/integration/test_cross_directory_refs.py:82`

- [x] Step 7: 편집
  - test_context_loader
    - `resolve_flags` 예시(`:71-72`, `:98-99`, `:111`)와 `:454` PROMPT: `--serena` → `--tavily`
    - `:134` Tier 1 목록, `:146` docstring, `:161` verbose tier 검사: 해당 항목을 지우고 `mcp/MCP_Tavily.md`로 같은 검사 유지
    - `:200-205` 해당 서버의 INSTRUCTION_MAP 내용 테스트 삭제
    - `:272-277` `--frontend-verify` 기대 집합에서 해당 항목 삭제, docstring "Playwright + DevTools"
  - test_cli_context
    - `--serena rename ...` → `--tavily research ...`, 기대 경로 `mcp/MCP_Tavily.md`, 기대 문자열 `--tavily`
    - `:214`, `:226` `--serena --play` → `--tavily --play`
    - `:302`, `:367` 캐시 fixture 값 → `mcp/MCP_Tavily.md`
  - test_mcp_fallback
    - `:89` 기대 목록에서 해당 항목 삭제
    - `:151-152`, `:168` ledger fixture 서버 이름 → `tavily`
    - `:185-194` `test_retired_servers_are_dropped`: ledger를 `{"tavily", "serena", "magic", "morphllm"}`로 두고 결과가 `{"tavily"}`인지 본다. 기존 사용자 ledger에서 이제 은퇴한 서버가 지워지는 것을 이 테스트가 고정한다
  - test_cross_directory_refs `:82`: `EXPECTED_MCP_DOCS`에서 해당 항목 삭제
- [x] Step 8: `git grep -n -i "serena" -- src/superclaude/scripts src/superclaude/hooks src/superclaude/utils src/superclaude/core/FLAGS.md src/superclaude/mcp` → `mcp/README.md`의 설치 표·Last verified 줄만 남는다 (Phase C에서 처리)

### Task B5: 검증과 커밋

- [x] Step 9: `uv run pytest tests/unit/test_context_loader.py tests/unit/test_cli_context.py tests/unit/test_mcp_fallback.py tests/integration/test_cross_directory_refs.py tests/unit/test_codex_component_map.py -v` → PASS
- [x] Step 10: `uv run pytest tests/unit/scripts -o addopts=` exit 0 (context_loader는 `src/superclaude/scripts/`)
- [x] Step 11: `uv run superclaude context explain "/sc:load"`와 `uv run superclaude context explain "--serena rename x"` → `mcp/` 파일 주입 없음
- [x] Step 12: `uv run pytest` exit 0, `make lint` 통과
- [x] Step 13: 커밋 `refactor(mcp): drop the symbol-server doc, its flag, injection and fallback hint`

## Deviations

- Extra file `README.md:28,519`: the MCP count in the badge table and the docs table went 4 → 3. `tests/unit/test_version_consistency.py` ties both to the tree, and no phase listed them.
- Extra tests in `tests/unit/test_context_loader.py` whose counts followed the deleted doc: `test_all_mcp_includes_3_servers` (was 4), `test_frontend_verify_includes_2_servers` (was 3), `test_trigger_map_mcp_count` (4 → 3), and the class comment "3 total: 2 tool + 1 behavioral".
- `test_context_loader.py:71-72`: that example already had `--tavily`, so it became `"analyze --tavily --c7"` instead of a duplicate flag.
- `context_loader.py:14` docstring counts were not changed in this phase. `--frontend-verify (3 MCP)` was right before it and went stale when the server left; `--all-mcp (6 MCP)` was already off. Both fixed in Phase F (Task F3).
