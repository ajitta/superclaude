---
feature: fable-5-1-alignment
phase: implementing
owner: ajitta
created: 2026-09-03
updated: 2026-09-03
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

Plan approved 2026-09-03 and being applied on `feature/fable-5-1-alignment` (branched from `master`; no `integration` branch exists). Harness facts checked against the Claude Code docs the same day (a `PreCompact` hook cannot inject compaction instructions; a `fable` alias selects Fable 5.1; refusal JSON fields and effort exposure are undocumented). Open questions in [05-plan.md section 4](./05-plan.md#4-open-questions) were resolved by their stated defaults; the canary spend on `claude-fable-5-1` remains the user's call and gates CS-D.

| Change set | Status |
|---|---|
| CS-A sediment (`prompt.md`, listings, one comment) | applied, `6dda706` |
| CS-B delegation run-alongside + compaction SSOT | applied, `d24bc69` |
| CS-C refusal classification in headless runners | applied after adversarial review (one high-severity fix folded in); commit hash in `git log` on the branch |
| CS-D long-output sentence in `RULES_DOCS.md` (measurement-gated); compaction hook dropped after the fact check | waiting on canary spend approval |
| CS-E deferred items with promotion triggers | recorded; G-j found already covered by `git_diff_max_files` |
