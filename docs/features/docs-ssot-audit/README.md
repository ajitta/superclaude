---
feature: docs-ssot-audit
phase: implementing
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Docs ↔ SSOT consistency audit (axis D)

Where does a human- or model-facing document state something the single source of truth (code, `pyproject.toml`, `Makefile`, `hooks.json`, the workflows, the file tree) contradicts? Phases 0–3 only: intent, inventory, method, findings and a plan with owner questions. No doc or code was changed in this round.

## Status

**Phases 0–3 done; the owner ruled Q1–Q10 as recommended ([05-plan.md](./05-plan.md) §Owner rulings); the fix round on `fix/docs-ssot` landed G1–G5 behind the T1–T7 guards (written red first). The independent verification ([06-verify.md](./06-verify.md), PASS WITH FIXES) found Z-1–Z-12; all twelve are applied. Waiting on merge and release (owner; `make release` needs `CANARY_OK=1`, reason in [05-plan.md](./05-plan.md) §4).** On `docs/docs-ssot-audit` from `master` @ 3301b506 (v4.30.2), on Linux. Read-only on everything outside this folder; the real `~/.claude` was not touched.

- **Findings:** 25 confirmed: 0 S1, 7 S2, 18 S3 ([03-findings.md](./03-findings.md)). Every cited line was re-read before filing.
- **Mechanical pass:** 443 candidate hits from [tools/extract_refs.py](./tools/extract_refs.py), 24 of them real; the rest are placeholders, Claude Code's own names, or dated research docs quoting the artifacts of their day ([02-method.md](./02-method.md) §3).
- **Already guarded:** README counts and roster, the codex inventory table, `/sc:help`'s roster, install-doc ordering, Makefile help, rule citations and handoffs in shipped content ([01-inventory.md](./01-inventory.md) §3). None of the 25 findings is in a guarded shape.
- **Fix round:** `tests/unit/test_docs_ssot_guards.py` (T1–T5, T7) and the T6 extension of `test_version_consistency.py`, 19 red before the fixes; five group commits G1–G5 plus the two draft plans deprecated under `docs/archive/plans/`. Deviations: [05-plan.md](./05-plan.md) §Deviations.
- **Sessions:** 0 headless; one in-session pass per round.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Request, what counts as a defect, severities, scope |
| [01-inventory.md](./01-inventory.md) | Every doc in scope, its claim types, the SSOT per type, existing guard tests |
| [02-method.md](./02-method.md) | Extraction scripts, commands, triage rules, targeted reading |
| [03-findings.md](./03-findings.md) | D-01–D-25 with file:line, claim, SSOT evidence, severity, fix, guard; what was checked and holds |
| [05-plan.md](./05-plan.md) | Fix groups, proposed guard tests, owner questions Q1–Q10, rulings, deviations |
| [06-verify.md](./06-verify.md) | Independent verification at 8d61d296 (Korean): PASS WITH FIXES, Z-1–Z-12, and how each was applied |
| [tools/](./tools/) | `ssot_facts.py` (SSOT dump), `extract_refs.py` (reference extraction) |
