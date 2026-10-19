---
feature: pressure-readout
phase: closed
owner: ajitta
created: 2026-10-20
updated: 2026-10-20
---

# Pressure probes, vanilla vs sc-full (10- and 30-run readout)

The question: when a prompt pushes to skip verification (a hurry, a tech lead's dictated fix, sunk cost), does sc-full verify more often than vanilla? The model was sonnet at low effort. The smoke round in [borrowed-checks](../borrowed-checks/06-verify.md) had two runs per task and arm, so it said nothing about a difference between arms.

## Status

Closed on branch `feature/pressure-readout`. 200 sessions in two batches, $16.63 API-equivalent (subscription).

- **Hurry probe: SC helps** (sc-full 30/30 vs vanilla 20/30, one-sided Fisher p = 0.0004, pre-registered rule 3).
  - All ten vanilla misses look the same: Edit, then `DONE`, with no run and no disclosure.
  - The unhurried control is 10/10 on both arms, so the drop comes from the hurry.
- **Dictated-fix and sunk-cost probes:** both arms are at ceiling (9–10/10), so these two probes do not separate the arms.
- **Two harness changes:**
  - `probe-verify-claim` now uses the same grader as its pressure twin.
  - Every arm now runs without the claude.ai account's synced plugins, skills and connectors. These had loaded in every eval round since at least 2026-10-19, varying from session to session. No earlier decision flips.
  - `sc-command-only` now really drops the always-loaded core. The project install also imports it from `.claude/CLAUDE.md`, so that arm used to read as sc-full.

## Documents

| File | Content |
|---|---|
| [00-prereg.md](./00-prereg.md) | Question, setup, batches, decision rules (committed 58 s into batch B, before any result file existed; corrections appended) |
| [02-verify.md](./02-verify.md) | Independent verification (opus, high effort): PASS WITH FIXES, findings 1–7 and the sc-command-only defect, all applied |
| [01-readout.md](./01-readout.md) | Primary and secondary cells, failing-transcript classes, batch A, the isolation fault, limits |
