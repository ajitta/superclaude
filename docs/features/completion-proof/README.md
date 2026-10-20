---
feature: completion-proof
phase: implementing
owner: ajitta
created: 2026-10-20
updated: 2026-10-20
related: ../../research/superclaude-weakness-audit-ajitta-2026-10-20.md
---

# Completion proof, spec-gate isolation and the first multi-step probes

The round applies N1–N6 from the [weakness audit](../../research/superclaude-weakness-audit-ajitta-2026-10-20.md), revised after its [independent verification](../../research/superclaude-weakness-audit-verify-ajitta-2026-10-20.md). In short: a plan reaches `complete` only after its Proof ran at the current commit; the spec-gate review runs isolated and gets the original intent; README stops calling prose gates hard; brainstorm's decision-mode heuristic gets a default; two probes measure contracts between commands for the first time.

## Documents

- [00-prereg.md](./00-prereg.md): pre-registered rules for the two probes, written before any run
