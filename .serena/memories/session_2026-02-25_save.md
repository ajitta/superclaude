# Session 2026-02-25 — Context Loader v3.1 Refactor

## Work Done
1. **permissionMode enforcement**: Added `permissionMode` frontmatter to all 20 agent .md files (autonomy→permissionMode mapping: high→acceptEdits, medium→default, low→plan)
2. **Command-agent linkage**: Wired 6 orphaned agents into commands via personas fields (7 command files updated)
3. **Triggers cleanup**: Removed redundant `<triggers>` XML from entire project (69 files: 20 agents, 28 commands, 4 core, 9 modes, 8 MCP)
4. **context_loader.py v3.1 refactor**:
   - Fixed false positives: removed generic words (edit, test, search, task, docs, debug, ui, etc.) from TRIGGER_MAP regex
   - Added COMPOSITE_FLAGS: --frontend-verify (Playwright+DevTools+Serena), --all-mcp (all 8 MCP)
   - Implemented --no-mcp: suppresses mcp/ context loading, modes still load
   - Hybrid INSTRUCTION_MAP: MCP files use short instructions, Mode files use full .md injection
   - Serena + Tavily excluded from INSTRUCTION_MAP → full .md injection (behavioral patterns)
5. **Tests**: 734 passing, 3 new tests added (permissionMode), 3 removed (triggers)

## Commits (5, unpushed)
- 66062c7: permissionMode + command-agent linkage + agent trigger removal
- e36c4c9: command triggers removal (28 files)
- 7fc7cc0: core/modes/mcp triggers removal (20 files)
- 57fb5c7: context_loader v3.1 hybrid injection
- d9f21df: Tavily → full .md injection

## Key Decisions
- `<triggers>` XML was dead code — never read by any Python code or runtime
- Claude Code reads ONLY YAML frontmatter `description` field for agent routing
- context_loader.py TRIGGER_MAP is the actual runtime trigger mechanism (hardcoded regex)
- Hybrid injection: MCP servers provide tool descriptions via protocol; modes define behavioral rules
- Serena + Tavily get full .md: integration flows, initialization sequences, multi-hop strategies

## Architecture: context_loader.py v3.1
```
User prompt → stdin → context_loader.py
  → COMPOSITE_FLAGS (--frontend-verify, --all-mcp)
  → --no-mcp filter (suppress mcp/)
  → TRIGGER_MAP regex (tightened, no generic words)
  → INSTRUCTION_MAP:
    - In map (6 MCP + 1 core) → short instruction (~40t)
    - Not in map (8 modes + Serena + Tavily) → full .md
```

## Repository State
- Branch: master (5 commits ahead of origin, unpushed)
- 734 tests passing, version 4.2.1+ajitta
