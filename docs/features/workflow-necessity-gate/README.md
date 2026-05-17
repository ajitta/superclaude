---
feature: workflow-necessity-gate
phase: complete
owner: chosh1179
created: 2026-04-02
updated: 2026-05-18
---

# Workflow Necessity Gate

## Purpose

Embed over-engineering prevention into `/sc:design`, `/sc:implement`, and RULES.md workflow gates. Three markdown files modified — Necessity Gate (3-question test) in design.md flow, Phase Validation in implement.md flow, [R18 Necessity Test] rule + updated workflow_gates in RULES.md.

## Documents

1. [Discovery](./01-discovery.md) — 2026-04-02, status: draft — necessity-gate requirements + 3-question test design
2. [Plan](./05-plan.md) — 2026-04-02, status: draft — 3-file markdown edit task list

## Status

Phase: **complete**. [R18 Necessity Test] rule confirmed present in RULES.md core_rules block. design.md flow includes Necessity step ("For each proposed component, apply [R18 Necessity Test]"). Source statuses preserved as draft per command spec.

## Migration Note

Promoted from standalone via `/sc:promote-feature workflow-necessity-gate` on 2026-05-18 per doc-convention-v2 R4. Pre-promotion paths: `docs/specs/workflow-necessity-gate-discovery-chosh1179-2026-04-02.md`, `docs/plans/workflow-necessity-gate-chosh1179-2026-04-02.md`. Original owner chosh1179 preserved in README frontmatter. Statuses preserved as-of original revision date. Fixed 1 non-standard `spec:` frontmatter field + 1 body self-ref to relative paths.
