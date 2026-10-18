---
feature: test-exclusion-lift
phase: handoff
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 02. Handoff — what remains after test-exclusion-lift

This round lifted the `tests/unit/scripts` exclusion on an eight-run rule, added Dependabot for the pinned actions and dropped the `frozenset` item ([01-verification.md](./01-verification.md)). Commits b54f21fb, 10697cd1, 3e64dc82 on fix/test-exclusion-lift from master fe3195c1. Sessions: **0**. Delivered: merged into master at 09ea2e74; released as v4.29.3 (d61d79cd), which moved `stable` onto the Dependabot config. A new session inherits no execution authorization.

## Candidates

| # | Item | Kind of decision | Evidence | What it needs |
|---|---|---|---|---|
| 1 | In-function `superclaude.*` imports in tests — **207** by `grep -n "^    from superclaude\|^        from superclaude" tests/unit/*.py` (the lean round's 198 and a looser regex's 218 are other counts; use this command) | Carried, **no guard** (owner Q1, 2026-10-19: option a) | lean-round `06-handoff.md:31`; reviewer spot-checks found no circular/optional/side-effect reason in three samples | Nothing scheduled. Reopen only with a measured cost (import-time, readability complaint); a ratchet test was judged process for its own sake |
| 2 | Stacked-mode prompts exceed the 12,000 default (P2 INTERACTION dropped) | Observation | context-budget-restore `01-verification.md` | Reopen only if a real prompt loses a P1 module |
| 3 | `_is_multiline_tag` accepts only attribute-shaped continuation lines | Recorded limit | author-check-multiline `02-handoff.md` | Revisit on a user report |
| 4 | Windows native abort `0xC0000409` recurrence watch | Monitoring | this round's 8/8 clean runs; `git revert 3e64dc82` is the path | If any Windows `uv run pytest` aborts natively: revert, then bisect `tests/unit/scripts/parallel_ab/` under concurrent load; record pytest-asyncio version |
| 5 | Dependabot activation | Confirmation — **active since v4.29.3** (file on the default branch) | `.github/dependabot.yml` is on master; GitHub reads the file from the **default branch**, which is `stable` (confirmed via `gh api repos/ajitta/superclaude --jq .default_branch`), and `stable` moves only at `make release` | Dependabot starts with the next release (stable → a commit containing the file). Then confirm under Insights → Dependency graph → Dependabot; the first grouped PR targets master and must pass the read-only-token CI. Missed by the plan and its review — recorded here, not in a code change |

Dropped this round: `frozenset("…".split())` rewrites (cosmetic, five carries). Recorded keeps stand (finding_policy; `CLAUDE_CONTEXT_MAX_TOKENS` knob; over-engineering-audit D01–D24).

## Next-round axes (chat, 2026-10-19 — owner asked for a new audit axis; decision pending)

The deterministic hygiene backlog inherited from the lean round is exhausted (the no-guard import item aside). Four axes were laid out in chat with repo evidence; the owner asked which is most valuable and chose to record them and end the session before deciding.

| Axis | Question | What exists | What the round would do | Sessions |
|---|---|---|---|---|
| **A. Purpose-inference generalization** (the owner's stated ultimate purpose) | Does the shipped `purpose_before_action` rule (core/RULES.md, 4.29.0) generalize beyond the two fixtures it was piloted on, and does it cause over-inference on plain requests? | reframing-anchoring: `action-vs-purpose-text/code` baseline vanilla 0/4, sc-full 0/4 (sonnet); `sc-candidate` pilot 0/3 → 3/3 (text), 3/3 · 2/3 (code) on sonnet/opus ([02a-measurement.md](../reframing-anchoring/02a-measurement.md), [06-pilot.md](../reframing-anchoring/06-pilot.md)); `-stated` variants 4/4 — the model acts on a purpose when told; generalization, side effects and Fable are recorded as unmeasured ([README](../reframing-anchoring/README.md) status) | 4–5 new discriminating fixtures in other domains (ops, data, docs requests) + 2 plain-request controls for scope creep (`git_diff_max_files`, `output_not_regex`); discriminability pass first (vanilla ≤1/3); vanilla vs sc-full × sonnet/opus × 3; Fable excluded (headless billing) — extrapolation limit stated | **~70–90** |
| B. Current-model-generation re-audit | Which shipped content now only forces what Sonnet/Opus 5.5 already do? | 03a–03f section classifications (A/D labels) in reframing-anchoring; canaries sit at ceiling ([01-baseline.md](../reframing-anchoring/01-baseline.md)); rule: no deletion on "the model already does this" without a measurement | Pick D-labelled sections without an ablation; delete-file arm per §3 recipe; checks = what the text instructs; reach check first (MCP/fan-out content is unreachable headless); `make canary-gates` at the end | k sections × 2 × 2 × 3 (+4) |
| C. Install / upgrade path audit | Do `superclaude install` scopes, hook merge, `find_unshipped`, `RETIRED_AGENT_FILES`, `verify-drift`, `doctor` behave on upgrade over an older install? | over-engineering-audit D01–D24; `test_cli_install.py`; every recent round only saw "83 installed, drift clean" | ponytail six-axis audit of `cli/install_*.py` + `verify_drift.py` (~3,700 lines) with upgrade-scenario regressions (stale components, user hooks, settings.json markers) | 0 |
| D. Docs ↔ SSOT consistency | Which README/docs claims about commands, flags and modes are unpinned and drifted? | pinned: README count sites, `help.md`, codex map, install docs; unpinned: README flag table, mode descriptions, `docs/reports/` command citations | enumerate unpinned claims, fix drift, pin only what a test can hold | 0 |

Recommendation given in chat: **A** — the only axis that advances the owner's purpose directly, and the shipped rule's generalization is the largest unmeasured question in the repo; side-effect controls belong in the same round. Proposed cap **90**. B follows A's result; C and D are foundations that fit any gap. The owner has **not** decided; the next session opens with this table and asks for the axis and the cap.

## Next-round start

Check git state and delivery status before relying on this document. Then put the axis table above to the owner (axis + session cap), map the prior rounds the chosen axis builds on (A: reframing-anchoring + purpose-boundary; B: reframing-anchoring 03a–03f; C: over-engineering-audit; D: version-consistency/codex-map tests), and compose and independently review the plan per the usual sequence.
