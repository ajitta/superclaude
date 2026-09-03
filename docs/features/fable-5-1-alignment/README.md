---
feature: fable-5-1-alignment
phase: complete
owner: ajitta
created: 2026-09-03
updated: 2026-09-04
related: ../opus5-fable5-alignment/
---

# Fable 5.1 Alignment

Delta alignment of the SuperClaude content framework to the Claude Fable 5.1 release (2026-09-01), on top of the August 2026 [Opus 5 / Fable 5 alignment](../opus5-fable5-alignment/README.md).

## Problem

Fable 5.1 changed little at the prompt level. Anthropic states that Fable 5 prompts perform well on it unchanged, and Claude Code now injects the Fable 5.1 tuning blocks (autonomy, scope, batching, progress updates) into the system prompt itself. That moves the framework's job: it must not duplicate what the harness now says, must not contradict it, and should fill only the gaps the harness leaves. Three things in `src/superclaude` do not meet that bar today: `commands/prompt.md` still targets Fable 5 and carries one removal rule that now inverts the 5.1 guidance; the delegation rule never says what the main loop does while a delegate runs; and the compaction preservation list exists twice and matches neither the six-item guidance.

## Inputs

- `C:\Users\ajitta\ObsidianVault\fable-5-1-obsidian-notes\` — ten curated notes plus a verification report that checked every factual claim against official docs on 2026-09-02.
- The Fable 5.1 prompting guide, migration guide, and overview pages, fetched as markdown on 2026-09-03.
- The Claude Code system prompt observed in a Fable 5.1 session on 2026-09-03.

## Documents

| Doc | Contents |
|---|---|
| [03-analysis.md](./03-analysis.md) | Fable 5 → 5.1 delta, harness-vs-framework coverage matrix, findings with file:line evidence, decided non-changes, pending harness facts |
| [05-plan.md](./05-plan.md) | Five change sets (sediment, on-demand gap fills, refusal classification, measurement-gated addition, deferred items), verification gates with cost, open questions, sequencing |

## Status

Complete 2026-09-04. All change sets applied on `feature/fable-5-1-alignment` and merged to `master`. Two Fable 5.1 canary runs (master baseline and branch) score identically on all 14 tasks: 13/14 fully passing, 7/7 hard gates, 0 refusals; the one shared miss is `plan-routing`, the task-versus-convention conflict recorded in August. CS-D measured at xhigh (n=2 per arm): means down 11% duration and 18% output tokens, ranges overlapping. Total eval spend across both canary runs, the invalidated first run, and the four CS-D runs: about $35.

| Change set | Status |
|---|---|
| CS-A sediment (`prompt.md`, listings, one comment) | applied, `6dda706` |
| CS-B delegation run-alongside + compaction SSOT | applied, `d24bc69` |
| CS-C refusal classification in headless runners | applied, `196d3e0`; follow-ups `c110e8f` (auto-improve stops after 3 consecutive refusals), `5ea27cb` (parallel_ab reads stream-json for the category) |
| CS-D long-output sentence in `RULES_DOCS.md` | applied, `fbff547`; gate met weakly (see 05-plan.md section 3) |
| CS-E deferred items | promoted 2026-09-04 by user decision, `3bcb6bc`: G-f verdict vocabulary, G-g feature contracts, G-h search nudge, G-i quoting example; G-j already covered by `git_diff_max_files`; chatspeak cleaned in the four edited files only |
| Harness | `d8d1610` (`--effort` passthrough), `e8caf0e` (runs outside `~/.claude`, PowerShell in transcript gates, stash-aware `file_preserved_glob`) |

Follow-up on 2026-09-04, after the merge: the `plan-routing` task was the thing at odds with the convention, not the framework. `RULES_DOCS.md` names two correct homes for a plan (standalone `docs/plans/` or the feature folder's `05-plan.md`, the zero-match default for `/sc:plan`), and the task scored the second as a wrong location. The task now accepts either and forbids only a plan at the repo root; the harness's `file_exists_glob` takes a pattern list for this. The convention itself is unchanged. In the same pass, the install walk-up gained a stop at `$HOME` so the unit suite no longer depends on where pytest keeps its temp dir, and a test fixture stopped installing into the developer's real dev-tree `.claude/`.

Second follow-up, same day: the two items left open above are closed. Every `mutation_error` (refusals included) now rolls the worktree back, so partial edits never become the next cycle's baseline. Doing that surfaced a pre-existing data-loss defect: `results.tsv` is untracked in the worktree, `git clean -fd` in rollback deleted it on every regressed or timed-out cycle, and the next append recreated it header-less with the baseline gone; rollback now excludes that file, and a test pins the history surviving a regression. The refusal detector has one implementation in `superclaude.utils`, imported by both package runners; `evals/` keeps its copy, pinned behaviorally by a test.

Third follow-up, same day: the CS-E items were promoted by user decision rather than by their recorded triggers (`3bcb6bc`, details in 05-plan.md section 1). Four content files changed, each loading only on its own context; the always-loaded tier is unchanged. G-h and G-i ship unmeasured because the canary has no research task. Merged to `master` the same day. Nothing is left open from this feature; the chatspeak sweep across the remaining 41 files stays on its opportunistic rule.
