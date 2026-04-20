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

Every mode **must** define all four axes. Each axis has a different content style:

| Axis | Tag | Purpose | Style | Example |
|------|-----|---------|-------|---------|
| **Thinking** | `<thinking>` | Cognitive principles — how to reason | Bullet list of named heuristics (3-5) | `- Diverge then Converge: Generate breadth before filtering` |
| **Communication** | `<communication>` | Expression style — how to present | Pipe-separated directives (1 line) | `Ask questions over giving answers \| Frame as possibilities` |
| **Priorities** | `<priorities>` | Trade-offs — what to optimize | `A > B` comparison pairs | `Exploration > efficiency \| Understanding > solution` |
| **Behaviors** | `<behaviors>` | Action patterns — what to do | Bullet list of named patterns (3-5) | `- Socratic: Ask probing questions to uncover requirements` |

## XML Template

```xml
<component name="mode-name" type="mode">
  <role>
    <mission>Single sentence defining the cognitive posture</mission>
  </role>

  <thinking>
  - Principle: Explanation (3-5 items)
  </thinking>

  <communication>Style directives separated by | pipes</communication>

  <priorities>Trade-off A > Trade-off B | C > D (3-5 items)</priorities>

  <behaviors>
  - Pattern-Name: Concrete behavioral description (3-5 items)
  </behaviors>

  <outcomes>Expected results separated by | pipes</outcomes>

  <examples>
  | Input | Response |
  |-------|----------|
  | "user scenario" | Expected mode-shaped response |
  </examples>

  <bounds should="core capabilities" avoid="out-of-scope actions" fallback="Revert to default behavior when inapplicable"/>
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

## Checklist

1. Create `src/superclaude/modes/MODE_PascalCase.md` starting with `<component>`
2. Define all 4 axes: thinking, communication, priorities, behaviors
3. Add `<bounds>` (should/avoid/fallback) and `<handoff>`
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
| Decorative `note=` XML attrs | Unparsed boilerplate, token waste | `note=` only for scope/safety/version/reference/quantified constraint |
