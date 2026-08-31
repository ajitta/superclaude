---
type: "Mode"
title: "Verbalized Sampling Mode"
description: "Distribution-level answering (--vs) — k candidate responses with post-hoc probabilities instead of one modal answer."
resource: "src/superclaude/modes/MODE_Verbalized_Sampling.md"
tags: [mode]
sources:
  - id: vs-paper
    resource: "https://arxiv.org/abs/2510.01171"
    title: "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity (ICML 2026)"
  - id: vs-reverification
    resource: "docs/research/verbalized-sampling-reverification-chosh1179-2026-08-31.md"
    title: "Verbalized Sampling re-verification — evidence base for the mode"
generated:
  by: claude/fable-5
  at: 2026-08-31
---

# Verbalized Sampling Mode

Distribution-level answering (--vs) — k candidate responses with post-hoc probabilities instead of one modal answer.

Source of truth: `src/superclaude/modes/MODE_Verbalized_Sampling.md`.

Evidence limits (re-verified 2026-08-31): reserved for creative/ideation/landscape work — on factual/information-seeking queries it trades answer quality for diversity; the verbalized probabilities are never calibrated frequency estimates.[^vs-reverification]

[^vs-reverification]: Per-claim verdicts in the research doc listed under sources.

# Links

- [Modes index](/modes/index.md)
- [Bundle index](/index.md)
