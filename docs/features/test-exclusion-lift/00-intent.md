---
feature: test-exclusion-lift
phase: intent
status: approved-for-plan
owner: ajitta
created: 2026-10-19
revised: 2026-10-19
---

# 00. Intent — lift the tests/unit/scripts exclusion; Dependabot

## Original request

After repo-hygiene was merged:

> 다음 진행

Candidate table in chat (1 `tests/unit/scripts` exclusion, 2 in-function test imports, 3 `frozenset` rewrites, 4 Dependabot, 5/6 deferred observations); recommendation 1 + 3 (drop) + 4, cap 0:

> 권고대로 진행

Reviewed plan v2:

> Q1 권고대로,
> Q2 시작

(Q1 = carried in-function imports stay carried with no guard.)

## Problem

`pyproject.toml` addopts carries `--ignore=tests/unit/scripts` since c97705c0 as a workaround for a Windows-only native abort (exit 0xC0000409) that the commit does not tie to a test or a trigger; CI runs the directory in a separate step and `make test-scripts` runs it locally, so Windows developers miss 140 tests on every plain `uv run pytest`. The exclusion is wired into nine places (pyproject, Makefile, CI, workflow README, AGENTS.md, PRD open question, four test docstrings). Separately, the SHA-pinned `setup-uv` action and the `@v4`/`@v5` actions have no upkeep mechanism, and a cosmetic `frozenset` item has been carried through five handoffs.

## Desired outcome

A pre-fixed rule decides the lift: eight full-suite runs with the directory included on this Windows host — six sequential, two under concurrent load (the only recorded trigger shape) — all exit 0, or the exclusion stays and the asyncio tests under `tests/unit/scripts/parallel_ab/` become the bisect target. If lifted, every wiring site is updated in one commit, the isolated CI step goes, and a CHANGELOG line tells contributors the default run now includes the directory. `.github/dependabot.yml` groups the three actions into one monthly PR against `master`. The `frozenset` item is dropped from the carried list.

## Affected users and systems

- Contributors: `uv run pytest` grows by ~140 tests / ~45 s and covers the directory on Windows; `make test-scripts` becomes a convenience that inherits addopts.
- CI: one fewer step per matrix entry; Dependabot PRs (read-only token — fine for the current workflow).
- Nothing installed into `~/.claude` changes; no release.

## Constraints and decisions

| Topic | Approved decision |
|---|---|
| Lift rule | all eight runs rc 0 → lift; any abort → keep, record, bisect target named |
| Scope | handoff rows 1 (exclusion), 3 (frozenset, dropped), 6 (Dependabot); row 2 carried with no guard; rows 4/5 deferred |
| Branch | fix/test-exclusion-lift from master fe3195c1 |
| Sessions | 0 — the reproduction runs and a CI run are the oracles |
| CHANGELOG | one `### Changed` line for the lift (contributor-facing, per precedent); none for Dependabot |
| Delivery | commit per item; merge/push on a later word; no release |

## Open questions

None blocking.

## Plan and review

Local working plan: .hermes/plans/2026-10-19_031500-test-exclusion-lift.md (reviewed v2; v1 beside it). The review added the concurrent-load runs, the environment record, the `test-scripts` addopts fix, the Dependabot `groups` and the CHANGELOG line.
