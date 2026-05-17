---
feature: doc-convention-v2
phase: planning
owner: ajitta
created: 2026-05-18
updated: 2026-05-18
---

# Doc Convention v2 — Feature Folder Migration

## Purpose

Replace flat per-type doc dirs (`docs/specs/`, `docs/plans/`, `docs/analysis/`, `docs/research/`) with per-feature folders that colocate every doc for one work item. Ends slug-drift, broken cross-links, and "which doc is canonical" ambiguity caused by scattered same-topic files.

## Documents

1. [Design](./04-design.md) — 2026-05-18, status: draft — full feature-folder spec
2. [Plan](./05-plan.md) — 2026-05-18, status: draft — overall migration phases + command updates
3. [Phase 2 Discovery](./01a-phase2-discovery.md) — 2026-05-18, status: complete — command output routing decisions (v2 review-clean)
4. [Phase 2 Plan](./05a-plan-phase2.md) — 2026-05-18, status: complete — 7-commit single-PR rollout: brainstorm canary → smoke gate → 5 replications → cleanup
5. [Open Decisions Resolution](./01b-discovery-open-decisions.md) — 2026-05-18, status: draft — 5 README open decisions resolved (cutoff date, migrate-on-touch, validator, link form, promotion trigger)

Feature-level discovery (01-) skipped — `/grill-with-docs` session served as upstream discovery. Phase 2 discovery (01a-) scoped to command-edit sub-work only. Phase 2 plan (05a-) is additional plan doc per NNa rule — distinguisher `phase2` distinguishes it from primary `05-plan.md` (overall rollout). Letter suffix per `NNa-<phase>-<distinguisher>` rule for parallel/sub-phase docs within same slot.

## Status

Phase: **planning**. Phase 1 shipped (RULES.md rewritten, 9f50a6a). Phase 2 shipped via PR #9 merged to master (4e79637) — 6 command-routing commits (brainstorm + design + plan + workflow + research + analyze) + status bumps. Phase 3 (validator + /sc:promote-feature command) pending — see [01b-discovery-open-decisions.md](./01b-discovery-open-decisions.md) for input requirements.

## Open Decisions

All 5 Phase 2 open decisions resolved — see [01b-discovery-open-decisions.md](./01b-discovery-open-decisions.md). Outcomes feed Phase 3 validator design (`/sc:cleanup --type docs` extension) and `/sc:promote-feature` command spec.
