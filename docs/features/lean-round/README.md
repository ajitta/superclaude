---
feature: lean-round
phase: closed
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# Lean round

Apply verified implementation simplifications and routing-preserving content consolidation left by the [reframing-anchoring audit](../reframing-anchoring/03-analysis.md), without removing the framework's purpose-inference behavior.

## Status

Q1–Q8 accepted in chat on 2026-10-18. Branch `fix/lean-round-2` on `30a08be3` (v4.28.0). B0–B4 are committed, one commit per batch ([04-batches.md](./04-batches.md)); the local-scope install is re-synced with no drift. B6 done: `make canary-gates` 7/7 after the `core/` edits; spot check 22 sessions + attribution 9 ([05-release-gate.md](./05-release-gate.md)) — canaries and the text task unchanged, the code task sits at the same level on pre-lean and lean content (the pilot's 5/6 is not reproduced by the shipped kernel on either). Budget 35/40. Released: v4.28.1 (B0–B4) and v4.28.2 (B5: git gotchas onto `/sc:git`, delegated-subagent sentence 389→295 B). Round closed; next-round candidates in [06-handoff.md](./06-handoff.md).

Working plan: `.hermes/plans/2026-10-18_001500-lean-round.md` (v3; v2 preserved alongside it). The [intent record](./00-intent.md) preserves the approved decisions independently of that local plan.

B0–B4 target patch 4.28.1, followed by B6 verification. Q4 git consolidation and Q7 common-paragraph shortening remain B5 work for separate commits and a separate release; their approval does not move them into B4. Component deletion remains deferred. Merge, push, and actual release require a separate instruction.

Headless budget: **0/40 used** in this round. Planned checks: 4 gate sessions + 12 I0 sessions + 10 existing-canary sessions, leaving 14 spare. No new behavioral baseline has been run in Phase 0. Earlier measurements are historical evidence, not new results on this branch; see [the earlier baseline](../reframing-anchoring/01-baseline.md), [pilot](../reframing-anchoring/06-pilot.md), and [release gate](../reframing-anchoring/07-release-gate.md).

## Documents

- [00-intent.md](./00-intent.md): original request, purpose, constraints, and Q1–Q8 decisions.
- [01-kernel-footprint.md](./01-kernel-footprint.md): measured always-loaded import footprint and token-estimation limits.
- [02-b0-doc-split.md](./02-b0-doc-split.md): B0 — size split of the eight oversized prior-round docs (content unchanged).
- [03-deferred-evidence.md](./03-deferred-evidence.md): evidence (path:line) for the six deferred deletion/shrink candidates; no proposal.
- [04-batches.md](./04-batches.md): B1–B4 commits, per-defect red evidence, deviations from the audit, what was skipped and why.
- [05-release-gate.md](./05-release-gate.md): canary gates 7/7, spot check, pre-lean vs lean attribution on the code task, budget.
- [06-handoff.md](./06-handoff.md): closed-round state, the nine candidates for a next round with their evidence and the measurement each needs, start procedure.

## Prior audit evidence

The recovered session report is already preserved in [04a-ponytail-lean-recovered.md](../reframing-anchoring/04a-ponytail-lean-recovered.md); no duplicate copy is needed. It is raw input, not deletion approval. [04-ponytail-audit-1.md](../reframing-anchoring/04-ponytail-audit-1.md) verifies it, and [03-analysis.md](../reframing-anchoring/03-analysis.md) supersedes the leaf reports' severity and deletion recommendations. Findings must be rechecked against this round's base before application.
