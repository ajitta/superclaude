---
paths: ["src/superclaude/commands/**", ".claude/rules/command-authoring.md"]
---

# Command Authoring Rules

> **Decision gate:** Create a command for **user-facing workflow entry** (`/sc:*` slash commands).
> - Command = **WHAT TO DO** (ordered workflow)
> - Agent = **WHO TO BE** (domain expertise, auto-delegated)
> - Skill = **WHICH CAPABILITY** (CC-native tool/hook)
> - Mode = **HOW TO THINK** (cognitive overlay)
>
> Need tool restrictions, hooks, or subagent execution? → use a skill, not a command.

## YAML Frontmatter

Minimal — only `description` is required. Commands inherit all tools and the parent model.

```yaml
---
description: One-line purpose of this slash command  # required, >10 chars, action-oriented
---
```

### Forbidden fields

Never add these — SSOT: `.claude/rules/schemas.yaml` (`forbidden_command_fields`):

- `name` — derived from filename (e.g., `build.md` → `/sc:build`)
- `model`, `permissionMode`, `memory`, `color` — agent-only
- `autonomy` — not an official CC field
- `context`, `agent`, `hooks` — skill-only (migrate to skill if needed)

## XML Template

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
  </flow>

  <outputs note="Per execution">
  | Artifact | Purpose |
  |----------|---------|
  | Type | What it produces |
  </outputs>

  <mcp servers="seq|c7|..."/>
  <tools>- ToolName: purpose</tools>

  <gotchas>
  - pattern-name: Concrete failure + action instruction (2-5 items)
  </gotchas>

  <examples>
  | Input | Output |
  |-------|--------|
  | `/sc:command-name arg` | Expected result |
  </examples>

  <bounds should="core capabilities" avoid="out-of-scope actions" fallback="Escalation path">
    Completion criteria and handoff behavior
  </bounds>

  <handoff next="/sc:next1 /sc:next2"/>
</component>
```

### XML Rules

- `<component name="...">` matches filename stem, `type="command"`
- `<role>` — first line is `/sc:command-name`, then `<mission>`
- `<mission>` — shares ≥30% significant words with frontmatter `description`
- `<flow>` — numbered execution steps (≥2)
- `<bounds>` — `should` + `avoid` attributes required
- `<handoff next="...">` — 2-3 natural next commands
- Optional: `<outputs>`, `<mcp>`, `<tools>`, `<gotchas>`, `<examples>`

## Checklist

1. Create `src/superclaude/commands/<name>.md` with frontmatter + XML
2. Verify `<component name="...">` matches filename
3. Write specific `description` (shown in `/menu`)
4. Add `<gotchas>` for project-specific failure patterns
5. Run `uv run pytest tests/unit/test_command_structure.py -v`
6. Update `src/superclaude/commands/README.md` table
7. Run `make deploy`

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|-------------|-----------|-----|
| `name:` in frontmatter | Filename is the command name | Remove |
| `model:` or `permissionMode:` | Agent-only, ignored for commands | Remove |
| `hooks:` or `context:` | Skill-only — migrate to skill if needed | Remove or migrate |
| Vague description | Poor `/menu` display | Be specific: "Build X with Y" |
| Missing `<bounds>` | No scope/safety boundary | Add `should`/`avoid` |
| Mission doesn't match description | Confusing inconsistency | Align ≥30% word overlap |
| Decorative `note=` XML attrs | Unparsed boilerplate, token waste | `note=` only for scope/safety/version/reference/quantified constraint |
