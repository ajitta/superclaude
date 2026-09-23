---
feature: opus-5-5-default-model
phase: implementing
owner: chosh1179
created: 2026-09-23
updated: 2026-09-23
---

# Opus 5.5 as the default model, Fable 5.1 on demand

Claude Opus 5.5 shipped on 2026-09-22. The goal of this feature: a user who installs SuperClaude runs on Opus 5.5 by default and uses Fable 5.1 only when a task needs it. This folder holds the external research on Opus 5.5, the audit of `src/superclaude` against that goal, the resulting proposals, and the record of implementing them.

## Summary

- **Claude Code already delivers the default.** From v2.1.280, `default` resolves to Opus 5.5 on Pro, Max, Team, Enterprise, the Anthropic API, Bedrock, Google Cloud and Claude Platform on AWS. Measured on this machine: `claude-opus-5-5[1m]`. SuperClaude writes no model setting and should keep it that way: a written key would override each user's and team's choice and add nothing, since `opus` and the default both run with the 1M window.
- **The framework is out of date in three places:** `/sc:prompt` has no Opus 5.5 target; `agents/README.md` states a subagent resolution order from before v2.1.251; and nothing says that only the user moves a delegation to Fable.
- **Fable 5.1's niche is narrow.** Anthropic: "Most workloads start with Claude Opus 5.5"; move to Fable when evals at `xhigh`/`max` still fall short. Fable costs 2.5× at list input/output price (1.25× on cache reads). The one-session path is `claude --model fable`; `/model fable` is saved and carries into later sessions.

P1, P2, P3, P5 and P7 are implemented on branch `fix/opus-5-5-default-model`, with D3 applied and D1/P6 left out on 04-design's recommendations ([08-implementation.md](./08-implementation.md)). P4 still waits for the `claude-api` skill to publish an Opus 5.5 migration section. Two design reviews and one three-reviewer implementation review are applied ([07-review.md](./07-review.md)). The implementation departs from 04-design in a few places, each amended there or listed in 08 with its source; the largest is that `/sc:prompt` deletes a no-thinking rule for Opus 5 too, as the migration reference says.

## Documents

- [02-research.md](./02-research.md): official specs, behavior against Opus 5, Opus 5.5 vs Fable 5.1, Claude Code facts, community evaluation, assessment
- [03-analysis.md](./03-analysis.md): measured alias and default resolution, the S1–S13 inventory of model-dependent surfaces in `src/superclaude`, and the `/sc:prompt` and `reasoning_extraction` probes
- [04-design.md](./04-design.md): proposals P1–P7, user decisions, rejected ideas, deferred items
- [06-self-refine.md](./06-self-refine.md): the self-refine pass over 02–04, listing what was corrected and what was kept
- [07-review.md](./07-review.md): three independent `/sc:review` rounds (folder, design, implementation) and how each finding was resolved
- [08-implementation.md](./08-implementation.md): what shipped, departures from 04-design with their sources, canary and two-path probe results, and what was observed but not acted on
