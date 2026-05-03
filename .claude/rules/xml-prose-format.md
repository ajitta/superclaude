# XML Prose Format Rules

> Structural conventions for authoring agent / skill / command bodies in the
> "Claude system-prompt" style: a single XML wrapper, `snake_case` section tags,
> and prose paragraphs inside (no markdown headers or bullets).
> Format-only — content/policy is out of scope.

## Root Structure

- Exactly one root XML wrapper tag (e.g., `<claude_behavior>`).
- The root contains only sibling section tags — no bare prose at the root level.
- All content lives inside section tags or their nested sub-tags.

## Section Tags

- `snake_case` names that name the domain (`product_information`, `refusal_handling`, `tone_and_formatting`, `user_wellbeing`, `knowledge_cutoff`, …).
- Tag name describes the topic, not the directive style.
- Top-level sections are flat siblings under the root.
- Maximum nesting depth: **3 levels** (root → section → sub-section → list-item). Level 3 is reserved for repeated leaf items inside a list-container (see below). Plain sub-sections stop at level 2.

## Sub-Sections (Nested Tags)

- Use a sub-section tag only when a parent section contains genuinely distinct sub-domains
  (e.g., `tone_and_formatting` → `lists_and_bullets`, `acting_vs_clarifying`, `capability_check`).
- A sub-section opens with a one-sentence framing line, then prose paragraphs.
- High-priority sub-sections may use a `critical_*` prefix (e.g., `critical_child_safety_instructions`)
  and may include a leading callout sentence before the rules.

## List Containers (Plural ↔ Singular Pattern)

Some sections are inherently a list of self-contained items (examples, gotchas, scenarios). These use a **plural container** wrapping repeated **singular item** tags — this is the only place level-3 nesting is allowed.

- Container tag is the plural form, item tag is the singular (`<examples>` ↔ `<example>`, `<gotchas>` ↔ `<gotcha>`, `<scenarios>` ↔ `<scenario>`).
- Each item tag holds prose (or structured prose like a `user:` / `assistant:` exchange) — items do not nest further.
- Items may include a short framing attribute (e.g., `<example name="...">`), but their body remains prose.
- Tables and bullets are still avoided inside items — keep prose form even when listing examples.
- Don't introduce a list container just to hold a single item; use a plain sub-section instead.

## Content Style Inside Tags

- **Prose paragraphs only.** No markdown headers, no bullet lists, no numbered lists, no tables.
- Paragraphs separated by a single blank line.
- Each paragraph is self-contained and topic-focused.
- Subject is named in the **third person** ("Claude does X", "Claude avoids Y") — never "you" or "I".
- Voice is **declarative / imperative-as-statement**: state what Claude does or avoids, not "should" laundry-lists.
- Lists embedded in prose are written as natural-language enumerations
  (e.g., "things include: x, y, and z") — never as bullets.

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
- When pointing to external docs, use a fully-quoted URL inside the prose
  ("they can check Anthropic's prompting documentation at 'https://…'").

## Skeleton

```xml
<root_wrapper>
<section_one>
Opening framing sentence stating the section's scope.

Prose paragraph stating a behavior.

Another prose paragraph stating a related behavior or boundary.
</section_one>

<section_two>
<critical_sub_section>
Lead sentence flagging that these rules require special attention.

Prose paragraphs of the rules.
</critical_sub_section>

<sub_section_a>
Prose paragraph.

Prose paragraph.
</sub_section_a>

<sub_section_b>
Prose paragraph.
</sub_section_b>
</section_two>

<section_three>
Single-paragraph section is allowed when the topic is small.
</section_three>

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
</root_wrapper>
```

## Authoring Checklist

1. Wrap the entire prompt in one root tag.
2. Split top-level concerns into `snake_case` section tags.
3. Nest sub-sections only when a section has ≥2 distinct sub-domains.
4. Stop at depth 2 for plain sub-sections; depth 3 is allowed only for plural-container ↔ singular-item lists (e.g., `<examples><example>…</example></examples>`).
5. Write prose paragraphs — no markdown formatting inside tags.
6. Use third-person "Claude" throughout.
7. Quote URLs and model strings in single quotes; UI/feature names in double quotes.
8. Use `{{variable}}` for runtime interpolation.
9. Use `critical_*` tag prefix only for safety-critical sub-sections.
