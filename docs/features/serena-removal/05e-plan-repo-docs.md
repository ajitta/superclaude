---
status: draft
revised: 2026-10-12
---

# Phase E: 레포 문서와 local scope 재동기화

Index: [05-plan.md](./05-plan.md). 결정 근거: 01-discovery P4·P5·P6·P7, index Deviations P4.

새 동작이 없으므로 실패하는 테스트 대신 grep 검사가 완료 기준이다.

### Task E1: 사용자·작업 문서

**Files:** Modify: `README.md:220,341,457-461,499,552,556,589,647`, `SECURITY.md:285`, `AGENTS.md:36`, `docs/reports/PROJECT_INDEX.md:37`

- [ ] Step 1: README
  - `:220` 해당 서버 bullet 삭제
  - `:341` "Available servers" 목록의 해당 bullet 삭제
  - `:457-461` 블록: 제목 "Research memory across sessions:", "Serena optional ..." 줄 삭제, 저장 위치 줄 추가 "Saved to `.claude/memories/` (committed) and Claude auto memory"
  - `:499` "Integrated Tool Orchestration" 목록의 해당 bullet 삭제
  - `:552` 플래그 표의 해당 행 삭제. `:556` → "Playwright + DevTools (UI debug)"
  - `:589` 예시: `--serena` 제거 → `/sc:improve src/api/handlers.py --loop --iterations 3`
  - `:647` → "`/sc:load` — Load session context (`.claude/memories/` + auto memory)"
- [ ] Step 2: SECURITY `:285` 해당 줄 삭제
- [ ] Step 3: AGENTS `:36` → "- Session memories live in `.claude/memories/` (committed, written by `/sc:save`, read by `/sc:load`)"
- [ ] Step 4: PROJECT_INDEX `:37` 트리 줄 → `├── .claude/memories/         # committed session memories (/sc:save)`. 트리에서 `.claude/` 아래에 두는 게 맞으면 그 위치로 옮긴다

### Task E2: 레포 규칙

**Files:** Modify: `.claude/rules/mcp-authoring.md:23,77,99` 와 Checklist 4·5번 줄

- [ ] Step 5: 편집
  - `:23` 예시: `` (`mcp/MCP_Tavily.md` → `tavily`) ``
  - `:77` 예시 목록: `tavily`, `playwright`, `chrome-devtools`
  - `:99` 플래그 예시: `` (`--c7`, `--tavily`, …) ``
  - Checklist 4: "Add a row to the `mcp/README.md` server table with flag + one-line mission."
  - Checklist 5: "Register in `cli/install_mcp.py::MCP_SERVERS` when `superclaude mcp` should offer it."

### Task E3: 검증, 커밋, 재동기화

- [ ] Step 6: `git grep -i -l serena -- src/ README.md SECURITY.md AGENTS.md docs/PRD.md docs/reports/ .claude/rules/` → 출력 없음
- [ ] Step 7: `uv run pytest` exit 0, `make lint` 통과
- [ ] Step 8: 커밋 `docs: point memory docs at .claude/memories/ and drop the symbol-server references`
- [ ] Step 9: index의 Proof 1~7을 모두 실행하고 결과를 기록한다
- [ ] Step 10: 이 레포 개발 환경(local scope) 재동기화
  - `superclaude doctor --scope local`로 local install이 있는지 먼저 확인 (gotcha `sync-scope-creates`)
  - 있으면 `superclaude install --force --scope local`. Windows에서 `make sync-local`이 실패할 수 있음 (gotcha `windows-make-sync-broken`)
  - 확인: `.claude/superclaude/core/rules/RULES_QUALITY.md`의 R17이 새 문구다. 남은 `.claude/superclaude/mcp/` 예전 파일은 읽히지 않으므로 그대로 둔다 (index Risks)
