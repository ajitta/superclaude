# Mode Authoring Rules

When creating or modifying mode `.md` files in `src/superclaude/modes/`, follow these rules exactly.

## What Modes Are

Modes are **cognitive overlays** — they change how Claude thinks, communicates, and prioritizes, not what Claude does. A mode is a mindset, not a procedure.

- Mode = **HOW TO THINK** (mindset, posture)
- Command = **WHAT TO DO** (workflow, steps)
- Agent = **WHO TO BE** (persona, expertise)

## No Frontmatter

Modes do **not** use YAML frontmatter. Unlike agents, commands, and skills, modes are not managed by Claude Code's native content system. They are injected on-demand by `context_loader.py` based on flag/keyword triggers defined in `scripts/context_loader.py` TRIGGER_MAP.

```markdown
<!-- WRONG -->
---
name: brainstorming
description: Collaborative discovery
---

<!-- CORRECT — start directly with XML -->
<component name="brainstorming" type="mode">
```

## XML Structure

Every mode follows this template:

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

  <bounds will="core capabilities" wont="out-of-scope actions" fallback="Revert to default behavior when inapplicable"/>

  <handoff next="/sc:command1 /sc:command2"/>
</component>
```

## The 4-Axis Requirement

Every mode **must** define all four axes:

| Axis | Tag | Purpose | Content Style |
|------|-----|---------|---------------|
| **Thinking** | `<thinking>` | Cognitive principles — how to reason | Bullet list of named principles |
| **Communication** | `<communication>` | Expression style — how to present | Pipe-separated directives |
| **Priorities** | `<priorities>` | Trade-off guidance — what to optimize | `A > B` comparison format |
| **Behaviors** | `<behaviors>` | Action patterns — what to do differently | Bullet list of named patterns |

### Axis Content Guidelines

**`<thinking>`** — Define 3-5 cognitive principles. Each should be a named heuristic:
```xml
<thinking>
- Diverge then Converge: Generate breadth before filtering for depth
- Quantity then Quality: More ideas first, evaluate later
</thinking>
```

**`<communication>`** — Pipe-separated style directives (not a list):
```xml
<communication>Ask questions over giving answers | Frame as possibilities | Summarize patterns without concluding</communication>
```

**`<priorities>`** — Trade-off pairs using `>` operator:
```xml
<priorities>Exploration > efficiency | Understanding > solution | User's vision > best practice</priorities>
```

**`<behaviors>`** — Named behavioral patterns with descriptions:
```xml
<behaviors>
- Socratic: Ask probing questions to uncover hidden requirements
- Non-Presumptive: Seek explicit guidance, let user guide direction
</behaviors>
```

## Naming Convention

- Filename: `MODE_PascalCase.md` (e.g., `MODE_Brainstorming.md`, `MODE_Token_Efficiency.md`)
- Component name: lowercase-hyphenated (e.g., `name="brainstorming"`, `name="token-efficiency"`)
- Component type: always `type="mode"`

## Allowed Content

Modes may include **reference data** that is essential to the mindset:
- Symbol tables (Token Efficiency mode)
- Expert framework mappings (Business Panel mode)
- Abbreviation maps

## Forbidden Content

Modes must **not** contain:
- Step-by-step process instructions → use commands/
- API reference tables → use mcp/
- Tool routing matrices → use core/FLAGS.md
- YAML frontmatter → modes are not CC-native content
- `type="config"` components → use a separate config file (like RESEARCH_CONFIG.md)

## Supporting Configuration Files

Some modes require operational parameters that are too detailed for the mode itself. These are stored as separate files with `type="config"`:

- `RESEARCH_CONFIG.md` — depth profiles, confidence thresholds, tool routing for research mode

Config files live in `modes/` alongside their associated mode but are **not** subject to mode validation (no 4-axis requirement).

## Validation

After creating or modifying a mode, run:

```bash
uv run python -m pytest tests/unit/test_mode_structure.py -v
```

This validates:
- `<component type="mode">` present
- `<role>` and `<mission>` present and non-empty
- All four axes present: `<thinking>`, `<communication>`, `<priorities>`, `<behaviors>`
- `<bounds>` with `will` and `wont` attributes
- `<handoff>` with `next` attribute
- No YAML frontmatter
- Mission is descriptive (>10 characters)
- Minimum content length (>300 characters)

**Note:** `RESEARCH_CONFIG.md` is excluded from mode tests (it has `type="config"`, not `type="mode"`). It is validated by `test_content_structure.py`.

## Checklist for New Modes

1. Create `src/superclaude/modes/MODE_PascalCase.md` starting with `<component>`
2. Define all 4 axes: thinking, communication, priorities, behaviors
3. Add bounds (will/wont/fallback) and handoff
4. Add trigger to `scripts/context_loader.py` TRIGGER_MAP
5. Add flag to `core/FLAGS.md` modes section
6. Run `uv run python -m pytest tests/unit/test_mode_structure.py -v`
7. Update `modes/README.md` table
8. Run `make deploy`

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|-------------|-----------|-----|
| Adding frontmatter | Modes aren't CC-native content | Remove `---` block |
| Missing an axis | Incomplete cognitive overlay | Add all 4 axes |
| Process steps in mode | Mode = mindset, not procedure | Move steps to command |
| Tool routing in mode | Tool selection belongs in FLAGS | Move to core/FLAGS.md |
| `type="config"` in mode test | Config files aren't modes | Exclude from mode fixture |
| Vague mission (<10 chars) | Doesn't guide behavior | Be specific about cognitive posture |
| Decorative XML attributes (`note=` restating tag name, `priority=` on component) | Unparsed attributes accumulate as boilerplate — token waste | Remove. Only add attributes parsed by code, validated by tests, or adding info not in tag name/content |
