---
sources:
  - {url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices", retrieved: 2026-10-14}
  - {url: "https://code.claude.com/docs/en/memory", retrieved: 2026-10-13}
---

# XML body

Read this only when the body is XML: `--xml`, an existing file whose body starts with a tag, or a new file in a project whose documents of the same type have XML bodies.

## When tags help

Tags separate kinds of content that would otherwise run together: instructions, context, examples, inputs. Wrap each kind in its own tag and nest tags when the content has a natural hierarchy. Tag names are descriptive and consistent within a document; no particular name carries special meaning.

## What the checker enforces

These hold for any XML body, whatever its tag names:

- One root element. Nothing but blank lines sits outside it. In a CLAUDE.md or other memory file, `@path` import lines and HTML comments may come before the root.
- Every opening tag has its closing tag, properly nested. A self-closing tag (`<item/>`) needs none.
- Output styles take a plain body, not XML.

Angle brackets in prose (`<3`, `<5KB`), in code, and placeholders inside a sentence (`docs/<name>/`) are text, not tags.

## Everything else follows the project

Tag names, nesting depth, which sections exist and their order come from the project's existing XML documents of the same type. Read one or two and reuse their names and layout. With none, name each part for what it holds, and keep the skeleton below as the starting point.

Converting a body between md and XML moves sentences into or out of tags; it removes none. Deleting a sentence is a separate step that needs approval.

## Fallback skeletons

Skill or command body (frontmatter stays YAML above it):

```xml
<instructions>
  <context>What this is for and what Claude needs to know first.</context>
  <steps>
    1. First action.
    2. Next action.
    3. The check that shows it worked.
  </steps>
  <references>
    - ${CLAUDE_SKILL_DIR}/references/topic.md: read when the condition holds.
  </references>
</instructions>
```

Subagent body:

```xml
<agent>
  <role>Who it is and what area it covers.</role>
  <task>What to do, with the paths and conventions it needs.</task>
  <return>What the summary sent back must contain.</return>
</agent>
```

CLAUDE.md (imports before the root; a rules file or an imported file has the root only):

```xml
@docs/architecture.md

<project>
  <commands>
    - Build: npm run build
    - Test: npm test
  </commands>
  <conventions>
    - Use 2-space indentation in YAML.
  </conventions>
</project>
```
