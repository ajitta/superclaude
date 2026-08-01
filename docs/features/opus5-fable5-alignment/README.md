---
feature: opus5-fable5-alignment
phase: analysis
owner: ajitta
created: 2026-08-02
updated: 2026-08-02
---

# Opus 5 / Fable 5 Alignment

Realigning the SuperClaude content framework to Anthropic's published prompt- and context-engineering guidance for the Claude 5 model family.

## Problem

SuperClaude's instruction surface was tuned against Opus 4.x behavior. Several of those behaviors reversed in the Claude 5 family — self-verification became native, subagent delegation flipped from under- to over-eager, and default verbosity rose while `effort` stopped controlling it. Instructions that compensated for a weakness the model no longer has do not become neutral; the model still follows them, so they become active distortions.

Two constraints make this urgent rather than cosmetic. `CLAUDE_SC.md` imports three core files into every session, so every sentence competes with the user's task for a finite attention budget. And Anthropic states that prescriptive content tuned for prior models "can degrade output quality" on Fable 5 — which puts a burden of proof on a framework whose value proposition is prescription.

## Documents

| Doc | Contents |
|---|---|
| [02-research.md](./02-research.md) | Source research and the derived 14-rule authoring guideline (G1–G14), behavioral deltas, anti-pattern reference |
| [03-analysis.md](./03-analysis.md) | Audit of `src/superclaude` against the guideline; ranked, verified improvement proposals |

## Status

Research and audit complete. No framework edits applied — `03-analysis.md` is a proposal set awaiting review. High-severity items should be A/B probed with `claude -p` from outside the repo before adoption, per the `probe-observer-effect` gotcha.
