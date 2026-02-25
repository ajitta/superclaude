# Wave 6-7 Opus 4.6 Alignment - Codebase Exploration Findings

## STATUS UPDATE (Feb 2026)
Several items from this exploration have been resolved in subsequent sessions:
- **A6 (autonomy field)**: Resolved as `permissionMode` frontmatter (Feb 25 session) — high→acceptEdits, medium→default, low→plan
- **A4 (color field)**: Not implemented — agent differentiation via role/mission/mindset instead (deliberate decision)
- **Triggers cleanup**: All `<triggers>` XML removed from 69 files (Feb 25 session) — was dead code
- **Test count**: Grew from ~225 to 734

## WAVE 6 TARGETS

### 1. Skills: confidence-check/SKILL.md (SK1, SK2)
- **SK1**: ✅ No @deprecated annotation (clean)
- **SK2**: ⚠️ No "disable-model-invocation" field (needs clarification on need)

### 2. Hooks: hooks.json (H1, H3)
- **H1**: ✅ TeammateIdle/TaskCompleted already present with [experimental] markers
- **H3**: ❌ No async hook support documentation (hooks are command-based)

## WAVE 7 TARGETS

### 3. Agent Files (A4-A7)
- **A4 (color)**: ❌ Not implemented (deliberate — not needed)
- **A5 (negative examples)**: ✅ All agents have bounds/tool_guidance with "Never" sections
- **A6 (autonomy)**: ✅ RESOLVED → `permissionMode` field added to all 20 agents
- **A7 (cross-refs)**: ⚠️ Minimal command cross-refs (MCP refs only)

### 4. Commands: index-repo.md vs index.md (CMD5)
- ✅ Clear separation: index = comprehensive docs, index-repo = token-efficient structure

### 5. Command section ordering (CMD6)
- ✅ Consistent XML ordering across all commands

### 6. MODE_Token_Efficiency.md (M2)
- ✅ Deprecated symbols documented, current symbols defined

### 7. Modes directory (M4)
- ❌ No README.md in modes/ (low priority)

### 8. MCP directory (MCP1, MCP5-7)
- **MCP1**: ✅ Deprecated files (Mindbase, Airis-Agent) properly marked
- **MCP5**: ❌ No version tags in MCP files
- **MCP6**: ✅ Consistent XML structure
- **MCP7**: ❌ No README.md in mcp/

### 9. Scripts (S2)
- ✅ All scripts present, context_reset.py verified

### 10. RESEARCH_CONFIG.md (C13)
- ⚠️ Some aspirational/undefined config keys

## SUMMARY TABLE

| Target | Finding | Status |
|--------|---------|--------|
| SK1 | @deprecated in SKILL.md | ✅ Clean |
| SK2 | disable-model-invocation | ⚠️ Not found |
| H1 | TeammateIdle/TaskCompleted | ✅ Present |
| H3 | Async hook docs | ❌ None |
| A4 | color field | ❌ Not needed |
| A5 | negative examples | ✅ All present |
| A6 | autonomy/permissionMode | ✅ RESOLVED |
| A7 | cross-refs to commands | ⚠️ Minimal |
| CMD5 | index vs index-repo | ✅ Clear |
| CMD6 | section ordering | ✅ Consistent |
| M2 | deprecated symbols | ✅ Documented |
| M4 | modes/ README | ❌ Missing |
| MCP1 | deprecated MCPs | ✅ Marked |
| MCP5 | version accuracy | ❌ No versions |
| MCP6 | standardization | ✅ Consistent |
| MCP7 | mcp/ README | ❌ Missing |
| S2 | context_reset.py | ✅ Verified |
| C13 | undefined config keys | ⚠️ Some aspirational |

## KEY INSIGHTS
1. Agent structure stable: all 20 agents use consistent YAML frontmatter with `memory: user` + `permissionMode`
2. Negative examples universal: all agents have bounds with "Never" sections
3. Command ordering consistent across all files
4. Documentation gaps: no README in modes/ or mcp/ (low priority)
5. Context reset: solid hash-based cache management with TTL
