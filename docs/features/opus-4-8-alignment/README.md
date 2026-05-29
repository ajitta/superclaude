---
feature: opus-4-8-alignment
phase: planning
owner: ajitta
created: 2026-05-30
updated: 2026-05-30
related:
  - ../../reports/OPUS_4_7_ALIGNMENT.md
  - ../../specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md
  - ../../archive/specs/2026-03-23-model-agnostic-compatibility-design-chosh1179.md
---

# Opus 4.8 Alignment

Track how SuperClaude framework content should respond to Claude Opus 4.8 (released 2026-05-28), the third link in the model-alignment chain (4.6 → 4.7 → 4.8).

## Documents

| Phase | Doc | Status | Summary |
|---|---|---|---|
| Research | [02-research.md](./02-research.md) | complete | Opus 4.8 behavior + usage, evidence-backed diff vs 4.7, implications for the framework |
| Plan | [05-plan.md](./05-plan.md) | draft | Tiered improvements (ship / measure / monitor), R18-gated, with verified anchors + verification checklist |

_No separate `03-analysis`/`04-design` doc — the design bridge is research §8 (Implications for SuperClaude)._

## TL;DR

- **4.8 mostly *validates* existing SuperClaude decisions** — model-agnostic content, inherit-only effort (no `effort:` fields), coverage-first review, anti-over-engineering. These need *documenting*, not changing.
- **The only justified edits are version-pinned claims** now reading as 4.6/4.7-specific when they describe a stable, multi-version trait. Fix = version-*neutral* phrasing (not a 4.7→4.8 stamp that re-stales in ~41 days), consistent with the model-agnostic design.
- **Highest-value content fix:** `agent-authoring.md` still recommends `xhigh` "as a coding/agentic baseline" — 4.8 makes `high` the best-balance default and reserves `xhigh`/"extra" for difficult/long-async tasks. The effort-enum SSOT (`schemas.yaml`) is also stale (wrong default, `max` "4.6 only", `xhigh` missing) — folded into the same fix (T1-c).
- **Key behavioral reversal:** 4.7 under-triggered tools/subagents; 4.8 explicitly *improves* tool triggering — so the spawn-threshold rewrite stays deferred pending eval, but the version label gets de-pinned.
- **Monitor (out of scope now):** dynamic workflows (CC research preview), mid-conversation system messages, 1,024-tok cache minimum — harness/SDK-level, not content.

## Gate

`05-plan.md` is `draft`. Per `<workflow_gates>`, approval precedes `/sc:implement --plan`. No framework files were changed by this feature yet.
