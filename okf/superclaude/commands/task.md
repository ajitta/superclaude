---
type: "Command"
title: "Task"
description: "Execute complex tasks with intelligent workflow management and delegation. Use ONLY when user explicitly types `/sc:task` — delegates to sub-agents and mutates tracked task state, wrong fire cost a revert. Do NOT auto-trigger on single-step actions, small TODOs, or \"do X\" — those execute directly."
resource: "src/superclaude/commands/task.md"
tags: [command]
generated:
  by: claude/fable-5
  at: 2026-08-31
---

# Task

Execute complex tasks with intelligent workflow management and delegation. Use ONLY when user explicitly types `/sc:task` — delegates to sub-agents and mutates tracked task state, wrong fire cost a revert. Do NOT auto-trigger on single-step actions, small TODOs, or "do X" — those execute directly.

Source of truth: `src/superclaude/commands/task.md`.

Invoke with `/sc:task`.

# Links

- [Commands index](/commands/index.md)
- [Bundle index](/index.md)
