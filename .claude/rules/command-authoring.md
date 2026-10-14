---
paths: ["src/superclaude/commands/**", ".claude/rules/command-authoring.md"]
---

# Command Authoring Rules

> **Decision gate:** Make command for **user-facing workflow entry** (`/sc:*` slash commands).
> - Command = **WHAT TO DO** (ordered workflow)
> - Agent = **WHO TO BE** (domain expertise, auto-delegated)
> - Mode = **HOW TO THINK** (cognitive overlay)
>
> Need its own model, hooks, or subagent execution (`context: fork`)? Claude Code accepts those fields on command files, but SuperClaude commands run in the main session on the parent model — treat the need as a signal to reconsider the design, not as a field to add.

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
- `permissionMode`, `memory`, `color` — agent-only
- `autonomy` — not official CC field
- `model`, `context`, `agent`, `hooks` — CC accepts them on command files; SuperClaude keeps commands on the parent model in the main session (see the decision gate above)
- `disable-model-invocation` — CC accepts it; SuperClaude keeps every command reachable by delegation (see Trigger Policy)

## Trigger Policy (auto vs on-request)

Commands install as CC skills — the harness lists each `description` for the model, which decides invocation from conversation context. Model judgment, not regex/hooks. The description is therefore a **model-facing invocation contract**. Every command stays model-invocable so a workflow step, another command or a sub-agent (Skill tool) can run it; the tier sentence says when the model may start it:

| Tier | Tier sentence | Use for | Examples |
|---|---|---|---|
| Auto | "Use when asked …" (natural request, no `/sc:X` needed — a typed `/sc:X` runs without the description) | Read/analysis workflows — false fire cheap | analyze, explain, review, research |
| On-request | "On request only — the user's /sc:X or a workflow step that names it." (exact sentence) | Mutates files, writes committed artifacts, orchestrates sub-agents, long-running loops | cleanup, build, implement, plan, auto-improve |

Rules:

- **Shape**: `<purpose — verb-led, what it does and writes>. <tier sentence>. Not for <cheap look-alike> — <direct alternative>.` ≤300 chars. No rationale ("so a wrong fire …"): it costs listing budget and routes nothing. Mechanically enforced: `tests/unit/test_command_structure.py` (`test_description_states_one_invocation_tier`, `test_description_has_negative_trigger_gate`, `test_description_fits_the_listing_budget`).
- **Why the cap**: every model-invocable description shares the skill listing's character budget (1% of the context window, 8,000-char fallback); on overflow CC drops descriptions of the least-used skills first.
- **Tier choice heuristic**: command mutates files, runs multi-agent orchestration, or writes committed artifacts → on-request. Read-only analysis or console-only output → auto.
- **No `disable-model-invocation`** (in `forbidden_command_fields`): it removes the description from the listing and blocks delegated runs and sub-agent preload. On-request wording is the gate; confirmations for risky operations live in the body (`<approval_required>`, `<bounds>`). Exception: a side effect found in use or reported (`content-quality.md` §1 Trigger) — that command gets the field with the report cited, and the `schemas.yaml` lint changes in the same commit.
- **Flipping tiers = description edit only**: swap the tier sentence, keep the negative gate and the 300-char cap. Then `uv run pytest tests/unit/test_command_structure.py` + re-sync (`superclaude install --force --scope user`; `make sync-user` may fail on Windows — see gotchas/general.md).

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

  <flags>
  - --flag-name <value>: behavior the flag turns on.
  </flags>

  <outputs>
  - Artifact: purpose
  </outputs>

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
- `<flow>` — ≥2 numbered steps in execution order; a step that anything points at starts with `N. Label:`
- Step pointers — anywhere in the body, point at a flow step as `the <Label> step`, or `the /sc:<name> <Label> step` for another command's flow, never by number. `test_command_structure.py` rejects `step <N>` and resolves each such label; a bare label (`after Confirm`) goes unchecked.
- `<flags>` — every `<syntax>` flag that is not a core/FLAGS.md global gets one `- --name <value>: behavior` line; `- --name` is what the hook and `test_command_structure.py` parse. A flag already defined elsewhere in the body (a flow step, `<outputs>`, a gotcha) gets a line pointing to it (a flow step by its label, a section by topic), not a restatement. A global name the command gives its own meaning is defined here too (`test_command_structure.py` catches a `<syntax>` value core/FLAGS.md does not allow, including any value for a global that takes none; a redefinition without a value, such as reflect's `--validate`, goes unchecked), and inside this command the hook then stops injecting that name's global directive (implement's `--plan` takes a plan path, not the global 5-line plan). A pointer takes one of these forms, which `test_command_structure.py` resolves: `the <Label> step` (see Step pointers), `the <topic> section|table`, `the <name> gotcha`, `the <name> pattern`, `the <topic> threshold`, `the <Tool> entry in the tools section`; a pointer in any other form goes unchecked.
- `<bounds>` — sub-tag form: `<does>` / `<never>` / `<fallback>` (each body prose sentence). `<does>` + `<never>` required; `<fallback>` optional (use when out-of-scope handling non-obvious). Sub-tag form keeps `<bounds>` structurally distinct from `<tool_guidance>` (session `S390`, a claude-mem record not in git, measured Claude conflating two when both used `- Label:` lines)
- `<handoff next="...">` — 2-3 natural next commands
- Optional: `<flags>` (required once `<syntax>` offers a non-global flag), `<outputs>`, `<tools>`, `<gotchas>`, `<examples>`

## Inherited from xml-prose-format.md

Rules below apply to all components, not restated above. See `.claude/rules/xml-prose-format.md` for full text.

- **Single root XML wrapper** — exactly one root tag per component body; sibling sections only at root level.
- **Long-form embedded enumerations** — lists embedded in running prose use natural-language enumeration ("things include x, y, z"), not bullets.
- **Quoting conventions** — URLs + model identifier strings in single quotes (`'https://…'`, `'claude-opus-4-7'`); UI / product / feature names in double quotes (`"settings"`); runtime variables in double curly braces (`{{currentDateTime}}`).
- **Cross-references** — point to other sections by plain English topic, not by tag path.
- **Markdown headers inside `<example>`** — permitted when illustration mirrors real markdown artifact (report template, commit message, user document); body-prose "no markdown headers" rule does not extend into `<example>` bodies.
- **Size target** — command body ≤200 lines (hard ceiling 300); extract overflow into referenced sibling file, not inline-bloat body.

## Checklist

1. Create `src/superclaude/commands/<name>.md` with frontmatter + XML; define every non-global `<syntax>` flag in `<flags>`
2. Verify `<component name="...">` matches filename
3. Write specific `description` (shown in `/menu`) — pick trigger tier + negative gate per "Trigger Policy"
4. Add `<gotchas>` for project-specific failure patterns
5. Run `uv run pytest tests/unit/test_command_structure.py -v`
6. Update `src/superclaude/commands/README.md` table
7. Run `make deploy`

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|-------------|-----------|-----|
| `name:` in frontmatter | Filename is the command name | Remove |
| `permissionMode:` | Agent-only, ignored for commands | Remove |
| `model:`, `hooks:` or `context:` | Valid in CC, but SuperClaude commands stay on the parent model in the main session | Remove |
| Vague description | Poor `/menu` display | Be specific: "Build X with Y" |
| Missing `<bounds>` | No scope/safety boundary | Add `<does>`/`<never>` |
| Mission doesn't match description | Confusing inconsistency | Align ≥30% word overlap |
| Decorative `note=` XML attrs | Unparsed boilerplate, token waste | See xml-prose-format.md "Attributes vs. Body" — `note=` only for scope/safety/version/reference/quantified constraint |