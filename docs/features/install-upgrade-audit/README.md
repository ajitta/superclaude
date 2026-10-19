---
feature: install-upgrade-audit
phase: implementing
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Install / upgrade path audit (axis C)

Does a real user's upgrade (an older SuperClaude install, then the current CLI) and a later uninstall end in the state the code and README promise, at every scope, without touching user content? Correctness axes A1–A6. The over-engineering audit already covered deletability.

## Status

**P0–P4 done; fixes pending.** On `fix/install-upgrade-audit` from master 1dd9622c (v4.29.6), on Linux, in a sandbox only. Nothing was written to the real `~/.claude`.

- **Harness:** outside the repo (the round's scratch dir).
- **Matrix run 1:** 99 records, 21 PASS. Every plan hypothesis T1–T6 and R1 reproduced.
- **Findings:** 21 confirmed: 7 S1, 10 S2, 4 S3. One S1 needs an owner decision (C-06; recommended option (b)).
- **Fixtures:** 12 legacy-install eras plus the shipped-names history, under `tests/fixtures/`, loaded by `tests/unit/test_install_upgrade_scenarios.py`. All of those tests pass on current code.
- **Next:** P5 fixes (red test first, per [03-findings.md](./03-findings.md)), P6 matrix rerun, P7 verify, P8 Windows (owner), P9 release.
- **Sessions:** 0 so far.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Original request, owner decisions Q1–Q16 |
| [01-inventory.md](./01-inventory.md) | Era map; what the current version and each older era wrote, per scope; current handling |
| [01a-inventory-history.md](./01a-inventory-history.md) | Hook command forms, hook runtime state, shipped-names history, unlisted artifact kinds |
| [02-scenarios.md](./02-scenarios.md) | P0 harness, result table, U-series, fixtures |
| [02a-scenarios-edge.md](./02a-scenarios-edge.md) | X (scope), I (idempotency, uninstall, MCP, interruption), D (detection), E (robustness) |
| [03-findings.md](./03-findings.md) | Confirmed findings C-01–C-21, red tests, owner checkpoint, not reproduced |
| [03a-findings-review.md](./03a-findings-review.md) | P3 code review by axis, each branch tagged with its scenario |
| [05-plan.md](./05-plan.md) | Plan v2 index: owner summary, progress, phases, decisions, risks, review dispositions |
| [05a-plan-matrix.md](./05a-plan-matrix.md) | Plan v2 §1–§3: inventory, axes, scenario matrix |
| [05b-plan-review-fixes.md](./05b-plan-review-fixes.md) | Plan v2 §4–§5: code review, outputs and fix policy |
