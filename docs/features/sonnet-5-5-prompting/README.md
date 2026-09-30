---
feature: sonnet-5-5-prompting
phase: complete
owner: ajitta
created: 2026-09-30
updated: 2026-09-30
related: ../opus-5-5-default-model/README.md
---

# Sonnet 5.5 prompting guidance applied to `src/superclaude`

Claude Sonnet 5.5 shipped on 2026-09-28, and from Claude Code v2.1.284 the `sonnet` alias resolves to it. This folder covers four things: the official changes (API, prompting guide, Claude Code), what each one means for `src/superclaude`, headless probes on Sonnet 5.5, and the proposals that follow.

## Summary

- **The kernel already fits.** `core/RULES.md` scope discipline and verification-before-completion say what the Sonnet 5.5 guide adds to system prompts: no unrequested tests, files or refactors, stop at ideas when ideas were asked for, and run a real check before reporting done. In a probe, the SuperClaude arm ran an exercising check on a one-line change 2/2, and the bare Sonnet 5.5 arm 0/2.
- **`/sc:prompt` was wrong on Sonnet sessions (fixed in 4.17.0).** It had no Sonnet target. In 4 of 4 runs it assumed Opus 5.5, and in 2 of 2 it deleted a verification requirement as "Opus self-verifies". Sonnet 5.5 needs the opposite edit at low effort. One generic rule (delete thinking incantations) also contradicts the guide's single think-first line for JSON reasoning tasks.
- **The upstream gate has lifted.** The `claude-api` skill's migration reference now has Opus 5.5 and Sonnet 5.5 sections (commit `8a1541c`, 2026-09-29). This unblocked the prior feature's P4; the interim Opus 5.5 text was retired in 4.18.0.
- **The inline refusal extends to Sonnet 5.5.** A `/sc:prompt` argument that asks for written-out reasoning was declined as `reasoning_extraction` before the command ran, as on Opus 5.5.

Q1–Q5 are implemented on branch `fix/sonnet-5-5-prompting` (4.17.0+ajitta), with D1–D3 settled on the recommendations; four canaries on Sonnet 5.5 passed ([08-implementation.md](./08-implementation.md)).

## Documents

- [02-research.md](./02-research.md): specification, the five breaking API changes, the prompting deltas G1–G14 with their direction against current practice, Claude Code facts, and the upstream reference now covering both 5.5 models
- [03-analysis.md](./03-analysis.md): which deltas the kernel already covers, the S1–S16 surface inventory, and the three-way verification inversion
- [03a-analysis-probes.md](./03a-analysis-probes.md): headless probes on `claude-sonnet-5-5`, covering `/sc:prompt` inference and refusal, reasoning-exposure modes, kernel vs bare on scope and verification, and hook text after tool results
- [04-design.md](./04-design.md): proposals Q1–Q5, user decisions D1–D3, rejected ideas, deferred items
- [08-implementation.md](./08-implementation.md): what shipped, departures from 04-design, test and canary results
- [09-followups.md](./09-followups.md): interim Opus 5.5 text retired, CI repaired, okf re-sync, low/xhigh and fallback probes
