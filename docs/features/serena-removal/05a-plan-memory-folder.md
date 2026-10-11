---
status: draft
revised: 2026-10-12
---

# Phase A: 메모리 폴더

Index: [05-plan.md](./05-plan.md). 결정 근거: 01-discovery Q6·Q7·P10.

### Task A1: 실패하는 테스트

**Files:** Create: `tests/unit/test_session_memory_folder.py`

- [ ] Step 1: 테스트 작성
  - `test_save_and_load_name_the_memory_folder`: `src/superclaude/commands/save.md`와 `load.md` 본문에 `.claude/memories/`가 있다
  - `test_save_and_load_use_no_memory_server_tools`: 두 파일에 `write_memory`, `read_memory`, `list_memories`, `onboarding()`, `.serena`가 없다
  - `test_project_manager_session_keys_live_in_memory_folder`: `agents/project-manager.md`에 `.claude/memories/`가 있고, `pm_context`, `last_session`, `next_actions` 키 이름이 남아 있다
  - `test_memory_folder_is_not_git_excluded`: `superclaude.cli.install_git_exclude._collect_entries(scope)`를 `"local"`과 `"project"`로 부르고, 어떤 항목도 `.claude/memories/probe.md`를 덮지 않는다 (항목이 `/`로 끝나면 prefix 비교, 아니면 정확히 일치 비교)
- [ ] Step 2: `uv run pytest tests/unit/test_session_memory_folder.py -v` → 앞의 세 테스트 FAIL, 네 번째는 지금도 PASS (회귀 가드)

### Task A2: /sc:save

**Files:** Modify: `src/superclaude/commands/save.md:2,7,14,17,36-41,43-50,53-58,84,86`

- [ ] Step 3: 편집
  - `:2` description: "Session lifecycle management with a committed project memory folder (`.claude/memories/`) + Claude auto memory for context persistence. Use ONLY when user explicitly types `/sc:save` — session-end lifecycle action that writes memory files and auto-memory entries. Do NOT auto-trigger on ..." (negative gate 원문 유지)
  - `:7` mission: "Session lifecycle management with a committed project memory folder + Claude auto memory for context persistence"
  - `:14` → `2. Persist (memory folder): Write .claude/memories/session_[date].md (context) → .claude/memories/learnings_[topic].md (insights); flat basename only, no path segments; create the folder when absent`
  - `:17` → `4. Verify: Glob .claude/memories/ + Read MEMORY.md confirms both stores`
  - `<storage>` 첫 줄 → `Memory folder (primary): .claude/memories/ — one markdown file per memory name, committed with the project`
  - `<outputs>` 표 열 제목 `Serena Memory` → `Memory folder` (행 값 그대로)
  - `<tools>` → `- Write/Edit: memory folder + auto memory persistence`, `- Glob: list memory files`, `- Read: verify both stores`
  - `:84` does: "memory folder + auto memory sync, auto-checkpoints, discovery preservation."
  - `:86` fallback: "Memory folder not writable: auto memory only, and tell the user. Ask user for guidance when uncertain."

### Task A3: /sc:load

**Files:** Modify: `src/superclaude/commands/load.md:2,7,12-20,29,33-38,44,60,64,66`

- [ ] Step 4: 편집
  - `:2` description: "Session lifecycle mgmt with the project memory folder (`.claude/memories/`) + Claude auto memory for proj context load. Use ONLY when user explicitly type `/sc:load` — session-start action prime context from memory files + proj state. Do NOT auto-trigger ..." (gate 원문 유지)
  - `:7` mission: "Session lifecycle mgmt with the project memory folder + Claude auto memory for proj context load"
  - `<flow>`를 다음으로 (Initialize 단계 삭제, 번호 다시 매김)
    1. `Load (memory folder): Glob .claude/memories/*.md → Read pm_context, last_session, next_actions when present; folder absent → skip`
    2. `Load (auto memory): MEMORY.md (auto-load) + topic files linked from MEMORY.md`
    3. `Discover: Proj struct + reqs (Glob/Grep/Read)`
    4. `Activate`, 5. `Validate`, 6. `Session Goal (optional)`: 원문 그대로
  - `:29` storage: "Storage locations (memory folder / auto memory / topic files / agent memory): SSOT in /sc:save <storage> — installed sibling commands/sc/save.md."
  - `<tools>` → `- Glob/Read: memory folder + auto memory + proj file analysis`, `- Grep: proj file analysis`, `- Write: Checkpoint create`
  - `:44` 예시 출력: "Current dir + memory folder + auto memory"
  - `:60` gotcha: "dual-persistence: Check both the memory folder and auto memory for full context"
  - `:64` does: "memory folder + auto memory load, cross-session persist, context load."
  - `:66` fallback: "Memory folder absent: auto memory + Read CLAUDE.md/PLANNING.md/TASK.md, Glob for struct. Ask user for guidance when uncertain."
- [ ] Step 5: 다른 파일이 load의 단계를 라벨로 가리키는지 확인: `git grep -n "/sc:load .* step" src/` → Initialize를 가리키는 곳이 있으면 같은 커밋에서 고친다

### Task A4: 메모리를 다루는 나머지 콘텐츠

**Files:** Modify
- `src/superclaude/agents/project-manager.md:22,26,38,71`
- `src/superclaude/commands/analyze.md:53`, `reflect.md:2,46`, `research.md:42`, `help.md:39`, `sc.md:35`, `README.md:18-19`, `brainstorm.md:64`, `roadmap.md:49`
- `src/superclaude/modes/RESEARCH_CONFIG.md:43`, `src/superclaude/mcp/MCP_Tavily.md:22`, `src/superclaude/core/rules/RULES_DOCS.md:43`
- `tests/unit/test_command_structure.py:362` (주석 예시)

- [ ] Step 6: 편집
  - project-manager `:22`: 서버 `read_memory`/`write_memory` 문구를 `.claude/memories/`의 파일 읽기·쓰기로 바꾼다. 예: "Session start: read prior context from `.claude/memories/` (pm_context, last_session, next_actions) ..." / "Session end: persist summary to `.claude/memories/` ..." / "Storage: `.claude/memories/` flat files (same names as the keys); patterns and mistakes stay in docs/memory/." `memory: project` 언급과 키 목록은 유지
  - project-manager `:26`: "persist lesson via Serena `write_memory` or local doc" → "persist lesson to `.claude/memories/` or a local doc"
  - project-manager `:38`: "session summaries persisted to `.claude/memories/`."
  - project-manager `:71` 표 행: "load prior context from `.claude/memories/` and docs/memory/, ..."
  - analyze `:53`: "Glob auto memory + `.claude/memories/` → grep `violated_rule: ...`"
  - reflect `:2`: "Task reflect + validate use Serena MCP analysis." → "Task reflect + validate." (나머지 그대로) / `:46` fallback 삭제 (`<fallback>`은 선택 항목)
  - research `:42`: "- /sc:save: cross-session research memory (`.claude/memories/`)"
  - help `:39`, sc `:35`: "(Serena)" → "(memory folder + auto memory)"
  - commands/README `:18-19`: "via Serena MCP + auto memory" → "via `.claude/memories/` + auto memory"
  - brainstorm `:64`, roadmap `:49` 예시 출력: "Cross-session with Serena" → "Cross-session via /sc:save"
  - RESEARCH_CONFIG `:43`: 해당 표 행 삭제
  - MCP_Tavily `:22`: "→ Serena:store" → "→ /sc:save"
  - RULES_DOCS `:43`: "Serena memory" → "`.claude/memories/` (/sc:save)"
  - test_command_structure `:362` 주석 예시: `("1. Load (memory folder): ..." -> "load")`
- [ ] Step 7: `git grep -n -i serena -- src/superclaude/commands/save.md src/superclaude/commands/load.md` → 출력 없음

### Task A5: 검증과 커밋

- [ ] Step 8: `uv run pytest tests/unit/test_session_memory_folder.py tests/unit/test_command_structure.py tests/unit/test_agent_structure.py -v` → 모두 PASS
- [ ] Step 9: `uv run pytest` exit 0, `make lint` 통과
- [ ] Step 10: 커밋 `refactor(memory): /sc:save and /sc:load use .claude/memories/ plus auto memory`
