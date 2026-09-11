---
type: "OutputStyle"
title: "Plain Language"
description: "Direct, specific prose in the user's language, without AI mannerisms or decorative structure."
resource: "src/superclaude/output-styles/plain-language.md"
tags: [output-style]
generated:
  by: process:okf-migrate
  at: 2026-09-11
---

# Plain Language

Direct, specific prose in the user's language, without AI mannerisms or decorative structure. Language-neutral by contract: names patterns (decorative contrast, empty signpost, ceremonial closing), never one language's phrases. Keeps Claude Code's coding instructions (`keep-coding-instructions: true`).

Source of truth: `src/superclaude/output-styles/plain-language.md`.

Delivery: installed to `<scope>/output-styles/`, the directory Claude Code scans; activated by `"outputStyle": "Plain Language"` in a settings file.

# Links

- [Output Styles index](/output-styles/index.md)
- [Bundle index](/index.md)
