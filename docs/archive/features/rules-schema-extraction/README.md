---
feature: rules-schema-extraction
phase: complete
owner: ajitta
created: 2026-04-14
updated: 2026-05-18
---

# Rules Schema Extraction

## Purpose

Extract RULES.md schema constants (forbidden field lists, enum sets, regex patterns) into a single SSOT file (`.claude/rules/schemas.yaml`) so downstream tooling (validators, structural tests) reads from one source instead of grepping RULES.md prose. Companion research doc at `docs/research/rules-xml-conversion-ajitta-2026-04-14.md` covers XML-vs-prose tradeoffs.

## Documents

1. [Discovery](./01-discovery.md) — 2026-04-14, status: draft — schema-extraction requirements
2. [Plan](./05-plan.md) — 2026-04-14, status: draft — 6-phase task breakdown

## Status

Phase: **complete**. `.claude/rules/schemas.yaml` exists in production; test_rules_schemas.py validates downstream consumption. Source statuses preserved as draft per command spec.

## Related (separate slug — promotion candidate)

`docs/research/rules-xml-conversion-ajitta-2026-04-14.md` — research on XML-vs-prose tradeoffs informing this work. Different slug (`rules-xml-conversion` not `rules-schema-extraction`); could be promoted to own feature folder OR pulled into this folder as `02-research.md` if treated as input research. Decision deferred.

## Migration Note

Promoted from standalone via `/sc:promote-feature rules-schema-extraction` on 2026-05-18 per doc-convention-v2 R4. Pre-promotion paths: `docs/specs/rules-schema-extraction-discovery-ajitta-2026-04-14.md`, `docs/plans/rules-schema-extraction-ajitta-2026-04-14.md`. Statuses preserved as-of original revision date.
