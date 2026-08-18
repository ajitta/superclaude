---
type: "Command"
title: "Prompt"
description: "Rewrite a prompt for Claude Opus 5 or Fable 5 — strip prompting folklore that degrades these models, apply model-specific behavioral deltas, mark missing context as placeholders. Use when user types `/sc:prompt`, asks to improve or tune a prompt for Opus 5 / Fable 5, or hands over a rough request to sharpen before sending. Do NOT auto-trigger on general prompt-engineering questions, on 'what does this prompt do', or on auditing prompt files across a repo — those get a direct answer or `/claude-api prompt-audit`."
resource: "src/superclaude/commands/prompt.md"
tags: [command]
timestamp: 2026-08-19
---

# Prompt

Rewrite a prompt for Claude Opus 5 or Fable 5 — strip prompting folklore that degrades these models, apply model-specific behavioral deltas, mark missing context as placeholders. Use when user types `/sc:prompt`, asks to improve or tune a prompt for Opus 5 / Fable 5, or hands over a rough request to sharpen before sending. Do NOT auto-trigger on general prompt-engineering questions, on "what does this prompt do", or on auditing prompt files across a repo — those get a direct answer or `/claude-api prompt-audit`.

Source of truth: `src/superclaude/commands/prompt.md`.

Invoke with `/sc:prompt`.

# Links

- [Commands index](/commands/index.md)
- [Bundle index](/index.md)
