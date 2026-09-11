---
paths: ["src/superclaude/output-styles/**", ".claude/rules/output-style-authoring.md"]
---

# Output Style Authoring Rules

> **Decision gate:** Create an output style only for **how every response reads** — role, tone, response format — applied to every turn.
> - Output style = **HOW EVERY RESPONSE READS** (voice, always on, replaces Claude Code's default tone instructions)
> - Mode = **HOW TO THINK** (mindset, injected on demand by `context_loader.py`)
> - Core = **WHO WE ARE** (always-loaded rules via `CLAUDE_SC.md`)

Consumed natively by Claude Code from `<scope>/output-styles/`; SuperClaude only installs the file. Reference: https://code.claude.com/docs/en/output-styles.

## Frontmatter (required)

```markdown
---
name: Plain Language
description: One line, shown in the /config picker
keep-coding-instructions: true
---
```

- `name` — the value users put in `"outputStyle"`; Title Case, stable across releases (renaming breaks every settings file that selects it).
- `description` — one line, shown in the picker.
- `keep-coding-instructions: true` — always. A style shipped by a coding framework changes how Claude communicates, not whether it keeps Claude Code's software-engineering instructions (scoping changes, verifying work). Omitting the field drops them.

## Body

- Plain Markdown prose, not the `<component>` XML pattern. Claude Code sends the body verbatim as system-prompt instructions; `.claude/rules/xml-prose-format.md` does not apply.
- **Language-neutral.** The style ships to every SuperClaude user. No text in a specific natural language other than English, no example phrases from one language, and no rule that only makes sense for one language. Say "the user's language", not a language name. `tests/unit/test_output_style_structure.py` fails on any letter outside the Latin script (Hangul, kana, CJK, Cyrillic, Greek alike).
- Declarative present tense. Editing warnings over banned-word lists: name the pattern ("decorative contrast") and give at most one or two English examples of it.
- Body under ~600 words — it is sent with every request.
- Every sentence passes the deletion test in `.claude/rules/content-quality.md`: a rule that restates what Claude Code's default instructions already say costs tokens every turn and changes nothing.

## File Naming

`kebab-case.md`. The `name` field, not the filename, is what users select.
