---
paths: ["src/superclaude/mcp/**", ".claude/rules/mcp-authoring.md"]
---

# MCP Authoring Rules

> **Decision gate:** Create an `MCP_*.md` for **SuperClaude workflow guidance** layered on top of an MCP server.
> - MCP doc = **WHEN/HOW to combine** with `/sc:*` commands and other servers (workflow patterns, decision tables)
> - NOT a tool catalog — CC's native MCP server description and `ToolSearch` already expose every tool, its parameters, and a usage hint.
>
> If the only content you want to write is "this server has tools X/Y/Z that do A/B/C", do not create the file. CC already has it.

| Component | Role |
|-----------|------|
| Agent     | WHO TO BE |
| Command   | WHAT TO DO |
| Skill     | WHICH CAPABILITY |
| Mode      | HOW TO THINK |
| MCP doc   | WHEN/HOW to use a server in SC workflows |

## Filename and Location

- Path: `src/superclaude/mcp/MCP_<ServerName>.md` (PascalCase, hyphens allowed: `MCP_Chrome-DevTools.md`).
- Filename stem after `MCP_` is the **display name**; the lowercase form is what `context_loader.py` matches against (`mcp/MCP_Serena.md` → `serena`).
- Register the file in `scripts/context_loader.py` TRIGGER_MAP and INSTRUCTION_MAP (see Wiring below). Unregistered files are dead — never loaded at runtime.

## No YAML Frontmatter

MCP docs are pure content components. They are not auto-discoverable like agents/skills — they only enter context via the loader's trigger map. Adding frontmatter buys nothing and breaks the `<component>` root-tag invariant of the XML prose format.

## XML Template

> Conforms to `.claude/rules/xml-prose-format.md`: single root `<component name="..." type="mcp">`, `snake_case` section tags, short-line lists (**Numbered** `1.` for ordered procedures, or `-` prefix as **Plain**, **Labeled**, **Named** per item type), plural↔singular containers (`<examples><example>`) for multi-line items.

```xml
<component name="server-name" type="mcp">

  <role>
    <mission>One sentence — the SC workflow value of this server.</mission>
  </role>

  <choose>
  Use:
  - Trigger context where this server is the right tool.
  - Another trigger context.

  Avoid:
  - Context where a native tool or another server is better.
  - Another out-of-scope context.
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

- `<component name="...">` matches the lowercase server identifier used in `context_loader.py` (e.g., `serena`, `context7`, `chrome-devtools`); `type="mcp"` required.
- All multi-word tag names use `snake_case`.
- Required tags: `<role>` (with `<mission>`), `<choose>`, `<bounds>`, `<handoff>`.
- Optional tags: `<call_order>` (only when call sequence matters — e.g., Context7's resolve→get pair), `<integration_patterns>` (cross-server / cross-command chains), `<examples>` (lookup table), `<example>` (rich illustration).
- `<bounds>` — sub-tag form `<does>` / `<never>` / `<fallback>`. `<fallback>` is the native-tool or alternate-server escape hatch (load-bearing for MCP docs — readers need to know what to do when the server is wrong or unavailable).
- `<handoff next="...">` — 2-3 natural next `/sc:*` commands.
- Short enums: **Numbered** for ordered call sequences (`<call_order>`); **Named** (`- Identifier-Name:` per-item identifiers) for `<integration_patterns>`.

### Forbidden Body Content (the trim rule)

- **No `<tools>` inventory tables.** Listing every tool with parameters duplicates CC's MCP server description and `ToolSearch` output, costs tokens, and rots when the server adds/renames tools. Drop them.
- **No `<role>` body beyond `<mission>`.** The server's own description ("what it does") belongs to CC; the SC doc adds workflow value, not tool overview.
- **No version/install/setup blocks.** Install lives in `cli/install_mcp.py`. Per-server setup hints belong in `mcp/README.md` if anywhere.
- **No "Token Management" / token-budget sections** unless the budget is server-specific and non-obvious (Context7's per-call token cap is the only confirmed exception today).

If a section reads like "this is what the server is" rather than "this is how I use the server inside SC", cut it.

## Wiring (mandatory — without this the file is dead)

`scripts/context_loader.py` has three maps you must update for any new file:

1. **Tool-name auto-load**: when CC fires a `mcp__<server>__*` tool, the loader injects the matching doc. Add the file to the tool-name section (currently lines 96-101 / 129-139 of `context_loader.py`, behind `_BEHAVIORAL_MCPS`).
2. **Flag-trigger TRIGGER_MAP**: maps user flags (`--c7`, `--seq`, …) to the file. Pick a stable flag and add a regex row.
3. **INSTRUCTION_MAP**: one-line summary string (≤120 chars) shown when the loader injects this doc — Claude reads it before the body lands.

Add a `MCP_<X>.md` with no entries in these maps and it will sit on disk forever, unloaded.

## Checklist

1. Create `src/superclaude/mcp/MCP_<Server>.md` — no frontmatter, single `<component name="..." type="mcp">` root.
2. Drop tool inventories, role descriptions, version/install blocks. Keep `<choose>` / integration / `<bounds>` / `<handoff>`.
3. Wire all three maps in `scripts/context_loader.py` (tool-name, TRIGGER_MAP, INSTRUCTION_MAP).
4. Add a row to `mcp/README.md` (Core or Plugin table) with flag and one-line mission.
5. If the server is core (auto-installed), register it in `cli/install_mcp.py::MCP_SERVERS`.
6. Run `make sync-user` (or scope-equivalent) and exercise the trigger — confirm the doc lands in context.

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
