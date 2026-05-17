---
feature: rule-vs-instruction
phase: discovery
owner: ajitta
created: 2026-05-05
updated: 2026-05-18
---

# Rule vs. Instruction Authoring Guide

## Purpose

Discovery spec exploring how SuperClaude authors should distinguish "rule" content (always-on behavioral invariants — e.g., `core/RULES.md` `<core_rules>` block) from "instruction" content (task-triggered decision references — e.g., command flows, mode behaviors) in the framework's content tree, plus authoring-meta-doc additions that would help the distinction land consistently.

## Documents

1. [Discovery (English)](./01-discovery.md) — 2026-05-05, status: draft — primary spec
2. [Discovery (Korean i18n)](./01a-discovery-ko.md) — 2026-05-05, status: draft — Korean translation; same content as 01-discovery.md

## Status

Phase: **discovery**. Spec drafted; no design or plan yet. Authoring-meta-doc additions discussed are still proposals — no command or rule file edited as direct outcome of this spec yet. Open for further work.

## Migration Note

Promoted from standalone via `/sc:promote-feature rule-vs-instruction` on 2026-05-18 per doc-convention-v2 R4. Pre-promotion paths: `docs/specs/rule-vs-instruction-discovery-ajitta-2026-05-05{,-ko}.md`. Korean variant placed at `01a-discovery-ko.md` per multi-of-same-phase rule (`NNa-<phase>-<distinguisher>`, distinguisher: `ko`); English variant is primary `01-discovery.md`. Statuses preserved as-of original revision date. 0 inbound refs.

## Edge note — i18n filename pattern

Source Korean filename used `-ko` suffix AFTER the date (`...-ajitta-2026-05-05-ko.md`), which violates RULES.md standalone pattern `<slug>-<suffix?>-<username>-YYYY-MM-DD.md` (suffix should precede username, not follow date). Post-promotion, i18n variant lives cleanly at `01a-discovery-ko.md` per the multi-of-same-phase rule. Surface for RULES.md spec clarification: should standalone format include explicit i18n suffix convention, or is i18n only a feature-folder concern via NNa?
