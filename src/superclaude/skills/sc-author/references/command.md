---
sources:
  - {url: "https://code.claude.com/docs/en/skills", retrieved: 2026-10-14}
---

# Slash command

## When to use this type

A file in `.claude/commands/` still works as a `/` command, but Claude Code recommends a skill for new work: a skill takes the same frontmatter and can also bundle supporting files. When a new command is requested, say this and let the person choose. Revising an existing command file stays a command.

## Project format and language

Read one or two existing command files in the project (`.claude/commands/**/*.md`) for their format and language only. Search the subfolders too: a subfolder is a namespace (`component.md` in a `frontend` subfolder is `/frontend:component`), and a project may keep all its commands in one. Sections, argument handling and fields come from this file unless the person chose the project's convention for a conflict; a field `fields.yaml` does not list for commands is reported, not copied.

## Template (md)

```markdown
---
description: <What the command does>
argument-hint: <[expected-arguments]>
---

<What to do with $ARGUMENTS, as numbered steps.>

1. <First action>
2. <Next action>
3. <The check that shows it worked>
```

## Pitfalls

- `name` and `paths` are not supported in command files; Claude Code ignores them. The filename sets the command name.
- Everything else follows the skill rules: a description in third person that says what it does, steps Claude can act on, and `disable-model-invocation: true` when the command has side effects.
