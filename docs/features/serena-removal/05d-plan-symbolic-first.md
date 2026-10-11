---
status: draft
revised: 2026-10-12
---

# Phase D: Symbolic-First 도구 중립화와 가드

Index: [05-plan.md](./05-plan.md). 결정 근거: 01-discovery Q2·P5·P8. 문구는 index의 Shared rules "도구 중립 문구 결정"을 그대로 쓴다.

### Task D1: 실패하는 가드 테스트

**Files:** Create: `tests/unit/test_shipped_content_server_neutral.py`

- [ ] Step 1: 테스트 작성
  - `src/superclaude/` 아래 파일을 걷는다. `__pycache__`와 `.pyc`는 건너뛰고, UTF-8로 읽히지 않는 파일도 건너뛴다
  - 각 파일 내용을 casefold한 문자열에 `"serena"`가 없어야 한다. 실패 메시지는 파일 경로와 줄 번호를 모두 나열한다
  - 모듈 docstring: 이 이름은 01-discovery Q2~Q5 결정으로 배포 콘텐츠에서 빠졌다는 것과 `docs/features/serena-removal/` 링크
  - 허용 목록 없음 (index Deviations P8)
- [ ] Step 2: `uv run pytest tests/unit/test_shipped_content_server_neutral.py -v` → FAIL. 실패 목록이 아래 Task D2~D3의 파일과 정확히 같은지 대조한다. 다르면 목록에 없는 파일을 이 phase에 추가하고 deviation으로 적는다

### Task D2: R17과 에이전트 18개

**Files:** Modify
- `src/superclaude/core/rules/RULES_QUALITY.md:17`
- 아래 표의 에이전트 18개
- `.claude/rules/agent-authoring.md:40,157,223-233`

- [ ] Step 3: R17 본문을 Shared rules의 R17 문구로 바꾼다. 태그 `[R17 Symbolic-First] 🟡`는 그대로
- [ ] Step 4: 에이전트 `<tool_guidance>`의 `- Serena-First: ...` 줄을 다음 표대로 바꾼다. full/light 문구는 Shared rules 정의 그대로, "고유 문구"는 기존 줄에서 옮겨 온다

| 에이전트 (줄) | 형 | 고유 문구 (full 형의 가운데에 넣음) |
|---|---|---|
| backend-architect (:39) | full | targeted Grep for route shapes and anti-patterns |
| frontend-architect (:43) | full | targeted Grep on JSX or styling shapes |
| security-engineer (:43) | full | CWE-style Grep (e.g., `eval\(|exec\(|dangerouslySetInnerHTML`) for vuln or taint patterns |
| root-cause-analyst (:44) | full | targeted Grep on structural error patterns |
| refactoring-expert (:39) | full | targeted Grep for pattern queries |
| quality-engineer (:43), python-expert (:40), performance-engineer (:39), self-review (:42), system-architect (:40), repo-index (:36) | full | 없음 |
| devops-architect (:40), project-manager (:47), project-initializer (:59), requirements-analyst (:40) | light | 없음 |
| learning-guide (:39), socratic-mentor (:39) | light | 끝에 "with the learner". socratic-mentor는 `[R17 Symbolic-First]` 태그 유지 |
| technical-writer (:39) | light | 끝에 "when tracing code that docs reference" |

- [ ] Step 5: project-initializer `:36`의 MCP 추천 문장에서 "Serena for Python/backend; " 구절만 삭제 (나머지 추천 그대로)
- [ ] Step 6: `.claude/rules/agent-authoring.md`
  - `:40` 예시 `mcpServers: [serena]` → `mcpServers: [playwright]`
  - `:157` 템플릿 → `- Proceed: actions to do freely. Symbolic-First: prefer symbol-aware queries or targeted Grep for code exploration.`
  - `:223-233` 절 제목 "Code Exploration (Symbolic-First)". 표의 Full/Light 지시를 Shared rules의 full/light 문구로 바꾼다. Rationale 줄에 "subagents do not receive core rules, so the line ships in the agent body" 한 문장 추가

### Task D3: 나머지 콘텐츠

**Files:** Modify
- `src/superclaude/core/PRINCIPLES.md:19`, `src/superclaude/core/rules/RULES_DELEGATION.md:61`
- `src/superclaude/modes/MODE_Orchestration.md:17`
- `src/superclaude/commands/explain.md:52`, `select-tool.md:27-47`, `index-repo.md:2`
- `src/superclaude/agents/deep-researcher.md:3,24`, `simplicity-guide.md:54-55`
- `src/superclaude/scripts/file_size_guard.py:5`

- [ ] Step 7: 편집
  - PRINCIPLES `:19` Right-Altitude 행: Before `"ALWAYS use symbol tools for ALL code reads"` / After `"Use symbol tools when exploring unfamiliar code"`
  - RULES_DELEGATION `:61`: "try Grep and connected symbol-aware tools before delegating to deep-researcher"
  - MODE_Orchestration `:17` 예시: "symbol ops → symbol-aware MCP when connected"
  - explain `:52` gotcha: `- symbolic-first: prefer symbol-aware queries (when connected) or targeted Grep for code exploration, not full file read`
  - select-tool `<decision_matrix>`
    - Symbol ops: symbol-aware MCP when connected (LSP rename, references)
    - Pattern edits: Edit (native) after Grep or a reference query confirms targets
    - Memory ops: /sc:save, /sc:load (`.claude/memories/` + auto memory)
    - Threshold >0.6: symbol-aware MCP when connected (accuracy)
    - Fallback: no symbol-aware tool → Native tools (Grep/Glob/Edit)
  - select-tool 예시 표: rename 행 → "Symbol-aware MCP (LSP rename) when connected", save 행 → "/sc:save (memory folder)"
  - select-tool error-path Correct: "symbol-aware rename (LSP) when connected; otherwise Grep every occurrence and review each before Edit; reserve plain Grep+Edit for unambiguous text patterns."
  - index-repo `:2` description: "use Glob/Grep/Serena overview direct" → "use Glob/Grep direct"
  - deep-researcher `:3`: "Use when repo and Serena cannot answer the question." → "Use when the repo cannot answer the question." `:24`: "Grep the repo before external search."
  - simplicity-guide `:54`: "analyze deps (reference and overview queries when a symbol-aware tool is connected, else Grep)". `:55`: "pattern critique checks actual usage (reference query or Grep)"
  - file_size_guard `:5`: "model toward symbol-aware tools, Grep, or paginated Read instead."

### Task D4: 검증과 커밋

- [ ] Step 8: `uv run pytest tests/unit/test_shipped_content_server_neutral.py tests/unit/test_agent_structure.py tests/unit/test_command_structure.py -v` → PASS
- [ ] Step 9: `uv run pytest tests/unit/scripts -o addopts=` exit 0 (file_size_guard)
- [ ] Step 10: 에이전트 description 길이 확인: `test_agent_structure.py`가 상한을 검사한다. deep-researcher는 줄어들기만 한다
- [ ] Step 11: `uv run pytest` exit 0, `make lint` 통과
- [ ] Step 12: 커밋 `refactor(agents): make Symbolic-First tool-neutral; guard shipped content against server names`
