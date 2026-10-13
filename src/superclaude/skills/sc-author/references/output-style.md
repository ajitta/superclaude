---
sources:
  - {url: "https://code.claude.com/docs/en/output-styles", retrieved: 2026-10-13}
---

# Output style

## When to use this type

An output style sets Claude's role, tone and response format for every response in a session. Other needs fit other files:

- what Claude should know about the project: CLAUDE.md
- instructions for one kind of task: a skill
- something that must happen every time: a hook
- a helper with its own tools for a focused task: a subagent

## Match the project first

Read the project's existing styles (`.claude/output-styles/*.md`) and match their language and how they phrase instructions. With none, start from the template below.

## Fallback template (md)

```markdown
---
name: <Name shown in the picker>
description: <One line shown in the picker>
keep-coding-instructions: true
---

<How every response should read: role, tone, length, format. Instructions, not project facts.>
```

## Pitfalls

- `keep-coding-instructions` defaults to `false`: a custom style then drops Claude Code's built-in software engineering instructions (scoping changes, comments, verifying work). Set it to `true` when Claude still writes code in this style.
- The body is plain prose. An XML body is not used for output styles.
- Field names are lowercase with hyphens. A misspelled field is ignored without an error; YAML that does not parse loads the style under its file name with no fields.
- The terminal reads style files at startup: after creating or editing one, restart Claude Code.
- A style applies to the main conversation and to forks, not to other subagents.
