---
status: complete
revised: 2026-10-12
---

# Phase E: 레포 문서와 local scope 재동기화

Index: [05-plan.md](./05-plan.md). 결정 근거: 01-discovery P4·P5·P6·P7, index Deviations P4.

새 동작이 없으므로 실패하는 테스트 대신 grep 검사가 완료 기준이다.

### Task E1: 사용자·작업 문서

**Files:** Modify: `README.md:220,341,457-461,499,552,556,589,647`, `SECURITY.md:285`, `AGENTS.md:36`, `docs/reports/PROJECT_INDEX.md:37`

- [x] Step 1: README
  - `:220` 해당 서버 bullet 삭제
  - `:341` "Available servers" 목록의 해당 bullet 삭제
  - `:457-461` 블록: 제목 "Research memory across sessions:", "Serena optional ..." 줄 삭제, 저장 위치 줄 추가 "Saved to `.claude/memories/` (committed) and Claude auto memory"
  - `:499` "Integrated Tool Orchestration" 목록의 해당 bullet 삭제
  - `:552` 플래그 표의 해당 행 삭제. `:556` → "Playwright + DevTools (UI debug)"
  - `:589` 예시: `--serena` 제거 → `/sc:improve src/api/handlers.py --loop --iterations 3`
  - `:647` → "`/sc:load` — Load session context (`.claude/memories/` + auto memory)"
- [x] Step 2: SECURITY `:285` 해당 줄 삭제
- [x] Step 3: AGENTS `:36` → "- Session memories live in `.claude/memories/` (committed, written by `/sc:save`, read by `/sc:load`)"
- [x] Step 4: PROJECT_INDEX `:37` 트리 줄 → `├── .claude/memories/         # committed session memories (/sc:save)`. 트리에서 `.claude/` 아래에 두는 게 맞으면 그 위치로 옮긴다

### Task E2: 레포 규칙

**Files:** Modify: `.claude/rules/mcp-authoring.md:23,77,99` 와 Checklist 4·5번 줄

- [x] Step 5: 편집
  - `:23` 예시: `` (`mcp/MCP_Tavily.md` → `tavily`) ``
  - `:77` 예시 목록: `tavily`, `playwright`, `chrome-devtools`
  - `:99` 플래그 예시: `` (`--c7`, `--tavily`, …) ``
  - Checklist 4: "Add a row to the `mcp/README.md` server table with flag + one-line mission."
  - Checklist 5: "Register in `cli/install_mcp.py::MCP_SERVERS` when `superclaude mcp` should offer it."

### Task E3: 검증, 커밋, 재동기화

- [x] Step 6: `git grep -i -l serena -- src/ README.md SECURITY.md AGENTS.md docs/PRD.md docs/reports/ .claude/rules/` → 출력 없음
- [x] Step 7: `uv run pytest` exit 0, `make lint` 통과
- [x] Step 8: 커밋 `docs: point memory docs at .claude/memories/ and drop the symbol-server references`
- [x] Step 9: index의 Proof 1~7을 모두 실행하고 결과를 기록한다
- [x] Step 10: 이 레포 개발 환경(local scope) 재동기화
  - `superclaude doctor --scope local`로 local install이 있는지 먼저 확인 (gotcha `sync-scope-creates`)
  - 있으면 `superclaude install --force --scope local`. Windows에서 `make sync-local`이 실패할 수 있음 (gotcha `windows-make-sync-broken`)
  - 확인: `.claude/superclaude/core/rules/RULES_QUALITY.md`의 R17이 새 문구다. 남은 `.claude/superclaude/mcp/` 예전 파일은 읽히지 않으므로 그대로 둔다 (index Risks)

## Proof results (Step 9, 2026-10-12, after commit 68771a2c)

1. `git grep -i -l serena -- src/ README.md SECURITY.md AGENTS.md docs/PRD.md docs/reports/ .claude/rules/` → no output, exit 1
2. `uv run pytest` → 2973 passed, 1 skipped. `uv run pytest tests/unit/scripts -o addopts=` → 149 passed. `make lint` → All checks passed!
3. `context explain "/sc:load"` → 1 file, `core/rules/RULES_INTERACTION.md`; no `mcp/` file
4. `context explain "--serena rename x"` → would inject no context files; no warning
5. `superclaude mcp --list` → one list (tavily, playwright, chrome-devtools), no core/plugin headings, `Total: 3 servers available`
6. `printf '\n' | superclaude mcp --dry-run` → servers numbered 1-3, `No servers selected`, exit 1
7. `git check-ignore -v .claude/memories/probe.md` → no output, exit 1

Step 10: `superclaude doctor --scope local` healthy → `superclaude install --force --scope local` (85 installed, 0 failed); installed R17 has the new wording. The installed `.claude/superclaude/mcp/MCP_Serena.md` stays, unread (index Risks).

## Deviations

- E1-E2 edits committed (68771a2c) before Step 9 ran, so Proof 1-7 checked the committed tree; this checklist update is its own commit.
- PROJECT_INDEX `:37`: the new line keeps the old line's spot, directly under `.claude/`.
