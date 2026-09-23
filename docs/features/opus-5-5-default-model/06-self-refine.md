---
status: complete
revised: 2026-09-23
---

# 06 — Self-refine pass over 02–04

One self-refine pass over [02-research.md](./02-research.md), [03-analysis.md](./03-analysis.md) and [04-design.md](./04-design.md), in the order: factual errors, logical leaps, missing requirements, repetition. Only defects confirmed against a source were changed. Each check re-read the downloaded page text or the repository; no subagent was used for the check.

## ① Confirmed errors, fixed

- **04 P1 price ratio.** The draft said Fable costs "2× input and 2.5× output". The prices are $10/$50 against $4/$20, which is 2.5× on both, and the text now says so.
- **04 P2 billing claim was too broad.** The draft said headless runs bill Fable "without a consent prompt" unconditionally. model-config says the prompt guards usage-credit billing, and that "In non-interactive mode with the `-p` flag and through the Agent SDK, Claude Code never shows the consent prompt. When a Fable request there would bill to usage credits, Claude Code bills it without asking." The text is now scoped to plans that bill Fable to usage credits.
- **04 P3 source attribution.** The draft credited the 128,000 `max_tokens` figure to the overview, effort and migration guides. It comes from the prompting guide ("a `max_tokens` of 128,000, the model's maximum, has worked well in Anthropic's testing"), and each fact now names its own source.
- **02 §2 quote.** The draft bracketed "[remain]" into the prompting-guide sentence. The source already reads "remain a reasonable starting point", so the brackets were removed.
- **02 §4 Foundry default.** Marked "not re-checked" in the draft. model-config lists "Microsoft Foundry: defaults to Sonnet 4.5" and gives the pre-2.1.280 defaults, now stated.

## ② Logical leaps, fixed

- **04 P2** argued that the main loop "cannot observe" a Fable-worthy shortfall mid-delegation. It can observe a failed delegation. The actual reason is that the official criterion is the user's own evaluation at `xhigh`/`max`, and the text now says that.

## ③ Missing requirement, added

- The request asked to research **and evaluate** Opus 5.5. 02 reported the evidence but gave no verdict. A new §6 "Assessment for this project" states the verdict: default well supported, weak spots prompt-tunable, Fable niche narrow but real. It also states how strong the evidence is.
- The folder had no `README.md`, which the doc convention requires; added.

## ④ Preserved after checking

- 03 §1 alias table: every row is a saved probe result (`probe_opus.json`, `probe_fable.json`, and the default and `[1m]` runs).
- 03 S6: `agents/README.md:90` and `:92` re-read; the sub-agents doc confirms the current order and "Before v2.1.251, `CLAUDE_CODE_SUBAGENT_MODEL` came first in this order."
- 03 S9 and 04 P5: model-config lists "Fable models, Opus 5.5, and Opus 5" as classifier-bearing. The evals pin (`tests/unit/test_eval_harness.py:524-542`) compares return values, so the P5 docstring edit is safe; its verify step now says so.
- 02 routing quotes ("Most workloads start with Claude Opus 5.5", the step-5 Fable criterion), the effort-resolution quote, and "Neither Fable model is the account-type default" were each matched against the downloaded page.
- The rejected-ideas table in 04 §3 stays as written; each row's reason is backed by a measurement or a quoted doc line.

## ⑤ Remaining uncertainty

- Community figures (Artificial Analysis index, The Decoder token counts, CodeRabbit bug counts, Every's 90% estimate) were not re-checked by the main loop. They are tagged COMMUNITY and no proposal depends on them.
- YouTube evidence is titles only; no transcript was retrieved.
- The probes in 03 §3 and §3b are one run each.
- Sonnet 5 pricing was not collected, so D1 (the auto-improve mutator default) stays a decision rather than a recommendation.
