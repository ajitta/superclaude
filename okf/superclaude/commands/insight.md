---
type: "Command"
title: "Insight"
description: "Capture structured session insights to per-project JSONL for human + tool analysis. Use ONLY when user explicitly types `/sc:insight` (with optional --list/--query/--stats/--review) — appends to .claude/insights.jsonl, wrong fire leaves a stored entry to delete. NO auto-trigger on \"let me note this\" or general observation — insights = deliberate capture, no auto-snapshot."
resource: "src/superclaude/commands/insight.md"
tags: [command]
generated:
  by: claude/fable-5
  at: 2026-08-31
---

# Insight

Capture structured session insights to per-project JSONL for human + tool analysis. Use ONLY when user explicitly types `/sc:insight` (with optional --list/--query/--stats/--review) — appends to .claude/insights.jsonl, wrong fire leaves a stored entry to delete. NO auto-trigger on "let me note this" or general observation — insights = deliberate capture, no auto-snapshot.

Source of truth: `src/superclaude/commands/insight.md`.

Invoke with `/sc:insight`.

# Links

- [Commands index](/commands/index.md)
- [Bundle index](/index.md)
