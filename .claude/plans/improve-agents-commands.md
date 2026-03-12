# Improvement Plan: agents/ and commands/

## Summary

Analysis of 31 commands and 21 agents reveals high consistency in agents (~95%) but several gaps in commands (~75% adherence to patterns).

## Safe Improvements (No Breaking Changes)

### Commands - Priority Fixes

| File | Issue | Fix |
|------|-------|-----|
| `agent.md` | `name="sc:agent"` inconsistent | Change to `name="agent"` |
| `troubleshoot.md` | Missing `<mcp>`, `<personas>`, `<checklist>` | Add sections |
| `explain.md` | Missing `<checklist>` | Add 4-item checklist |
| `brainstorm.md` | Missing `<checklist>` | Add 4-item checklist |
| `select-tool.md` | Missing `<checklist>`, `<personas>` | Add sections |

### Commands - Pattern Alignment (5 files)

Add `<checklist note="SHOULD complete all">` with 4 items to:
- `explain.md` - explanation quality checks
- `brainstorm.md` - requirements discovery checks
- `troubleshoot.md` - diagnostic quality checks
- `select-tool.md` - tool selection accuracy checks

Add `<mcp>` and `<personas>` where missing:
- `troubleshoot.md` - add `<mcp servers="seq"/>` and `<personas p="root|devops"/>`
- `select-tool.md` - add `<personas p="arch"/>`

### Agents - No Changes Needed

All 21 agents are well-structured with:
- Consistent frontmatter (100%)
- Standard sections present (95%)
- Intentional variations for specialized agents

## Execution Plan

1. Fix `agent.md` naming (1 edit)
2. Add missing sections to 4 commands (4 files, ~16 edits)
3. Validate no breaking changes

## Files Modified

```
src/superclaude/commands/agent.md        # name fix
src/superclaude/commands/explain.md      # +checklist
src/superclaude/commands/brainstorm.md   # +checklist
src/superclaude/commands/troubleshoot.md # +mcp, +personas, +checklist
src/superclaude/commands/select-tool.md  # +personas, +checklist
```

## Not Changing

- Agents directory (already consistent)
- Command lists in sc.md/help.md/README.md (intentional reference duplication)
- File sizes (variation is acceptable)
