---
paths: ["src/superclaude/modes/**", ".claude/rules/mode-authoring.md"]
---

# Mode Authoring Rules

> **Decision gate:** Create a mode only for **cognitive posture** — how Claude thinks, communicates, and prioritizes.
> - Mode = **HOW TO THINK** (mindset)
> - Command = **WHAT TO DO** (workflow)
> - Agent = **WHO TO BE** (domain expertise)
> - Skill = **WHICH CAPABILITY** (CC-native tool/hook)

Mindset-shifting overlay, not a procedure. Injected on-demand by `context_loader.py` TRIGGER_MAP.

## No Frontmatter

Modes are not CC-native content — no YAML frontmatter. Start directly with `<component>`.

```markdown
<!-- WRONG -->
---
name: brainstorming
---

<!-- CORRECT -->
<component name="brainstorming" type="mode">
```

## The 4-Axis Requirement

Every mode **must** define all four axes (per `.claude/rules/xml-prose-format.md`):

| Axis | Tag | Purpose | Style |
|------|-----|---------|-------|
| **Thinking** | `<thinking>` | Cognitive principles — how to reason | 3-5 `- Principle: explanation` lines |
| **Communication** | `<communication>` | Expression style — how to present | Single-line prose with directives joined by " \| " |
| **Priorities** | `<priorities>` | Trade-offs — what to optimize | Single-line prose with `A > B` pairs joined by " \| " |
| **Behaviors** | `<behaviors>` | Action patterns — what to do | 3-5 `- Pattern-Name: description` lines |

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

  <communication>Style directives joined by | pipes on a single prose line.</communication>

  <priorities>Trade-off A > Trade-off B | C > D | E > F.</priorities>

  <behaviors>
  - Pattern-Name: concrete behavioral description (3-5 items)
  </behaviors>

  <outcomes>Expected results joined by | pipes on a single prose line.</outcomes>

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

- Filename: `MODE_PascalCase.md` (e.g., `MODE_Brainstorming.md`)
- Component name: lowercase-hyphenated (e.g., `name="brainstorming"`)
- Component type: always `type="mode"`

## Content Boundaries

**Allowed** (if essential to the mindset):
- Symbol tables (Token Efficiency mode)
- Expert framework mappings (Business Panel mode)
- Abbreviation maps

**Forbidden** (belongs elsewhere):
- Step-by-step process → `commands/`
- API reference → `mcp/`
- Tool routing matrix → `core/FLAGS.md`
- YAML frontmatter (not CC-native)
- `type="config"` blocks → separate file like `RESEARCH_CONFIG.md`

## Supporting Config Files

Operational parameters too detailed for the mode itself go in sibling `type="config"` files (e.g., `RESEARCH_CONFIG.md` — depth profiles, confidence thresholds). Not subject to mode validation (no 4-axis requirement), validated by `test_content_structure.py`.

## Inherited from xml-prose-format.md

The following rules apply to all components and are not restated above. See `.claude/rules/xml-prose-format.md` for full text.

- **Single root XML wrapper** — exactly one root tag per component body; sibling sections only at root level.
- **Long-form embedded enumerations** — lists embedded in running prose use natural-language enumeration ("things include x, y, z"), not bullets.
- **Quoting conventions** — URLs and model identifier strings in single quotes (`'https://…'`, `'claude-opus-4-7'`); UI / product / feature names in double quotes (`"settings"`); runtime variables in double curly braces (`{{currentDateTime}}`).
- **Cross-references** — point to other sections by plain English topic, not by tag path.
- **Markdown headers inside `<example>`** — permitted when the illustration mirrors a real markdown artifact (report template, commit message, user document); the body-prose "no markdown headers" rule does not extend into `<example>` bodies.
- **Size target** — mode body ≤300 lines (hard ceiling 500); extract overflow into a referenced sibling file rather than inline-bloating the body.

## Checklist

1. Create `src/superclaude/modes/MODE_PascalCase.md` starting with `<component>`
2. Define all 4 axes: thinking, communication, priorities, behaviors
3. Add `<bounds>` sub-tag form `<does>` / `<never>` / `<fallback>` (each tag's body is a prose sentence; `<does>` + `<never>` required; `<fallback>` recommended for modes — explicit recovery when overlay doesn't apply) and `<handoff>`
4. Add trigger to `scripts/context_loader.py` TRIGGER_MAP
5. Add flag to `core/FLAGS.md` modes section
6. Run `uv run pytest tests/unit/test_mode_structure.py -v`
7. Update `modes/README.md` table
8. Run `make deploy`

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
