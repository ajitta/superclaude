# Command Authoring Rules

When creating or modifying command `.md` files in `src/superclaude/commands/`, follow these rules exactly.

## YAML Frontmatter

Commands use minimal frontmatter — only `description` is required.

```yaml
---
description: One-line purpose of this slash command  # required | shown in /menu
---
```

### Field Rules

**Required field**:
- `description` — shown in Claude Code's `/menu` listing. Must be >10 characters, specific, and action-oriented.

**Forbidden fields** — never include in command frontmatter:
- `name` — command name is derived from filename (e.g., `build.md` → `/sc:build`)
- `model`, `permissionMode`, `memory`, `color` — agent-only fields
- `autonomy` — not an official Claude Code field
- `context`, `agent`, `hooks` — skill-only fields

Commands inherit all tools and the parent model. Use skills (not commands) when you need tool restrictions, hooks, or subagent execution.

## XML Body Structure

Every command body follows this template:

```xml
<component name="command-name" type="command">

  <role>
    /sc:command-name
    <mission>Single sentence matching description</mission>
  </role>

  <syntax>/sc:command-name [args] [--flags]</syntax>

  <flow>
    1. Step: Description
    2. Step: Description
    3. Step: Description
  </flow>

  <outputs note="Per execution">
  | Artifact | Purpose |
  |----------|---------|
  | Type | What it produces |
  </outputs>

  <mcp servers="seq|c7|..."/>
  <personas p="arch|be|fe|..."/>

  <tools>
    - ToolName: purpose
  </tools>

  <gotchas note="Recommended — project-specific failure patterns">
  - pattern-name: Concrete failure + action instruction (2-5 items)
  </gotchas>

  <examples>
  | Input | Output |
  |-------|--------|
  | `/sc:command-name arg` | Expected result |
  </examples>

  <token_note>Consumption level — guidance for context management</token_note>

  <bounds will="core capabilities" wont="out-of-scope actions" fallback="Escalation path">
    Completion criteria and handoff behavior
  </bounds>

  <handoff next="/sc:next1 /sc:next2"/>
</component>
```

### XML Rules

- `<component>` — `name` must match filename stem, `type` must be `"command"`
- `<role>` — first line is `/sc:command-name` (the invocation), then `<mission>`
- `<mission>` — must share 30%+ significant words with frontmatter `description`
- `<syntax>` — show full invocation with args and flags
- `<flow>` — numbered execution steps (minimum 2)
- `<bounds>` — must include `will` and `wont` attributes
- `<handoff>` — list 2-3 natural next commands
- Optional sections: `<outputs>`, `<mcp>`, `<personas>`, `<tools>`, `<gotchas>`, `<examples>`, `<token_note>`

## Validation

After creating/modifying a command, run:
```bash
uv run pytest tests/unit/test_command_structure.py -v
```

This validates:
- Frontmatter has `description` field (>10 chars)
- No forbidden fields (agent/skill-only)
- XML component name matches filename
- component type is "command"
- `<role>` and `<mission>` exist
- mission ↔ description word overlap (≥30%)
- `<bounds>` exists
- `<handoff>` exists
- Minimum content length (>300 chars)

## Checklist for New Commands

1. Create `src/superclaude/commands/<name>.md` with frontmatter + XML body
2. Verify `<component name="...">` matches filename (without `.md`)
3. Write specific `description` for `/menu` display
4. Add `<gotchas>` section (recommended — project-specific failure patterns)
5. Run `uv run pytest tests/unit/test_command_structure.py -v`
6. Update `src/superclaude/commands/README.md` command table
7. Run `make deploy`

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|-------------|-----------|-----|
| Adding `name:` to frontmatter | Redundant — filename is command name | Remove field |
| Adding `model:` or `permissionMode:` | Agent-only fields, ignored by CC for commands | Remove field |
| Adding `hooks:` or `context:` | Skill-only fields — use skill if hooks needed | Migrate to skill |
| Vague description | Poor `/menu` display | Be specific: "Build X with Y" |
| Missing `<bounds>` | No scope/safety boundary | Add will/wont attributes |
| Mission doesn't match description | Confusing inconsistency | Align 30%+ word overlap |
