---
feature: skill-authoring-consistency
phase: complete
owner: ajitta
created: 2026-04-25
updated: 2026-05-18
---

# Skill Authoring Consistency

## Purpose

Align SuperClaude skill-authoring with Anthropic's documented skill spec — remove the silently-dropped `when-to-use` field, fold trigger keywords into `description`, fix stale figures, unify `<bounds>` across 4 authoring files (skill / agent / command / mode), and standardize cosmetics. Originally scoped as 4 sequential PRs (PR1 P0 → PR4 P3) of decreasing priority.

## Documents

1. [Discovery](./01-discovery.md) — 2026-04-25, status: draft — full consistency audit + D1-D9 design decisions
2. [PR1 P0 — Remove when-to-use](./05a-plan-pr1-p0.md) — 2026-04-25, status: draft — fold triggers into description, probe-verify auto-invocation
3. [PR2 P1 — Drift fixes](./05b-plan-pr2-p1.md) — 2026-04-25, status: draft, depends-on PR1
4. [PR3 P2 — Internal coherence + 4-file `<bounds>` unification](./05c-plan-pr3-p2.md) — 2026-04-25, status: draft, depends-on PR2
5. [PR4 P3 — Cosmetic + bilingual + conditional gotchas](./05d-plan-pr4-p3.md) — 2026-04-25, status: draft, depends-on PR3

## Status

Phase: **complete**. Per session memory, 8-phase retrospective followups bundle merged to master 2026-04-25. Skill-authoring spec changes confirmed in `.claude/rules/skill-authoring.md` + `<bounds>` shape in shipped skills. Source statuses preserved as draft per command spec.

## Migration Note

Promoted from standalone via `/sc:promote-feature skill-authoring-consistency` on 2026-05-18 per doc-convention-v2 R4. Pre-promotion paths: `docs/specs/skill-authoring-consistency-discovery-ajitta-2026-04-25.md`, `docs/plans/skill-authoring-consistency-pr{1..4}-p{0..3}-ajitta-2026-04-25.md`. 4 plan files mapped to 05-plan slot via multi-of-same-phase rule as parallel streams (`05a/05b/05c/05d-plan-pr{1..4}-p{0..3}.md`, distinguishers preserved from original filenames). No primary `05-plan.md` — all 4 are parallel streams per RULES.md NNa rule.

Fixed self-refs:
- 4 frontmatter `spec:` fields → `./01-discovery.md`
- 3 frontmatter `depends-on:` fields → relative paths chaining 05a→05b→05c→05d
- 4 body `Spec:` refs → `./01-discovery.md`

## External Inbound Warnings (flag only, out of migration scope per command bounds)

3 archive files hold stale paths to moved docs:
- `docs/archive/plans/skill-authoring-consistency-pr1-canary-test-scenario-ajitta-2026-04-25.md:4` references `docs/plans/skill-authoring-consistency-pr1-p0-...md`
- `docs/archive/plans/skill-authoring-consistency-pr1-canary-test-results-ajitta-2026-04-25.md` paired with above scenario doc
- `docs/archive/analysis/superclaude-session-retrospective-ajitta-2026-04-25.md:12` references discovery spec

Archived docs — out-of-scope for migration; fix in separate cleanup if desired.
