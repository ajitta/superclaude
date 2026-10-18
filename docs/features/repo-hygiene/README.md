---
feature: repo-hygiene
phase: intent
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Repo hygiene: Makefile help, CI setup-uv

Close two lean-round leftovers: `make help` generated from `##` comments with a test that keeps it complete, and CI installing uv through `astral-sh/setup-uv`. A third candidate (frontmatter `yaml.safe_load` test) was found already shipped in 3286c3f8 and is recorded as closed.

## Status

Intent approved in chat on 2026-10-19 (1b + 1c, 0 sessions, no release). Implementation on fix/repo-hygiene from master b7ac6716.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Original request, decisions, scope and limits |
