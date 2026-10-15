---
paths: ["src/superclaude/mcp/**", ".claude/rules/mcp-authoring.md"]
---

# MCP Authoring Rules

> **Decision gate:** Create an `MCP_*.md` for **superclaude workflow guidance** layered on top of an MCP server.
> - MCP doc = **WHEN/HOW to combine** with `/sc:*` commands and other servers (workflow patterns, decision tables)
> - NOT a tool catalog — CC's native MCP server description and `ToolSearch` already expose every tool, its parameters, and a usage hint.
>
> If the only content would be "this server has tools X/Y/Z that do A/B/C", do not create the file. CC already has it.

| Component | Role |
|-----------|------|
| Agent     | WHO TO BE |
| Command   | WHAT TO DO |
| Mode      | HOW TO THINK |
| MCP doc   | WHEN/HOW to use a server in SC workflows |

## Filename and Location

- Path: `src/superclaude/mcp/MCP_<ServerName>.md` (PascalCase, hyphens ok: `MCP_Chrome-DevTools.md`).
- The filename stem after `MCP_` is the **display name**; the lowercase form is what `context_loader.py` matches against (`mcp/MCP_Tavily.md` → `tavily`).
- Register the file in `scripts/context_loader.py` TRIGGER_MAP (see Wiring below); a file with no TRIGGER_MAP entry never loads.

## No YAML Frontmatter

MCP docs are pure content components. They are not auto-discoverable like agents/skills — they only enter context via the loader's trigger map. Frontmatter buys nothing and breaks the `<component>` root-tag invariant of the XML prose format.

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

- `<component name="...">` matches the lowercase server identifier used in `context_loader.py` (e.g., `tavily`, `playwright`, `chrome-devtools`); `type="mcp"` required.
- All multi-word tag names use `snake_case`.
- Required tags: `<role>` (with `<mission>`), `<choose>`, `<bounds>`, `<handoff>`.
- Optional tags: `<call_order>` (only when call sequence matters — e.g., a resolve→query pair), `<integration_patterns>` (cross-server / cross-command chains), `<examples>` (lookup table), `<example>` (rich illustration).
- `<choose>` — sub-tag form `<use>` / `<never>`, each body a prose sentence. Mirrors `<bounds>` slot-tag discipline; declarative voice, no hedging vocabulary (no `Avoid:` / `should:`). Sub-tag form keeps `<choose>` structurally distinct from neighboring Labeled sections.
- `<bounds>` — sub-tag form `<does>` / `<never>` / `<fallback>`. `<fallback>` is the native-tool or alternate-server escape hatch (load-bearing for MCP docs — readers need to know what to do when the server is wrong or unavailable).
- `<handoff next="...">` — 2-3 natural next `/sc:*` commands.
- Short enums: **Numbered** for ordered call sequences (`<call_order>`); **Named** (`- Identifier-Name:` per-item identifiers) for `<integration_patterns>`.

### Forbidden Body Content (the trim rule)

- **No `<tools>` inventory tables.** Listing every tool with parameters duplicates CC's MCP server description and `ToolSearch` output, costs tokens, and rots when the server adds/renames tools. Drop them.
- **No `<role>` body beyond `<mission>`.** The server's own description ("what it does") belongs to CC; the SC doc adds workflow value, not tool overview.
- **No version/install/setup blocks.** Install lives in `cli/install_mcp.py`. Per-server setup hints belong in `mcp/README.md` if anywhere.
- **No "Token Management" / token-budget sections** unless the budget is server-specific and non-obvious.

If a section reads like "this is what the server is" rather than "this is how I use the server inside SC", cut it.

## Wiring (mandatory — without this the file is dead)

`scripts/context_loader.py` matches the **user prompt text** (UserPromptSubmit hook only — it does NOT intercept `mcp__<server>__*` tool calls), so a new file must be wired into these maps:

1. **TRIGGER_MAP**: map user flags (`--tavily`, `--play`, …) and keyword regexes to the file. Pick a stable flag and add a regex row.
2. **COMPOSITE_FLAGS**: if the server participates in `--frontend-verify` / `--all-mcp`, add it to the matching composite-flag set so those umbrella flags pull the doc.
3. **INSTRUCTION_MAP / TIER_0_MAP**: by default the loader injects this string *instead of* the body — Tier 1 for behavioral docs (INSTRUCTION_MAP), a Tier 0 one-line hint for tool MCPs (TIER_0_MAP; never both). The body is injected only with `--verbose-context`, or when the file is in neither map (Tier 2). Put what the model must know by default into the string.

A file with no TRIGGER_MAP entry sits on disk unloaded.

## Format

Body-format rules (single root, list forms, quoting, cross-references, headers inside `<example>`, size targets) live in `.claude/rules/xml-prose-format.md`, which loads together with this file. They are not restated here.

## Checklist

1. Create `src/superclaude/mcp/MCP_<Server>.md` — no frontmatter, single `<component name="..." type="mcp">` root.
2. Drop tool inventories, role descriptions, version/install blocks. Keep `<choose>` / integration / `<bounds>` / `<handoff>`.
3. Wire `scripts/context_loader.py`: TRIGGER_MAP (flag/keyword regex) and the INSTRUCTION_MAP or TIER_0_MAP string, plus COMPOSITE_FLAGS if part of `--frontend-verify`/`--all-mcp`.
4. Add a row to the `mcp/README.md` server table with the flag and a one-line mission.
5. Register in `cli/install_mcp.py::MCP_SERVERS` when `superclaude mcp` should offer it.
6. Re-sync an existing install: run `superclaude doctor --scope <s>` first, because `install --force` creates an install where none exists (gotcha `sync-scope-creates`); when it reports an install, run `superclaude install --force --scope <s>`. `make deploy` reinstalls only the CLI. Then exercise the trigger and confirm the string (or body) lands in context.

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|-------------|-----------|-----|
| `<tools>` table listing every tool | Duplicates CC's MCP description / ToolSearch | Remove; keep only `<call_order>` if sequence is load-bearing |
| `<role>` paragraph describing the server | CC's MCP server description already does this | Trim `<role>` to a single `<mission>` line |
| Adding YAML frontmatter | Breaks single-root XML invariant; loader ignores it | Remove frontmatter |
| File present, no `context_loader.py` entry | File never loads | Wire TRIGGER_MAP and the INSTRUCTION_MAP or TIER_0_MAP string (plus COMPOSITE_FLAGS if applicable) |
| Install/setup instructions in body | Wrong layer; rots fast | Move to `cli/install_mcp.py` or `mcp/README.md` |
| Decorative `note=` XML attributes | Token waste | See xml-prose-format.md "Attributes vs. Body" — `note=` only for scope/safety/version/reference/quantified constraint |
| Generic "use this server for hard problems" | Vague trigger; no value over CC native | Replace with concrete trigger contexts in `<choose>` and chained `/sc:*` patterns in `<integration_patterns>` |