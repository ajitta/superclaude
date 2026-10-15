---
paths: ["src/superclaude/modes/**", ".claude/rules/mode-authoring.md"]
---

# Mode Authoring Rules

> **Decision gate:** Create mode only for **cognitive posture** — how Claude thinks, communicates, prioritizes.
> - Mode = **HOW TO THINK** (mindset)
> - Command = **WHAT TO DO** (workflow)
> - Agent = **WHO TO BE** (domain expertise)

Mindset-shifting overlay, not procedure. Injected on-demand by `context_loader.py` TRIGGER_MAP.

## No Frontmatter

Modes not CC-native — no YAML frontmatter. Start directly with `<component>`.

```markdown
<!-- WRONG -->
---
name: brainstorming
---

<!-- CORRECT -->
<component name="brainstorming" type="mode">
```

## The 4-Axis Requirement

Every mode **must** define all four axes (enforced by `tests/unit/test_mode_structure.py`):

| Axis | Tag | Purpose | Style |
|------|-----|---------|-------|
| **Thinking** | `<thinking>` | Cognitive principles — how to reason | 3-5 `- Principle: explanation` lines |
| **Communication** | `<communication>` | Expression style — how to present | One line: short directives in full words (no abbreviations), joined by " \| " |
| **Priorities** | `<priorities>` | Trade-offs — what to optimize | Single-line prose with `A > B` pairs joined by " \| " |
| **Behaviors** | `<behaviors>` | Action patterns — what to do | 3-5 `- Pattern-Name: description` lines |

`<outcomes>` is **optional**, not a fifth axis. Include it only when the line states directives the four axes do not already carry (`Confidence score mandatory`, `Contradiction resolve required`). A line listing benefits the mode produces (`Better decisions | Pattern recognition | Self-awareness`) fails the deletion test in `.claude/rules/content-quality.md` — omit it. Shipped example that earns it: `MODE_DeepResearch.md`; modes that dropped theirs: `MODE_Brainstorming.md`, `MODE_Introspection.md`.

## XML Template

> Conforms to `.claude/rules/xml-prose-format.md`: single root, `snake_case` section tags, short-line lists (**Numbered** `1.` for ordered procedures, or `-` prefix as **Plain**, **Labeled**, **Named** per item type), plural↔singular containers (`<examples><example>`) for multi-line items. Modes use **Named** for `<thinking>` (Principle-Name) and `<behaviors>` (Pattern-Name); single-line prose for `<communication>`, `<priorities>`, `<outcomes>`. Modes have no ordered-procedure tag.

```xml
<component name="mode-name" type="mode">
  <role>
    <mission>Single sentence defining the cognitive posture.</mission>
  </role>

  <thinking>
  - Principle-Name: explanation in prose (3-5 items)
  </thinking>

  <communication>Short directives in full words, joined by | on one line.</communication>

  <priorities>Trade-off A > Trade-off B | C > D | E > F.</priorities>

  <behaviors>
  - Pattern-Name: concrete behavioral description (3-5 items)
  </behaviors>

  <!-- optional — only if it states directives the 4 axes miss; see note above -->
  <outcomes>Mandatory conditions joined by | pipes on a single prose line.</outcomes>

  <examples>
  | Trigger | Expected behavior |
  |---|---|
  | short scenario | one-line shape showing the mode-shaped behavior |
  | another scenario | another one-line shape |
  </examples>

  <bounds>
    <does>core capabilities described in prose (in-scope).</does>
    <never>out-of-scope actions described in prose.</never>
    <fallback>revert to default behavior when the cognitive overlay does not apply.</fallback>
  </bounds>

  <handoff next="/sc:command1 /sc:command2"/>
</component>
```

## Naming

- Filename: `MODE_<Name>.md`, capitalized words joined by `_` (e.g., `MODE_Brainstorming.md`, `MODE_Task_Management.md`); `MODE_DeepResearch.md` predates the `_` form and keeps its name
- Component name: lowercase-hyphenated (e.g., `name="brainstorming"`)
- Component type: always `type="mode"`

## Content Boundaries

**Allowed** (if essential to mindset):
- Expert framework mappings (Business Panel mode)
- Domain vocabulary tables where the terms are the mindset

Note: symbol systems and abbreviation maps as an *output contract* were removed from Token Efficiency mode — Anthropic's Claude 5 guidance names arrow chains and invented abbreviations as the wrong lever for brevity, and directs shortening by selective omission instead. Business Panel's symbols remain because they label expert framework output rather than compress prose.

**Forbidden** (belongs elsewhere):
- Step-by-step process → `commands/`
- API reference → `mcp/`
- Tool routing matrix → `core/FLAGS.md`
- YAML frontmatter (not CC-native)
- `type="config"` blocks → separate file like `RESEARCH_CONFIG.md`

## Supporting Config Files

Operational parameters too detailed for mode itself go in sibling `type="config"` files (e.g., `RESEARCH_CONFIG.md` — depth profiles, confidence thresholds). Not subject to mode validation (no 4-axis requirement); only the cross-reference check (`test_cross_references.py`) reads them.

## Format

Body-format rules (single root, list forms, quoting, cross-references, headers inside `<example>`, size targets) live in `.claude/rules/xml-prose-format.md`, which loads together with this file. They are not restated here.

## Checklist

1. Create `src/superclaude/modes/MODE_<Name>.md` starting with `<component>`
2. Define all 4 axes: thinking, communication, priorities, behaviors
3. Add `<bounds>` sub-tag form `<does>` / `<never>` / `<fallback>` (each tag's body is prose sentence; `<does>` + `<never>` required; `<fallback>` recommended for modes — explicit recovery when overlay doesn't apply) and `<handoff>`
4. Add trigger to `scripts/context_loader.py` TRIGGER_MAP
5. Add flag to `core/FLAGS.md` modes section
6. Run `uv run pytest tests/unit/test_mode_structure.py -v`
7. Update `modes/README.md` table
8. Re-sync an existing install: run `superclaude doctor --scope <s>` first, because `install --force` creates an install where none exists (gotcha `sync-scope-creates`); `make deploy` reinstalls only the CLI.

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|-------------|-----------|-----|
| Adding frontmatter | Modes aren't CC-native | Remove `---` block |
| Missing an axis | Incomplete cognitive overlay | Add all 4 |
| Process steps in mode | Mode = mindset, not procedure | Move to command |
| Tool routing in mode | Tool selection belongs in FLAGS | Move to `core/FLAGS.md` |
| Vague mission (<10 chars) | Doesn't guide behavior | Be specific about posture |
| `type="config"` in mode test | Config files aren't modes | Exclude from mode fixture |
| Decorative `note=` XML attrs | Unparsed boilerplate, token waste | See xml-prose-format.md "Attributes vs. Body" — `note=` only for scope/safety/version/reference/quantified constraint |