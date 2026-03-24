# Serena-First Agent Exploration — Implementation Plan

**Goal:** 18개 에이전트의 `<tool_guidance>`에 Serena-First 디렉티브를 추가하고, RULES.md와 agent-authoring.md를 업데이트하여 코드 탐색 시 Serena 심볼릭 도구 우선 사용을 표준화한다.
**Architecture:** Agent .md body 수정 (tool_guidance 1줄 + mcp tag) + core RULES.md 규칙 추가 + authoring 가이드 업데이트
**Spec:** `docs/specs/2026-03-24-serena-first-agent-exploration-design-chosh1179.md`

---

## Sprint 1: HIGH Tier Agents (11 files)

각 에이전트에 2가지 변경: `<tool_guidance>` Proceed에 Serena-First 줄 추가 + `<mcp servers="...">` 태그에 `serena` 추가 (이미 있으면 skip).

**디렉티브 (동일 문구):**
```
- Serena-First: For code exploration, use get_symbols_overview → find_symbol(include_body=True) before Read. Reserve Read for non-code files (config, docs, data). Use find_referencing_symbols for impact analysis.
```

### Task 1: backend-architect, frontend-architect, python-expert
**Files:** Modify: `src/superclaude/agents/backend-architect.md`, `frontend-architect.md`, `python-expert.md`
- [ ] backend-architect: tool_guidance Proceed에 Serena-First 줄 추가, mcp `seq|c7` → `seq|c7|serena`
- [ ] frontend-architect: tool_guidance Proceed에 Serena-First 줄 추가, mcp `magic|play|perf` → `magic|play|perf|serena`
- [ ] python-expert: tool_guidance Proceed에 Serena-First 줄 추가, mcp `c7|seq` → `c7|seq|serena`

### Task 2: performance-engineer, quality-engineer, security-engineer
**Files:** Modify: `src/superclaude/agents/performance-engineer.md`, `quality-engineer.md`, `security-engineer.md`
- [ ] performance-engineer: tool_guidance Proceed에 Serena-First 줄 추가, mcp `perf|seq|play` → `perf|seq|play|serena`
- [ ] quality-engineer: tool_guidance Proceed에 Serena-First 줄 추가, mcp `play|seq` → `play|seq|serena`
- [ ] security-engineer: tool_guidance Proceed에 Serena-First 줄 추가, mcp `seq|c7` → `seq|c7|serena`

### Task 3: root-cause-analyst, system-architect, refactoring-expert
**Files:** Modify: `src/superclaude/agents/root-cause-analyst.md`, `system-architect.md`, `refactoring-expert.md`
- [ ] root-cause-analyst: tool_guidance Proceed에 Serena-First 줄 추가 (mcp 이미 `seq|serena` — skip)
- [ ] system-architect: tool_guidance Proceed에 Serena-First 줄 추가, mcp `seq|c7` → `seq|c7|serena`
- [ ] refactoring-expert: tool_guidance Proceed에 Serena-First 줄 추가 (mcp 이미 `seq|serena|morph` — skip)

### Task 4: repo-index, self-review
**Files:** Modify: `src/superclaude/agents/repo-index.md`, `self-review.md`
- [ ] repo-index: tool_guidance Proceed에 Serena-First 줄 추가 (mcp 이미 `serena` — skip)
- [ ] self-review: tool_guidance Proceed에 Serena-First 줄 추가 (mcp 이미 `seq|serena` — skip)

### Task 5: Sprint 1 검증
- [ ] `grep -c "Serena-First" src/superclaude/agents/{backend-architect,frontend-architect,python-expert,performance-engineer,quality-engineer,security-engineer,root-cause-analyst,system-architect,refactoring-expert,repo-index,self-review}.md` — 11개 모두 1
- [ ] `uv run pytest tests/unit/test_agent_structure.py -v` — 전체 통과

---

## Sprint 2: MEDIUM Tier Agents (7 files, simplicity-guide 제외)

**디렉티브 (동일 문구):**
```
- Serena-First: When exploring code, prefer Serena symbolic tools (get_symbols_overview, find_symbol) over Read for token efficiency.
```

### Task 6: project-manager, project-initializer, devops-architect
**Files:** Modify: `src/superclaude/agents/project-manager.md`, `project-initializer.md`, `devops-architect.md`
- [ ] project-manager: tool_guidance Proceed에 Serena-First 줄 추가 (mcp 이미 `serena|seq` — skip)
- [ ] project-initializer: tool_guidance Proceed에 Serena-First 줄 추가, mcp `seq` → `seq|serena`
- [ ] devops-architect: tool_guidance Proceed에 Serena-First 줄 추가, mcp `seq|c7` → `seq|c7|serena`

### Task 7: technical-writer, learning-guide, socratic-mentor, requirements-analyst
**Files:** Modify: `src/superclaude/agents/technical-writer.md`, `learning-guide.md`, `socratic-mentor.md`, `requirements-analyst.md`
- [ ] technical-writer: tool_guidance Proceed에 Serena-First 줄 추가, mcp `c7|seq` → `c7|seq|serena`
- [ ] learning-guide: tool_guidance Proceed에 Serena-First 줄 추가, mcp `c7|seq` → `c7|seq|serena`
- [ ] socratic-mentor: tool_guidance Proceed에 Serena-First 줄 추가, mcp `seq|c7` → `seq|c7|serena`
- [ ] requirements-analyst: tool_guidance Proceed에 Serena-First 줄 추가, mcp `seq` → `seq|serena`

### Task 8: Sprint 2 검증
- [ ] `grep -c "Serena-First" src/superclaude/agents/{project-manager,project-initializer,devops-architect,technical-writer,learning-guide,socratic-mentor,requirements-analyst}.md` — 7개 모두 1
- [ ] `grep "find_referencing_symbols" src/superclaude/agents/simplicity-guide.md` — 기존 Serena 지시 보존 확인
- [ ] `uv run pytest tests/unit/test_agent_structure.py -v` — 전체 통과

---

## Sprint 3: RULES.md (1 file)

### Task 9: [R17] 규칙 + examples 추가
**Files:** Modify: `src/superclaude/core/RULES.md`
- [ ] `[R16] Safe Read` 뒤에 `[R17] Serena-First 🟢` 규칙 추가
- [ ] `<examples>` 테이블에 Serena-First 3줄 추가 (기존 패턴: `| Scenario | Wrong | Right | Rule |`)
- [ ] `grep "R17" src/superclaude/core/RULES.md` — 규칙 존재 확인

---

## Sprint 4: agent-authoring.md (1 file)

### Task 10: 템플릿 + mcpServers 문서화 + Code Exploration Pattern
**Files:** Modify: `.claude/rules/agent-authoring.md`
- [ ] `<tool_guidance>` 템플릿 예시에 `| Serena-First: prefer symbolic tools for code exploration` 추가
- [ ] Frontmatter 필드 레퍼런스에 `mcpServers` 필드 문서화 (optional, 스코핑 용도 설명 포함)
- [ ] `## Validation` 앞에 `## Code Exploration Pattern` 섹션 추가 (3-tier 테이블 + Rationale + Note)
- [ ] `grep "Code Exploration Pattern" .claude/rules/agent-authoring.md` — 섹션 존재 확인

---

## Sprint 5: Final Verification

### Task 11: 전체 검증
- [ ] `uv run pytest tests/unit/test_agent_structure.py -v` — 에이전트 구조 전체 통과
- [ ] `uv run pytest` — 전체 테스트 스위트 회귀 (baseline: 1,694 tests)
- [ ] `grep -rc "Serena-First" src/superclaude/agents/ | grep -v ":0" | wc -l` — 18개 확인
- [ ] `grep -c "Serena-First" src/superclaude/agents/simplicity-guide.md` — 0 (기존 문구 유지)
- [ ] `grep "serena" src/superclaude/agents/*.md | grep "mcp servers" | wc -l` — 20개 (기존 7 + 신규 13)
- [ ] `make deploy` — 글로벌 도구 배포
