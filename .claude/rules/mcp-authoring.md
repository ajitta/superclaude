---
paths: ["src/superclaude/mcp/**", ".claude/rules/mcp-authoring.md"]
---

# MCP Authoring Rules

> **Decision gate:** Make `MCP_*.md` for **SuperClaude workflow guidance** layered on top of MCP server.
> - MCP doc = **WHEN/HOW to combine** with `/sc:*` commands + other servers (workflow patterns, decision tables)
> - NOT tool catalog — CC native MCP server description + `ToolSearch` already expose every tool, params, usage hint.
>
> If only content be "this server has tools X/Y/Z that do A/B/C", no make file. CC have it already.

| Component | Role |
|-----------|------|
| Agent     | WHO TO BE |
| Command   | WHAT TO DO |
| Skill     | WHICH CAPABILITY |
| Mode      | HOW TO THINK |
| MCP doc   | WHEN/HOW to use server in SC workflows |

## Filename and Location

- Path: `src/superclaude/mcp/MCP_<ServerName>.md` (PascalCase, hyphens ok: `MCP_Chrome-DevTools.md`).
- Filename stem after `MCP_` = **display name**; lowercase form what `context_loader.py` match against (`mcp/MCP_Serena.md` → `serena`).
- Register file in `scripts/context_loader.py` TRIGGER_MAP + INSTRUCTION_MAP (see Wiring below). Unregistered files dead — never load at runtime.

## No YAML Frontmatter

MCP docs pure content components. Not auto-discoverable like agents/skills — only enter context via loader trigger map. Frontmatter buy nothing + break `<component>` root-tag invariant of XML prose format.

## XML Template

> Conforms to `.claude/rules/xml-prose-format.md`: single root `<component name="..." type="mcp">`, `snake_case` section tags, short-line lists (**Numbered** `1.` for ordered procedures, or `-` prefix as **Plain**, **Labeled**, **Named** per item type), plural↔singular containers (`<examples><example>`) for multi-line items.

```xml
<component name="server-name" type="mcp">

  <role>
    <mission>One sentence — the SC workflow value of this server.</mission>
  </role>

  <choose>
    <use>trigger contexts where this server is the right tool — describe in prose with concrete cases.</use>
    <never>contexts where a native tool, another server, or no MCP at all is better — describe in prose.</never>
  </choose>

  <call_order>                                                <!-- optional, only when sequence is load-bearing -->
  1. `tool-a` — what it returns.
  2. `tool-b` — consumes step 1's output.
  </call_order>

  <integration_patterns>
  - Pattern-Name: server → next server / `/sc:command` (one-line chain).
  </integration_patterns>

  <examples>
  | Trigger | Action | Reason |
  |---|---|---|
  | short trigger | one-line action | one-line reason |
  </examples>

  <example>
  Free-form prose for a richer case (multi-step session, before/after, code-bearing illustration).
  </example>

  <bounds>
    <does>core scope in prose.</does>
    <never>out-of-scope use in prose.</never>
    <fallback>native tool / other server / WebSearch when out of scope.</fallback>
  </bounds>

  <handoff next="/sc:next1 /sc:next2"/>
</component>
```

### Body Rules

- `<component name="...">` match lowercase server identifier used in `context_loader.py` (e.g., `serena`, `context7`, `chrome-devtools`); `type="mcp"` required.
- All multi-word tag names use `snake_case`.
- Required tags: `<role>` (with `<mission>`), `<choose>`, `<bounds>`, `<handoff>`.
- Optional tags: `<call_order>` (only when call sequence matters — e.g., Context7 resolve→get pair), `<integration_patterns>` (cross-server / cross-command chains), `<examples>` (lookup table), `<example>` (rich illustration).
- `<choose>` — sub-tag form `<use>` / `<never>`, each body prose sentence. Mirror `<bounds>` slot-tag discipline; declarative voice, no hedging vocab (no `Avoid:` / `should:`). Sub-tag form keep `<choose>` structurally distinct from neighbor Labeled sections.
- `<bounds>` — sub-tag form `<does>` / `<never>` / `<fallback>`. `<fallback>` = native-tool or alternate-server escape hatch (load-bearing for MCP docs — readers need know what do when server wrong or unavailable).
- `<handoff next="...">` — 2-3 natural next `/sc:*` commands.
- Short enums: **Numbered** for ordered call sequences (`<call_order>`); **Named** (`- Identifier-Name:` per-item identifiers) for `<integration_patterns>`.

### Forbidden Body Content (the trim rule)

- **No `<tools>` inventory tables.** List every tool with params duplicate CC MCP server description + `ToolSearch` output, cost tokens, rot when server add/rename tools. Drop them.
- **No `<role>` body beyond `<mission>`.** Server own description ("what it does") belong to CC; SC doc add workflow value, not tool overview.
- **No version/install/setup blocks.** Install live in `cli/install_mcp.py`. Per-server setup hints belong in `mcp/README.md` if anywhere.
- **No "Token Management" / token-budget sections** unless budget server-specific + non-obvious (Context7 per-call token cap = only confirmed exception today).

If section read like "this is what server is" rather than "this is how I use server inside SC", cut it.

## Wiring (mandatory — without this the file is dead)

`scripts/context_loader.py` have three maps must update for any new file:

1. **Tool-name auto-load**: when CC fire `mcp__<server>__*` tool, loader inject matching doc. Add file to tool-name section (currently lines 96-101 / 129-139 of `context_loader.py`, behind `_BEHAVIORAL_MCPS`).
2. **Flag-trigger TRIGGER_MAP**: map user flags (`--c7`, `--seq`, …) to file. Pick stable flag + add regex row.
3. **INSTRUCTION_MAP**: one-line summary string (≤120 chars) shown when loader inject this doc — Claude read before body land.

Add `MCP_<X>.md` with no entries in these maps + it sit on disk forever, unloaded.

## Inherited from xml-prose-format.md

Following rules apply to all components + not restated above. See `.claude/rules/xml-prose-format.md` for full text.

- **Single root XML wrapper** — exactly one root tag per component body; sibling sections only at root level.
- **Long-form embedded enumerations** — lists embedded in running prose use natural-language enumeration ("things include x, y, z"), not bullets.
- **Quoting conventions** — URLs + model identifier strings in single quotes (`'https://…'`, `'claude-opus-4-7'`); UI / product / feature names in double quotes (`"settings"`); runtime variables in double curly braces (`{{currentDateTime}}`).
- **Cross-references** — point to other sections by plain English topic, not by tag path.
- **Markdown headers inside `<example>`** — permitted when illustration mirror real markdown artifact (report template, commit message, user document); body-prose "no markdown headers" rule no extend into `<example>` bodies.

## Checklist

1. Make `src/superclaude/mcp/MCP_<Server>.md` — no frontmatter, single `<component name="..." type="mcp">` root.
2. Drop tool inventories, role descriptions, version/install blocks. Keep `<choose>` / integration / `<bounds>` / `<handoff>`.
3. Wire all three maps in `scripts/context_loader.py` (tool-name, TRIGGER_MAP, INSTRUCTION_MAP).
4. Add row to `mcp/README.md` (Core or Plugin table) with flag + one-line mission.
5. If server core (auto-installed), register in `cli/install_mcp.py::MCP_SERVERS`.
6. Run `make sync-user` (or scope-equivalent) + exercise trigger — confirm doc land in context.

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|-------------|-----------|-----|
| `<tools>` table listing every tool | Duplicates CC's MCP description / ToolSearch | Remove; keep only `<call_order>` if sequence is load-bearing |
| `<role>` paragraph describing the server | CC's MCP server description already does this | Trim `<role>` to a single `<mission>` line |
| Adding YAML frontmatter | Breaks single-root XML invariant; loader ignores it | Remove frontmatter |
| File present, no `context_loader.py` entry | File never loads | Wire all three maps (tool-name, TRIGGER_MAP, INSTRUCTION_MAP) |
| Install/setup instructions in body | Wrong layer; rots fast | Move to `cli/install_mcp.py` or `mcp/README.md` |
| Decorative `note=` XML attributes | Token waste | See xml-prose-format.md "Attributes vs. Body" — `note=` only for scope/safety/version/reference/quantified constraint |
| Generic "use Sequential for hard problems" | Vague trigger; no value over CC native | Replace with concrete trigger contexts in `<choose>` and chained `/sc:*` patterns in `<integration_patterns>` |