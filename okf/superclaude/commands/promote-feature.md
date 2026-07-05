---
type: "Command"
title: "Promote Feature"
description: "Promote standalone docs sharing a slug into a feature folder per doc-convention-v2. Use ONLY when user explicitly types `/sc:promote-feature <slug>` to consolidate scattered standalone docs (`docs/specs/`, `docs/plans/`, etc.) into `docs/features/<slug>/`. Manual gate per Q2 policy — never auto-migrates without user confirm. NOT auto-trigger when /sc:cleanup --type docs surfaces 'consider promotion' suggestion — that's detection, this is action."
resource: "src/superclaude/commands/promote-feature.md"
tags: [command]
timestamp: 2026-07-05
---

# Promote Feature

Promote standalone docs sharing a slug into a feature folder per doc-convention-v2. Use ONLY when user explicitly types `/sc:promote-feature <slug>` to consolidate scattered standalone docs (`docs/specs/`, `docs/plans/`, etc.) into `docs/features/<slug>/`. Manual gate per Q2 policy — never auto-migrates without user confirm. NOT auto-trigger when /sc:cleanup --type docs surfaces "consider promotion" suggestion — that's detection, this is action.

Source of truth: `src/superclaude/commands/promote-feature.md`.

Invoke with `/sc:promote-feature`.

# Links

- [Commands index](/commands/index.md)
- [Bundle index](/index.md)
