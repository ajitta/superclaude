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

> Conforms to `.claude/rules/xml-prose-format.md`: single root, `snake_case` section tags, short-line lists (**Numbered** `1.` for ordered procedures, or `-` prefix as **Plain**, **Labeled**, **Named** per item type), plural↔singular containers (`<examples><example>`) for multi-line items.

```xml
<component name="command-name" type="command">

  <role>
    /sc:command-name
    <mission>Single sentence matching description.</mission>
  </role>

  <syntax>/sc:command-name [args] [--flags]</syntax>

  <flow>
  1. Verb-leading description of the step (≥2 steps; sequence is load-bearing).
  </flow>

  <outputs>
  - Artifact: purpose
  </outputs>

  <mcp servers="seq|c7|..."/>

  <tools>
  - ToolName: purpose
  </tools>

  <gotchas>
  - pattern-name: concrete failure + action instruction (2-5 items)
  </gotchas>

  <examples>
  | Trigger | Expected behavior |
  |---|---|
  | `/sc:command-name arg` | one-line response shape |
  | `/sc:command-name arg2` | another one-line shape |
  </examples>

  <bounds>
    <should>core capabilities described in prose (in-scope).</should>
    <avoid>out-of-scope actions described in prose.</avoid>
    <fallback>escalation path; optional for commands — use when out-of-scope handling is non-obvious.</fallback>
  </bounds>

  <handoff next="/sc:next1 /sc:next2"/>
</component>
```

### XML Rules

- `<component name="...">` matches filename stem, `type="command"`
- All multi-word tag names use `snake_case`
- Short enums: **Numbered** (`1.` for ordered procedures: `<flow>`), **Labeled** (`- Label:` fixed-set labels: `<tool_guidance>` Proceed/Ask First/Never), **Named** (`- identifier-name:` per-item identifiers: `<outputs>`, `<tools>`, `<gotchas>`)
- `<examples>` — compact markdown table with minimal separators `|---|---|` for short uniform rows. For richer illustrations (code blocks, narrative, multi-turn prose), use a standalone `<example>` tag — its body is free-form prose, not locked to a `user:` / `assistant:` shape. `<examples>` and `<example>` are two distinct constructs (see xml-prose-format.md)
- `<role>` — first line is `/sc:command-name`, then `<mission>`
- `<mission>` — shares ≥30% significant words with frontmatter `description`
- `<flow>` — at least two numbered steps in execution order
- `<bounds>` — sub-tag form: `<should>` / `<avoid>` / `<fallback>` (each tag's body is a prose sentence). `<should>` + `<avoid>` required; `<fallback>` optional (use when out-of-scope handling is non-obvious). Sub-tag form keeps `<bounds>` structurally distinct from `<tool_guidance>` (commit `S390` measured Claude conflating the two when both used `- Label:` lines)
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
| Decorative `note=` XML attrs | Unparsed boilerplate, token waste | See xml-prose-format.md "Attributes vs. Body" — `note=` only for scope/safety/version/reference/quantified constraint |
