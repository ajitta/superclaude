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
3. [Phase 2 Discovery](./01a-phase2-discovery.md) — 2026-05-18, status: approved-for-plan — command output routing decisions (v2 review-clean)
4. [Phase 2 Plan](./05a-plan-phase2.md) — 2026-05-18, status: draft — 7-commit single-PR rollout: brainstorm canary → smoke gate → 5 replications → cleanup

Feature-level discovery (01-) skipped — `/grill-with-docs` session served as upstream discovery. Phase 2 discovery (01a-) scoped to command-edit sub-work only. Phase 2 plan (05a-) is additional plan doc per NNa rule — distinguisher `phase2` distinguishes it from primary `05-plan.md` (overall rollout). Letter suffix per `NNa-<phase>-<distinguisher>` rule for parallel/sub-phase docs within same slot.

## Status

Phase: **planning**. Phase 1 shipped (RULES.md rewritten, 9f50a6a). Phase 2 discovery + plan drafted; awaiting `/sc:implement --plan` execution.

## Open Decisions

- [ ] Cutoff date for legacy format (proposal: 2026-05-18)
- [ ] Migrate-on-touch policy (auto-promote on revision? manual only?)
- [ ] Validator command: extend `/sc:cleanup --type docs` or new `/sc:validate-docs`?
- [ ] Cross-feature link form: relative path (`../oauth-flow/05-plan.md`) vs slug ref (`[[oauth-flow#plan]]`)
- [ ] Standalone-to-feature promotion trigger: 2nd doc auto-detect, or manual `/sc:promote-feature`?
