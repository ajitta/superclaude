---
feature: test-exclusion-lift
phase: handoff
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 02. Handoff — what remains after test-exclusion-lift

This round lifted the `tests/unit/scripts` exclusion on an eight-run rule, added Dependabot for the pinned actions and dropped the `frozenset` item ([01-verification.md](./01-verification.md)). Commits b54f21fb, 10697cd1, 3e64dc82 on fix/test-exclusion-lift from master fe3195c1. Sessions: **0**. Delivered: merged into master at 09ea2e74 and pushed; no release needed. A new session inherits no execution authorization.

## Candidates

| # | Item | Kind of decision | Evidence | What it needs |
|---|---|---|---|---|
| 1 | In-function `superclaude.*` imports in tests — **207** by `grep -n "^    from superclaude\|^        from superclaude" tests/unit/*.py` (the lean round's 198 and a looser regex's 218 are other counts; use this command) | Carried, **no guard** (owner Q1, 2026-10-19: option a) | lean-round `06-handoff.md:31`; reviewer spot-checks found no circular/optional/side-effect reason in three samples | Nothing scheduled. Reopen only with a measured cost (import-time, readability complaint); a ratchet test was judged process for its own sake |
| 2 | Stacked-mode prompts exceed the 12,000 default (P2 INTERACTION dropped) | Observation | context-budget-restore `01-verification.md` | Reopen only if a real prompt loses a P1 module |
| 3 | `_is_multiline_tag` accepts only attribute-shaped continuation lines | Recorded limit | author-check-multiline `02-handoff.md` | Revisit on a user report |
| 4 | Windows native abort `0xC0000409` recurrence watch | Monitoring | this round's 8/8 clean runs; `git revert 3e64dc82` is the path | If any Windows `uv run pytest` aborts natively: revert, then bisect `tests/unit/scripts/parallel_ab/` under concurrent load; record pytest-asyncio version |
| 5 | Dependabot first PR | Confirmation | `.github/dependabot.yml` | After merge, confirm the ecosystem appears under Insights → Dependency graph → Dependabot; the first grouped PR arrives within a month and must pass the read-only-token CI |

Dropped this round: `frozenset("…".split())` rewrites (cosmetic, five carries). Recorded keeps stand (finding_policy; `CLAUDE_CONTEXT_MAX_TOKENS` knob; over-engineering-audit D01–D24).

## Next-round start

Check git state and delivery status before relying on this document. The deterministic hygiene backlog inherited from the lean round is now empty except the no-guard import item; the next round's candidates come from new evidence (a Windows abort, a Dependabot PR, a user report) or from a new audit axis the owner names.
