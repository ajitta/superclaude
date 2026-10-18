---
feature: repo-hygiene
phase: handoff
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Repo hygiene: Makefile help, CI setup-uv

Close two lean-round leftovers: `make help` generated from `##` comments with a test that keeps it complete, and CI installing uv through `astral-sh/setup-uv`. A third candidate (frontmatter `yaml.safe_load` test) was found already shipped in 3286c3f8 and is recorded as closed.

## Status

Implemented on fix/repo-hygiene from master b7ac6716: intent 2e043236, Makefile f40257cb, CI cd9f7e63. Guard test red→green, `make -n` over all 21 targets, `gawk --posix` parity and CI run 39151749108 (3 jobs green) are in [01-verification.md](./01-verification.md). Sessions: 0. **Unmerged**; merge and push await the owner's instruction. No release planned (nothing installed changes).

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Original request, decisions, scope and limits |
| [01-verification.md](./01-verification.md) | Drift set, red→green, `make -n`, awk parity, CI run |
| [02-handoff.md](./02-handoff.md) | Carried leftovers, stale-note lesson, delivery status pointer |
