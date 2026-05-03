# XML Prose Format Rules

> Body-format spec for SuperClaude content components — agent / skill / command / mode bodies under `src/superclaude/`. Derived from Claude.ai's system-prompt prose style, adapted with a minimal `-` line list so short labeled enumerations stay readable without resorting to verbose XML containers.
> Format-only — content/policy of any specific component is out of scope.
> **Scope.** This rule governs component bodies. The `*-authoring.md` meta-docs in `.claude/rules/` document this rule for human authors and may use plain Markdown (headers, tables) — they are not themselves SuperClaude components.

## Design Goals

- **Prose first.** Structured forms only where prose would mush distinct items together.
- **Token-efficient.** Prefer the simplest form that preserves readability — never reach for a heavier construct than the content needs.
- **One canonical shape per concept.** No parallel "options"; the rule below picks one form per situation.

## Root Structure

- Exactly one root XML wrapper tag (e.g., `<component name="…" type="…">`, `<claude_behavior>`).
- The root contains only sibling section tags — no bare prose at the root level.
- All content lives inside section tags or their nested sub-tags.

## Section Tags

- `snake_case` names that name the domain (`tool_guidance`, `memory_guide`, `refusal_handling`, `tone_and_formatting`, …).
- Tag name describes the topic, not the directive style.
- Top-level sections are flat siblings under the root.
- **Maximum nesting depth: 3 levels** (root → section → sub-section → list-item). Level 3 is reserved for plural↔singular list containers (see below). Plain sub-sections stop at level 2.

## Sub-Sections (Nested Tags)

- Use a sub-section tag only when a parent section contains genuinely distinct sub-domains.
- A sub-section's body is prose — typically a single framing sentence (e.g., `<mission>`, `<mindset>`) or a framing sentence followed by paragraphs. Don't open with a list.
- High-priority sub-sections may use a `critical_*` prefix (e.g., `critical_child_safety_instructions`) and may include a leading callout sentence before the rules.

## Content Inside Tags

Default to **prose paragraphs**:

- No markdown headers (`#`, `##`)
- No markdown tables
- No checkboxes (`- [ ]`)
- Numbered lists (`1.`, `2.`) are reserved for **ordered procedures** where step sequence is load-bearing — see Numbered form below. Don't use them for non-ordered enums.
- Third-person voice ("Claude does X", "the agent avoids Y") — never "you" or "I"
- Declarative / imperative-as-statement (state what is done or avoided, not "should" laundry-lists)

### Short-line list (`-` or `1.` prefix)

For **3-5 single-line items** that would mush together as prose, use a prefixed line. Pick the form by item type:

| Form | Pattern | Use when | Example tags |
|------|---------|----------|--------------|
| Numbered | `1. prose statement.` | **Ordered procedure** — step sequence is load-bearing; readers must execute in this order | `<actions>`, `<flow>` |
| Plain | `- prose statement.` | Unordered enum or homogeneous criteria — sequence is incidental | `<checklist>` |
| Labeled | `- Label: prose.` | Items use a **fixed label set** identical across components | `<tool_guidance>` (Proceed / Ask First / Never), `<bounds>` (Should / Avoid / Fallback) |
| Named | `- identifier-name: prose.` | Each item has a **component-specific identifier** that varies across components | `<focus>`, `<outputs>`, `<tools>`, `<gotchas>` (pattern-name), `<memory_guide>` (CategoryName), `<thinking>` (Principle-Name), `<behaviors>` (Pattern-Name) |

The Plain-vs-Numbered distinction: if reordering the items breaks meaning (step 2 depends on step 1), use Numbered. If items are independent criteria or homogeneous facts, use Plain.

The Labeled-vs-Named distinction: Labeled labels are part of the spec (every `<bounds>` in every component uses the same Should/Avoid/Fallback labels). Named identifiers are part of the content (each agent picks its own `<focus>` category names).

Do NOT use `-` or `1.` lines for free-form multi-paragraph prose — they are for short single-line enums only.

### Plural ↔ singular containers

Reserved for **multi-line items that don't fit on a single `-` line** — typically a `user:` / `assistant:` exchange or a multi-paragraph item with attributes. Always check first whether a `-` line would suffice.

- Container tag is the plural form, item tag is the singular (`<examples>` ↔ `<example>`, `<scenarios>` ↔ `<scenario>`).
- Each item holds prose (or structured prose like a `user:` / `assistant:` turn) — items do not nest further.
- Items may include a short framing attribute (e.g., `<example name="…">`); their body remains prose.
- Don't introduce a container just to hold a single item; don't reach for it when a `-` line would suffice.

### Long-form embedded enumerations

Lists embedded inside running prose are written as natural-language enumerations ("things include: x, y, and z") — not as bullets.

## Attributes vs. Body

- **Attributes carry identifiers**, not prose. Reserve them for short, fixed values: `name`, `type`, `path`, `level`, `next`, `servers`, etc.
- **Prose / guidance content goes in the tag body** as `-` lines or paragraphs. Do not stuff multi-clause prose into attribute strings (e.g., `<bounds should="…long sentence…" avoid="…">`) — quote-escape pain, no multiline, breaks the line-list convention.
- Rule of thumb: if the value reads like "a short identifier", attribute is fine. If it reads like "a sentence of guidance", move it to the body.
- **Decorative `note=` attributes are forbidden.** A `note=` attribute is allowed only when it carries one of: scope qualifier, safety directive ("do NOT …"), version gate, reference location, or quantified constraint. Remove it if the surrounding tag or body content already conveys the meaning.

## Quoting and Reference Conventions

| What | Convention | Example |
|------|------------|---------|
| URLs | single quotes | `'https://docs.claude.com'` |
| Model identifier strings | single quotes | `'claude-opus-4-7'` |
| UI / product feature names | double quotes | `"settings"`, `"user preferences"` |
| Tool / button names | bare or quoted | `thumbs down` button, `tool_search` |
| Reminder / classifier names | comma-separated bare list | `image_reminder, cyber_warning, …` |
| Dynamic variables | double curly braces | `{{currentDateTime}}` |

## Cross-References

- Reference another section by its plain English topic, not by tag path.
- When pointing to external docs, quote the URL inside the prose ("see Anthropic's prompting docs at 'https://…'").

## Skeleton

```xml
<component name="example-component" type="agent">

  <role>
    <mission>Single-sentence purpose.</mission>
  </role>

  <focus>
  - Category-One: capabilities described in prose.
  - Category-Two: capabilities described in prose.
  </focus>

  <actions>
  1. Verb-leading description of the first step.
  2. Verb-leading description of the second step.
  </actions>

  <tool_guidance>
  - Proceed: actions to do freely.
  - Ask First: actions requiring confirmation, with thresholds.
  - Never: actions the component must never take.
  </tool_guidance>

  <bounds>
  - Should: in-scope description.
  - Avoid: out-of-scope actions.
  - Fallback: escalation path when out-of-scope.
  </bounds>

  <examples>
    <example>
    user: short prompt illustrating a trigger.
    assistant: prose response showing the expected behavior.
    </example>
    <example>
    user: another trigger.
    assistant: another expected response.
    </example>
  </examples>

  <handoff next="/sc:next1 /sc:next2"/>
</component>
```

## Authoring Checklist

1. Wrap the body in one root tag with identifier attributes (`name`, `type`).
2. Split top-level concerns into `snake_case` section tags.
3. Nest sub-sections only when a section has ≥2 distinct sub-domains; depth 2 max for plain sub-sections.
4. Default to prose paragraphs.
5. For 3-5 short enum items, use a prefixed line: **Numbered** (`1.`) for ordered procedures, **Plain** / **Labeled** / **Named** (`-`) per item type. Skip the prefix for free-form prose.
6. Use plural↔singular containers (depth 3) only for multi-line items like `<examples><example>`.
7. Keep attributes for identifiers; move guidance prose into the tag body.
8. Use third-person ("Claude") and declarative voice.
9. Quote URLs and model strings in single quotes; UI/feature names in double quotes; runtime values in `{{variable}}`.
10. Reserve `critical_*` tag prefix for safety-critical sub-sections.
