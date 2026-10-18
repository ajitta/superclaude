---
feature: author-check-multiline
phase: handoff
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 02. Handoff — what remains after author-check multiline + release 4.29.2

This round closes the author-check multiline candidate carried since harness-checker-hygiene (fix a1d6ca7a on fix/author-check-multiline from master 02f31d7b; evidence in [01-verification.md](./01-verification.md)) and releases the accumulated `[Unreleased]` entries as 4.29.2. Headless sessions used: **0**. Delivered: merged at 37a6501b, released as **v4.29.2** at 1f57aa62 (master = stable = tag), local install synced; see [README.md](./README.md) §Status. Remaining work is for a new session; this round grants it no execution authorization.

## Candidates

| # | Item | Kind of decision | Evidence | What it needs |
|---|---|---|---|---|
| 1 | Lean-round small leftovers: `frozenset` rewrites, Makefile help from `##` comments, CI `curl \| sh` → `setup-uv`, lift the `tests/unit/scripts` exclusion, in-function test imports | **Makefile help and CI setup-uv resolved** in [repo-hygiene](../repo-hygiene/README.md) (f40257cb, cd9f7e63); `frozenset`, `tests/unit/scripts`, in-function imports carried there | [mode-retire handoff](../mode-retire/02-handoff.md) §Small leftovers; [lean-round](../lean-round/README.md) | Each item's oracle is the suite/CI going green; the `tests/unit/scripts` exclusion exists because those tests can abort natively on Windows inside the full run (AGENTS.md) — lifting it needs a Windows run, not just CI |
| 2 | Frontmatter `yaml.safe_load` test idea | **Already shipped** — `tests/unit/test_frontmatter_yaml.py`, 3286c3f8 (2026-10-15); the "gap" note was stale since purpose-boundary. Historical row | purpose-boundary round notes; `author-check` F1 already rejects a `: ` inside `description` | Check overlap with F1 and `test_command_structure.py` before adding; may be a no-op |
| 3 | Stacked-mode prompts (≥3 mode flags + `--delegate`) exceed the 12,000 default; P2 `RULES_INTERACTION.md` dropped | Observation, no action proposed | [context-budget-restore/01-verification.md](../context-budget-restore/01-verification.md) last table row | Reopen only if a real prompt shape loses a P1 module |
| 4 | `_is_multiline_tag` accepts only attribute-shaped continuation lines | Recorded limit | `author_check.py` `_ATTR_LINE_RE` | A multiline opener with prose-like unquoted content on a continuation line is treated as prose (today's behavior). No shipped file has one; revisit only on a user report |

Recorded keeps stand: finding_policy ([mode-retire decisions](../mode-retire/01-decisions.md) item 2), the `CLAUDE_CONTEXT_MAX_TOKENS` knob.

## Next-round start

Check git state and delivery status before relying on this document. Read the candidates, select numbers and a session policy in chat, then compose and independently review the next plan.
