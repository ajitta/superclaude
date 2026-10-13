---
sources:
  - {url: "https://code.claude.com/docs/en/sub-agents", retrieved: 2026-10-13}
---

# Subagent

## When to use this type

A subagent runs a focused task in a fresh context window with its own system prompt, tools and model, and returns a summary to the main conversation. It suits work that would flood the main conversation (wide searches, long logs) or that needs a restricted tool set.

## Match the project first

Read one or two existing subagents in the project (`.claude/agents/*.md`) and match their language, section layout, how they state what to return, and the frontmatter fields they use. A field `fields.yaml` does not list for agents is not copied; report it. With no subagent in the project, start from the template below.

## Fallback template (md)

```markdown
---
name: <name>
description: <When Claude should delegate to it: the kind of task and the signal in the request>.
tools: <Only what the task needs, for example Read, Grep, Glob>
---

You are <role> for <project or area>.

## Task

<What to do, with the paths, commands and conventions the task needs.>

## Return

<What the summary sent back must contain, and in what shape.>
```

## What the subagent sees

- Its own body as the system prompt, plus environment details. Not the Claude Code system prompt.
- Not the conversation history, the skills already invoked or the files already read. It works from the delegation message Claude writes. A fork is the exception: it inherits the conversation.
- The CLAUDE.md hierarchy and project rules, unless `omitClaudeMd: true`. Auto memory and the output style are not loaded (except in a fork).

So the body states the task context that is not in CLAUDE.md, and does not repeat what CLAUDE.md already gives it.

## Pitfalls

- `description` says when to delegate; Claude picks subagents by it. Keep it short: descriptions take up context.
- `name`: no `:` (reserved for plugin-scoped names), not starting with `-`, unique within the agents directory tree. The filename does not set the identity.
- Multi-word fields are camelCase (`disallowedTools`, `permissionMode`, `maxTurns`). A misspelled field is ignored without an error.
- Without `tools` the subagent inherits every available tool. With `tools`, a tool the body tells it to use but the list leaves out cannot run.
