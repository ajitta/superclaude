---
type: "Command"
title: "Roadmap"
description: "Generate structured implementation workflows from PRDs and feature requirements. Use ONLY when user explicitly types `/sc:roadmap` — commits a phased workflow file, so a wrong fire skips the approval gate and creates files unasked. For a TDD implementation plan with exact file paths from a spec, use /sc:plan. Do NOT auto-trigger on \"what's the order of steps\" or short ad-hoc task lists — those get inline 2-3 step answer, not workflow file."
resource: "src/superclaude/commands/roadmap.md"
tags: [command]
generated:
  by: claude/fable-5
  at: 2026-08-31
---

# Roadmap

Generate structured implementation workflows from PRDs and feature requirements. Use ONLY when user explicitly types `/sc:roadmap` — commits a phased workflow file, so a wrong fire skips the approval gate and creates files unasked. For a TDD implementation plan with exact file paths from a spec, use /sc:plan. Do NOT auto-trigger on "what's the order of steps" or short ad-hoc task lists — those get inline 2-3 step answer, not workflow file.

Source of truth: `src/superclaude/commands/roadmap.md`.

Invoke with `/sc:roadmap`.

# Links

- [Commands index](/commands/index.md)
- [Bundle index](/index.md)
