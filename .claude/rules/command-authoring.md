---
paths: ["src/superclaude/commands/**", ".claude/rules/command-authoring.md"]
---

# Command Authoring Rules

> **Decision gate:** Make command for **user-facing workflow entry** (`/sc:*` slash commands).
> - Command = **WHAT TO DO** (ordered workflow)
> - Agent = **WHO TO BE** (domain expertise, auto-delegated)
> - Skill = **WHICH CAPABILITY** (CC-native tool/hook)
> - Mode = **HOW TO THINK** (cognitive overlay)
>
> Need tool restrictions, hooks, or subagent execution? → use skill, not command.

## YAML Frontmatter

Minimal — only `description` required. Commands inherit all tools + parent model.

```yaml
---
description: One-line purpose of this slash command  # required, >10 chars, action-oriented
---
```

### Forbidden fields

Never add — SSOT: `.claude/rules/schemas.yaml` (`forbidden_command_fields`):

- `name` — derived from filename (e.g., `build.md` → `/sc:build`)
- `model`, `permissionMode`, `memory`, `color` — agent-only
- `autonomy` — not official CC field
- `context`, `agent`, `hooks` — skill-only (migrate to skill if needed)

## XML Template

> Conforms to `.claude/rules/xml-prose-format.md`: single root, `snake_case` section tags, short-line lists (**Numbered** `1.` for ordered procedures, or `-` prefix as **Plain**, **Labeled**, **Named** per item type), plural↔singular containers (`<examples><example>`) for multi-line items.

```xml
<component name="command-name" type="command">

  <role command="/sc:command-name">
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

  <examples>
  | Trigger | Expected behavior |
  |---|---|
  | `/sc:command-name arg` | one-line response shape |
  | `/sc:command-name arg2` | another one-line shape |
  </examples>

  <gotchas>
  - pattern-name: concrete failure + action instruction (2-5 items)
  </gotchas>

  <bounds>
    <does>core capabilities described in prose (in-scope).</does>
    <never>out-of-scope actions described in prose.</never>
    <fallback>escalation path; optional for commands — use when out-of-scope handling is non-obvious.</fallback>
  </bounds>

  <handoff next="/sc:next1 /sc:next2"/>
</component>
```

### XML Rules

- `<component name="...">` matches filename stem, `type="command"`
- All multi-word tag names use `snake_case`
- Short enums: **Numbered** (`1.` for ordered procedures: `<flow>`), **Labeled** (`- Label:` fixed-set labels: `<tool_guidance>` Proceed/Ask First/Never), **Named** (`- identifier-name:` per-item identifiers: `<outputs>`, `<tools>`, `<gotchas>`)
- `<examples>` — compact markdown table, minimal separators `|---|---|` for short uniform rows. For richer illustrations (code blocks, narrative, multi-turn prose), use standalone `<example>` tag — body free-form prose, not locked to `user:` / `assistant:` shape. `<examples>` and `<example>` are two distinct constructs (see xml-prose-format.md)
- `<role command="/sc:command-name">` — `command` attribute carries slash identifier (matches filename stem); body contains `<mission>` only. Per xml-prose-format "Attributes vs. Body", short identifiers belong as attributes.
- `<mission>` — shares ≥30% significant words with frontmatter `description`
- `<flow>` — ≥2 numbered steps in execution order
- `<bounds>` — sub-tag form: `<does>` / `<never>` / `<fallback>` (each body prose sentence). `<does>` + `<never>` required; `<fallback>` optional (use when out-of-scope handling non-obvious). Sub-tag form keeps `<bounds>` structurally distinct from `<tool_guidance>` (commit `S390` measured Claude conflating two when both used `- Label:` lines)
- `<handoff next="...">` — 2-3 natural next commands
- Optional: `<outputs>`, `<mcp>`, `<tools>`, `<gotchas>`, `<examples>`

## Inherited from xml-prose-format.md

Rules below apply to all components, not restated above. See `.claude/rules/xml-prose-format.md` for full text.

- **Single root XML wrapper** — exactly one root tag per component body; sibling sections only at root level.
- **Long-form embedded enumerations** — lists embedded in running prose use natural-language enumeration ("things include x, y, z"), not bullets.
- **Quoting conventions** — URLs + model identifier strings in single quotes (`'https://…'`, `'claude-opus-4-7'`); UI / product / feature names in double quotes (`"settings"`); runtime variables in double curly braces (`{{currentDateTime}}`).
- **Cross-references** — point to other sections by plain English topic, not by tag path.
- **Markdown headers inside `<example>`** — permitted when illustration mirrors real markdown artifact (report template, commit message, user document); body-prose "no markdown headers" rule does not extend into `<example>` bodies.
- **Size target** — command body ≤200 lines (hard ceiling 300); extract overflow into referenced sibling file, not inline-bloat body.

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
| Missing `<bounds>` | No scope/safety boundary | Add `<does>`/`<never>` |
| Mission doesn't match description | Confusing inconsistency | Align ≥30% word overlap |
| Decorative `note=` XML attrs | Unparsed boilerplate, token waste | See xml-prose-format.md "Attributes vs. Body" — `note=` only for scope/safety/version/reference/quantified constraint |