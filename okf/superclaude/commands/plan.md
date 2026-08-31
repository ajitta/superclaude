---
type: "Command"
title: "Plan"
description: "Make detailed impl plans w/ TDD tasks, exact file paths, verify commands. Use ONLY when user explicitly types `/sc:plan` — commits a plan doc under docs/plans/, so a wrong fire skips the approval gate and creates files unasked. NOT auto-trigger on \"what's the plan\" / \"how should we approach this\" — those get 2-3 sentence inline answer, not plan file."
resource: "src/superclaude/commands/plan.md"
tags: [command]
generated:
  by: claude/fable-5
  at: 2026-08-31
---

# Plan

Make detailed impl plans w/ TDD tasks, exact file paths, verify commands. Use ONLY when user explicitly types `/sc:plan` — commits a plan doc under docs/plans/, so a wrong fire skips the approval gate and creates files unasked. NOT auto-trigger on "what's the plan" / "how should we approach this" — those get 2-3 sentence inline answer, not plan file.

Source of truth: `src/superclaude/commands/plan.md`.

Invoke with `/sc:plan`.

# Links

- [Commands index](/commands/index.md)
- [Bundle index](/index.md)
