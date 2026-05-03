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
- Checkboxes (`- [ ]`) only inside `<checklist>` (or a similarly verification-pending list); never in descriptive enums like `<focus>`, `<outputs>`, `<gotchas>`
- Markdown tables only inside `<examples>` (or a similarly dense-lookup tag) — see Compact tables below
- Numbered lists (`1.`, `2.`) are reserved for **ordered procedures** where step sequence is load-bearing — see Numbered form below. Don't use them for non-ordered enums.
- Third-person voice ("Claude does X", "the agent avoids Y") — never "you" or "I"
- Declarative / imperative-as-statement (state what is done or avoided, not "should" laundry-lists)

### Short-line list (`-` or `1.` prefix)

For **3-5 single-line items** that would mush together as prose, use a prefixed line. Pick the form by item type:

| Form | Pattern | Use when | Example tags |
|------|---------|----------|--------------|
| Numbered | `1. prose statement.` | **Ordered procedure** — step sequence is load-bearing; readers must execute in this order | `<actions>`, `<flow>` |
| Plain | `- prose statement.` | Unordered enum or homogeneous criteria — sequence is incidental | `<checklist>` |
| Labeled | `- Label: prose.` | Items use a **fixed label set** identical across components, and items remain single-line | `<tool_guidance>` (Proceed / Ask First / Never) |
| Named | `- identifier-name: prose.` | Each item has a **component-specific identifier** that varies across components | `<focus>`, `<outputs>`, `<tools>`, `<gotchas>` (pattern-name), `<memory_guide>` (CategoryName), `<thinking>` (Principle-Name), `<behaviors>` (Pattern-Name) |

The Plain-vs-Numbered distinction: if reordering the items breaks meaning (step 2 depends on step 1), use Numbered. If items are independent criteria or homogeneous facts, use Plain.

The Labeled-vs-Named distinction: Labeled labels are part of the spec (every `<tool_guidance>` in every component uses the same Proceed/Ask First/Never labels). Named identifiers are part of the content (each component picks its own `<focus>` category names).

Do NOT use `-` or `1.` lines for free-form multi-paragraph prose — they are for short single-line enums only.

### Sub-tag enumerations

When a section has a **fixed small set of named slots** that need (a) multi-line prose per slot, or (b) a structurally distinct shape from a neighboring Labeled list, use sub-tags instead of `- Label:` lines. Each sub-tag carries a single label; its body holds the prose.

```xml
<bounds>
  <should>refactor with proven patterns; preserve behavior.</should>
  <avoid>adding features mid-refactor; large risky changes.</avoid>
  <fallback>escalate to system-architect for boundary changes; ask the user when scope spans more than three modules.</fallback>
</bounds>
```

Use this form when:
- The section sits next to a Labeled section using the same `- Label:` shape and Claude must not conflate them (measured boundary blur — see commit `S390`).
- Any one slot reasonably needs multi-line prose that wouldn't fit a single `- Label:` line.
- The label set is fixed and small (2-4 slots).

Sub-tag bodies are prose, not lists. Depth stays at 2 (root → section → sub-section).

### Compact tables (`<examples>` and similar dense lookups)

For **dense fixed-shape data** — typically 3+ short rows of trigger → outcome — use a compact markdown table inside the tag. Use minimal separators (`|---|---|`); padding is unnecessary noise.

```xml
<examples>
| Trigger | Expected behavior |
|---|---|
| short trigger | one-line response shape |
| another trigger | another one-line shape |
</examples>
```

Reserve for ≤4 columns and short cells. The table form gives the lowest token cost when each row reads on a single line; a row that needs multi-line prose belongs in `<example>` (below).

### `<example>` for rich illustrations

When a single example needs multi-paragraph prose, a code block, a before/after comparison, a `user:` / `assistant:` turn, or attribute framing, use `<example>` directly as a standalone tag. One or more `<example>` siblings can appear under the root or under another organizing parent.

`<example>` body is **free-form prose** — pick whichever shape fits the illustration. The format does not prescribe a specific structure; common shapes include:

```xml
<example name="code-shape">
A typical refactor extracts cohesive helpers from a long method:

```python
def process(items):
    cleaned = [_normalize(x) for x in items]
    return [_format(x) for x in cleaned]
```

The agent runs the unit suite after each extraction.
</example>

<example name="narrative-shape">
The user reports a flaky test. The agent reproduces it locally first, captures the failing seed, and adds a deterministic fixture before touching production code.
</example>

<example name="conversation-shape">
user: this OrderModule keeps growing — apply SOLID where it helps.
assistant: Identifies the strongest violation first, proposes a single-responsibility split, validates with tests.
</example>

<example name="anti-pattern-shape" type="error-path">
- Input: /sc:build --type prod (after build fails with missing dependency).
- Why wrong: retrying the same build without fixing the root cause wastes tokens and time.
- Correct: investigate the error, fix the dependency, then re-run /sc:build.
</example>
```

The anti-pattern shape uses Labeled-line form (`- Input:` / `- Why wrong:` / `- Correct:`) — a fixed-set Labeled list inside `<example>` that documents an error path. Use it when an example needs to contrast wrong-vs-right behavior in three short lines; promote to narrative-shape if any line needs multi-line prose.

`<example>` is not a sub-item of `<examples>` — they are two distinct constructs. `<examples>` is the table-based dense lookup; `<example>` is the prose-form rich illustration. Choose by content shape: short uniform rows → `<examples>` table; multi-line / multi-paragraph / code-bearing → `<example>`.

### Other plural ↔ singular containers

For non-example list-shaped sections (e.g., `<scenarios>` ↔ `<scenario>`, `<gotchas>` ↔ `<gotcha>` when items genuinely need multi-line bodies), the plural-container ↔ singular-item pattern still applies. Container is plural, item is singular, each item holds prose, items do not nest further. Check first whether a `-` line list or a compact table would suffice.

### Long-form embedded enumerations

Lists embedded inside running prose are written as natural-language enumerations ("things include: x, y, and z") — not as bullets.

## Attributes vs. Body

**Attributes carry identifiers and short metadata. Body carries content and guidance.**

### Use an attribute when

- The value is a **short identifier** (≤30 chars, no full sentences): `name`, `type`, `path`, `level`, `next`, `servers`, `version`, `lang`.
- The value is **structural metadata** that names or scopes the tag rather than describing behavior — e.g., `<example name="solid-violation">`, `<handoff next="/sc:improve /sc:test"/>`.
- A self-closing tag conveys all needed information without a body — e.g., `<handoff next="..."/>`.

### Move to body when

- The value reads like **a sentence of guidance** ("escalate to X when …", "refactor with proven patterns and …").
- The value is **multi-clause** (would need pipe-separation hacks like `should="x|y|z"`).
- The value would benefit from **multi-line prose** or a list of items.
- Multiple long attributes accumulate on one tag — that's a signal the body should hold them, with each clause in its own line or sub-tag.

### Quick test

Read the attribute value aloud. If it sounds like a short label or filename, it's an attribute. If it sounds like a sentence, move it to the body — as a `- Label:` line, a sub-tag, or a paragraph, depending on shape.

### Decorative attributes are forbidden

A `note=` attribute is allowed only when it carries one of: scope qualifier, safety directive ("do NOT …"), version gate, reference location, or quantified constraint. Remove it if the surrounding tag or body content already conveys the meaning.

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
<root_wrapper>

  <section_one>
  Opening framing sentence stating the section's scope.

  Prose paragraph stating a behavior.

  Another prose paragraph stating a related behavior or boundary.
  </section_one>

  <section_two>
    <sub_section_a>
    Prose paragraph.
    </sub_section_a>

    <sub_section_b>
    Prose paragraph.
    </sub_section_b>
  </section_two>

  <named_enum_section>
  - Item-One: short prose statement.
  - Item-Two: short prose statement.
  </named_enum_section>

  <ordered_procedure_section>
  1. Verb-leading first step.
  2. Verb-leading second step.
  </ordered_procedure_section>

  <fixed_label_section>
    <label_a>distinct prose for label A.</label_a>
    <label_b>distinct prose for label B.</label_b>
    <label_c>distinct prose for label C.</label_c>
  </fixed_label_section>

  <examples>
  | Trigger | Expected behavior |
  |---|---|
  | short trigger | one-line response shape |
  | another trigger | another one-line shape |
  </examples>

  <example>
  Free-form prose illustrating a richer case. May include narrative, code blocks, multi-paragraph reasoning, or a `user:` / `assistant:` turn — whichever shape fits the content.
  </example>

</root_wrapper>
```

## Authoring Checklist

1. Wrap the body in one root tag with identifier attributes (`name`, `type`).
2. Split top-level concerns into `snake_case` section tags.
3. Nest sub-sections only when a section has ≥2 distinct sub-domains; depth 2 max for plain sub-sections.
4. Default to prose paragraphs.
5. For 3-5 short enum items, use a prefixed line: **Numbered** (`1.`) for ordered procedures, **Plain** / **Labeled** / **Named** (`-`) per item type. Skip the prefix for free-form prose.
6. For a fixed small set of named slots that need multi-line prose or distinct shape from a neighboring Labeled list, use sub-tags (e.g., `<should>`/`<avoid>`/`<fallback>`) instead of `- Label:` lines.
7. For dense fixed-shape data, use a compact markdown table inside `<examples>` (or similar lookup tag). For rich multi-line illustration, use standalone `<example>` instead.
8. Other plural↔singular containers (depth 3) are reserved for genuinely multi-line list items.
9. Keep attributes for short identifiers and structural metadata; move guidance prose into the tag body.
10. Use third-person ("Claude") and declarative voice.
11. Quote URLs and model strings in single quotes; UI/feature names in double quotes; runtime values in `{{variable}}`.
12. Reserve `critical_*` tag prefix for safety-critical sub-sections.
