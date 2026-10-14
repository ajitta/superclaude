---
sources:
  - {url: "https://code.claude.com/docs/en/sub-agents", retrieved: 2026-10-14}
---

# Subagent

## When to use this type

A subagent runs a focused task in a fresh context window with its own system prompt, tools and model, and returns a summary to the main conversation. It suits work that would flood the main conversation (wide searches, long logs) or that needs a restricted tool set.

## Project format and language

Read one or two existing subagents in the project (`.claude/agents/**/*.md`) for their format and language only. Claude Code scans `.claude/agents/` recursively, so search the subfolders too. Sections, how the return is stated and fields come from this file; a field `fields.yaml` does not list for agents is reported, not copied.

## Template (md)

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

When the task takes everything it needs from the delegation message and nothing from the project's CLAUDE.md files, offer `omitClaudeMd: true`: the subagent then starts without the user, project and local CLAUDE.md files (managed policy files still load). A rule that must still reach it goes in the delegation message; the main conversation keeps the full CLAUDE.md when it reads the result.

## Pitfalls

- `description` says when to delegate; Claude picks subagents by it. Keep it short: descriptions take up context.
- `name`: no `:` (reserved for plugin-scoped names), not starting with `-`, unique within the agents directory tree. The filename does not set the identity.
- Multi-word fields are camelCase (`disallowedTools`, `permissionMode`, `maxTurns`). A misspelled field is ignored without an error.
- Without `tools` the subagent inherits every available tool. With `tools`, a tool the body tells it to use but the list leaves out cannot run.
- Check how the person does each kind of work the task needs. If it runs a command-line program (a search CLI they set up, a build or test runner), `tools` needs `Bash` (or `PowerShell`) and the body names the command; `WebSearch` does not stand in for a search service they reach through a CLI. `Bash` grants the whole shell, so say so when offering it. When the same service is connected as an MCP server, name its MCP tools instead: a `tools` list drops MCP tools it does not name.
