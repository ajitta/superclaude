---
feature: repo-hygiene
phase: handoff
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 02. Handoff — what remains after repo hygiene

This round closes lean-round leftovers 1b (Makefile help) and 1c (CI setup-uv) on fix/repo-hygiene from master b7ac6716 and records the frontmatter YAML test as already shipped in 3286c3f8. Evidence: [01-verification.md](./01-verification.md). Sessions: **0**. Delivery state: [README.md](./README.md) §Status. A new session inherits no execution authorization from this round.

## Candidates

| # | Item | Kind of decision | Evidence | What it needs |
|---|---|---|---|---|
| 1 | `tests/unit/scripts` default exclusion (`pyproject` addopts `--ignore`) | Investigation first | AGENTS.md; `Makefile` `test-scripts` comment: Windows-only native abort 0xC0000409 under memory pressure | Reproduce on Windows inside the full run before lifting; CI already runs the directory in its own step, so the cost of the exclusion is Windows-local only |
| 2 | 198 in-function `superclaude.*` imports in tests | Mechanical cleanup | lean-round `06-handoff.md:31` | Check each for an import-time side effect or circularity reason before hoisting; low value per the lean round |
| 3 | `frozenset("…".split())` rewrites | Cosmetic | lean-round `04-batches.md:43` | Twice deferred as cosmetic; recommend dropping from the list rather than carrying again |
| 4 | Stacked-mode prompts exceed the 12,000 default (P2 INTERACTION dropped) | Observation | context-budget-restore `01-verification.md` | Reopen only if a real prompt loses a P1 module |
| 5 | `_is_multiline_tag` accepts only attribute-shaped continuation lines | Recorded limit | author-check-multiline `02-handoff.md` | Revisit on a user report |
| 6 | Dependabot / action-pin upkeep | Not configured | `.github/` has no `dependabot.yml`; `setup-uv` is SHA-pinned with a `# v10.3.0` comment | Decide whether pinned actions get automated bumps; out of this round's scope |

Recorded keeps stand (finding_policy; `CLAUDE_CONTEXT_MAX_TOKENS` knob; over-engineering-audit D01–D24).

## Stale-note lesson

A handoff row that says "test idea" or "may be a no-op" is a verification target, not a candidate: grep `tests/` for the behavior before planning it. This round's v1 plan scheduled a test that had existed for four days.

## Next-round start

Check git state and delivery status before relying on this document. Read the candidates, select numbers and a session policy in chat, then compose and independently review the next plan.
