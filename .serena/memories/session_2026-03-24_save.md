# Session 2026-03-24: Serena-First Agent Exploration

## Commit
- `eb50d36` feat: add Serena-First directive to 18 agents for symbolic code exploration
- 22 files changed, +431 -14

## What Was Done
1. **Brainstorm**: Identified why agents use Read/Grep instead of Serena — ACCESS ≠ BEHAVIOR gap
2. **Research**: Confirmed via official docs that sub-agents inherit MCP tools by default; `mcpServers` (frontmatter) vs `<mcp servers>` (XML body, documentation-only) distinction
3. **Spec**: `docs/specs/2026-03-24-serena-first-agent-exploration-design-chosh1179.md`
4. **Review → Fix**: C1 deep-researcher dual classification, C2 simplicity-guide downgrade prevention
5. **Plan**: `docs/plans/2026-03-24-serena-first-agent-exploration-chosh1179.md` — 5 sprints, 11 tasks
6. **Implementation**: All 5 sprints complete, 626/626 tests pass
7. **Post-review**: PASS — spec 100% fidelity

## Key Changes
- HIGH tier (11 agents): full Serena-first directive in tool_guidance
- MEDIUM tier (7 agents): conditional Serena preference
- simplicity-guide: existing detailed Serena directive PRESERVED (not overwritten)
- LOW tier (3): no change (deep-researcher, business-panel-experts, git-workflow)
- 13 agents: serena added to mcp servers documentation tag
- RULES.md: [R17] Serena-First rule + 3 examples
- agent-authoring.md: mcpServers field docs + Code Exploration Pattern section

## Key Discoveries
- Sub-agents inherit ALL parent MCP tools by default (code.claude.com/docs/en/sub-agents)
- `mcpServers` (YAML frontmatter) = official CC field with runtime effect
- `<mcp servers="...">` (XML body) = SuperClaude documentation convention, no runtime effect
- .claude/rules/*.md sub-agent injection: uncertain (community reports conflict)
- RULES.md (@import chain) sub-agent injection: not guaranteed
