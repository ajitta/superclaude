---
status: complete
revised: 2026-09-23
---

# 02 — External research: Claude Opus 5.5

Opus 5.5 (`claude-opus-5-5`) was released on 2026-09-22 and is already Claude Code's default on every first-party plan. Against Opus 5 it is cheaper, faster and defaults to `medium` effort. Anthropic's routing advice matches the goal of this feature: start on Opus 5.5 and move to Fable 5.1 only when evals at `xhigh`/`max` still fall short.

Method: a delegated web-research pass (official docs, announcement, system card, Claude Code docs and changelog, press, Hacker News, blogs, YouTube). The main loop then re-checked each claim marked OFFICIAL below against the downloaded page text. Tags: **OFFICIAL** = Anthropic docs, announcement or system card; **COMMUNITY** = press, blogs, forums, video; **INFERRED** = this document's reasoning.

## 1. Specification (OFFICIAL)

Sources: [Opus 5.5 overview](https://platform.claude.com/docs/en/models/opus-5-5/overview), [What's new](https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5), [migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide), [announcement](https://www.anthropic.com/claude-opus-5-5).

| Item | Opus 5.5 | Opus 5 | Fable 5.1 |
|---|---|---|---|
| Model ID | `claude-opus-5-5` (no date suffix) | `claude-opus-5` | `claude-fable-5-1` |
| Context / max output | 1M native / 128K | | 1M / 128K |
| Price per MTok (in / out) | $4 / $20 | $5 / $25 | $10 / $50 |
| Default effort | `medium` | `high` | `high` |
| Latency (overview table) | "Moderate" | | "Slower" |
| Fast mode price | $8 / $40 | $10 / $50 | |

- Anthropic: "at default settings it will cost 40% less than Opus 5 on typical workloads" and it generates output "more than 30% faster".
- Prompting guide (lines 38-43): "Claude Opus 5.5 at `medium` matches or exceeds Claude Opus 5 at `high`" and "Reserve `xhigh` and `max` for work where you've measured a quality gain." The effort guide says of `max`: "Reserve for frontier problems."
- Thinking: "Adaptive thinking is always on and can't be turned off." Requests with `thinking: {type: "disabled"}` or `budget_tokens` return 400.
- Other breaking API changes: `tool_choice` `any`/`tool` returns 400 (use `auto` plus strict tools); thinking blocks are bound to the model and conversation; `computer_20251124` is rejected on the Claude API and Google Cloud.

## 2. Behavior against Opus 5 (OFFICIAL, prompting guide)

Source: [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5).

- "Existing Claude Opus 5 prompts should perform well without changes, and the patterns in Prompting Claude Opus 5 remain a reasonable starting point." Opus 5 guidance is therefore a valid base, and the 5.5 deltas are additions to it.
- **Remove "think carefully" lines** in chat system prompts: "consider removing them for Claude Opus 5.5", because the model decides how much to think.
- **Remove instructions to write reasoning into the response.** A new refusal category covers them: "Requests that push the model to reproduce its internal reasoning in the response text can be declined with the `reasoning_extraction` category." Server-side fallback does not retry these declines.
- **Unattended runs stop early.** "Some of those updates end the turn with text rather than a tool call." The guide supplies a paragraph for fully unattended harnesses only, not human-in-the-loop ones.
- **It acts before looking** on multi-app work. The guide gives an "explore broadly with tool calls" line.
- **It uses elapsed-time signals.** In lead-plus-subagent setups a time budget speeds up the work through more parallel calls.
- **Refusal categories:** biology safeguards are the same as Fable 5.1's and are new relative to Opus 5; cyber stays; `reasoning_extraction` is new.
- **Safety** (system card p.94): its rate of "overeager or destructive actions is the lowest among our recent models."
- **Writing** (announcement): it "puts the most important information up front, is less likely to use jargon or idiosyncratic phrases, and follows the writing rules you give it."

Not found in any official Opus 5.5 source: guidance on capital-letter emphasis, literal instruction following, or how often the model spawns subagents. The 5.5 guide defers to the Opus 5 guide on those axes. The "delegates to subagents far more effectively" and "40% less verbose" lines on the announcement page are customer quotes, not Anthropic measurements.

## 3. Opus 5.5 vs Fable 5.1 (OFFICIAL)

Source: [Choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model), [Claude Code model config](https://code.claude.com/docs/en/model-config).

- "Most workloads start with Claude Opus 5.5." Step 5 of the routing list: "If your evals at `xhigh` or `max` effort still fall short on demanding reasoning or long-horizon agentic work, move to Claude Fable 5.1."
- Fable's listed best uses: agent sessions that run for hours, multistep deep research, analysis carried through to a finished document, spreadsheet or deck. Opus 5.5's: multihour autonomous coding, large refactors, complex systems engineering, vision-heavy work, computer use.
- The announcement says "the gap between Opus 5.5 and Claude Fable 5.1 is narrower than these scores suggest" and cites a C-to-Rust HAProxy port: Opus 5.5 took 9.5 h against Fable's 12 h, at 51% less cost.
- Claude Code: Fable suits "tasks larger than a single sitting", and "Neither Fable model is the account-type default on any plan or provider. Select one explicitly" (`/model fable` or `claude --model fable`). On some plans Fable bills to usage credits behind a consent prompt; in `-p` mode and the Agent SDK Claude Code bills it without asking, and Enterprise members with organization billing never see the prompt either. Persistence differs by path: `claude --model fable` applies "only to the session you launch with" it, while "Choosing one with `/model` saves it as the selected model in your user settings, so later sessions start on it."

INFERRED: the official criterion for moving to Fable is evidence-based (measured shortfall at high effort), and Fable costs 2.5× Opus 5.5 at list input/output price (cache reads $0.25 against $0.20, 1.25×; the announcement says cache reads "make up the majority of agentic and coding work costs"). So the move to Fable should be a user decision, never an automatic escalation by the framework.

## 4. Claude Code facts (OFFICIAL, v2.1.280)

Sources: [model-config](https://code.claude.com/docs/en/model-config), [sub-agents](https://code.claude.com/docs/en/sub-agents), [changelog](https://code.claude.com/docs/en/changelog).

- **Default model:** "Pro, Max, Team, Enterprise, and Anthropic API: defaults to Opus 5.5", and the same on Claude Platform on AWS, Bedrock and Google Cloud's Agent Platform. Microsoft Foundry defaults to Sonnet 4.5. Opus 5.5 requires v2.1.280+; before it, `default` resolved to Sonnet 5 on Pro and Team Standard and to Opus 5 elsewhere, so a user on an older Claude Code does not get Opus 5.5 by default. The 2.1.280 changelog also moved Pro and Team Standard defaults from Sonnet to Opus.
- **Aliases:** `default`, `opus`, `opus[1m]`, `sonnet`, `sonnet[1m]`, `haiku`, `fable` (Fable 5.1; Fable 5 in Claude apps gateway sessions), `best` (Fable where available, else Opus), `opusplan` (Opus in plan mode, Sonnet for execution). "Aliases point to the recommended version for your provider and update over time."
- **Subagent model resolution**, in order: "1. The per-invocation `model` parameter", 2. frontmatter `model:`, "3. The `CLAUDE_CODE_SUBAGENT_MODEL` environment variable", 4. the main conversation's model. "Before v2.1.251, `CLAUDE_CODE_SUBAGENT_MODEL` came first in this order."
- **Effort resolution:** explicit choice (`CLAUDE_CODE_EFFORT_LEVEL`, `--effort`, `/effort`), then settings, then the model default. "a top-level `effortLevel` in your user settings file doesn't count for Opus 5.5": Opus 5.5 starts at `medium` until a level is chosen for it with `/effort` or the `/model` picker. A top-level `effortLevel` in project, local or managed settings still applies to every model.
- **Thinking:** "You can't turn thinking off on Opus 5.5 or the Fable models."
- **Content fallback:** Fable models, Opus 5.5 and Opus 5 run safety classifiers; flagged requests re-run on a fallback model per category.

## 5. Community evaluation (COMMUNITY)

Nine sources, all from 2026-09-22 and 2026-09-23.

- **Effort sweet spot is `medium`/default.** On [HN](https://news.ycombinator.com/item?id=49804316), commenter zerof1l wrote that "Medium thinking effort is ideal for most tasks". [Simon Willison](https://simonwillison.net/2026/Sep/22/opus-and-sol-and-luna/) found `max` "effectively useless" on a simple prompt, at about $2.56 and 20 minutes per failed attempt. [Latent Space](https://www.latent.space/p/ainews-claude-opus-55-the-new-default) relays that `xhigh` costs about 2.8× `medium` for a lower FrontierCode score, and that "At max effort, the per-task saving over Opus 5 disappears."
- **Token burn at high effort.** [The Decoder](https://the-decoder.com/claude-opus-5-5-matches-fable-5-1-at-40-percent-lower-cost-as-anthropic-promises-to-fix-claudish-writing/) reports about 119K output tokens per task at `max`, against 73K for Opus 5 and 78K for Fable 5.1. [CodeRabbit](https://www.coderabbit.ai/blog/opus-5-5-model-review) caught more bugs (51 vs 49; 10 vs 5 on hard cases) with about 50% more tokens.
- **Capability relative to Fable.** [Every](https://every.to/vibe-check/vibe-check-opus-5-5-is-pulling-our-codex-converts-back-to-claude) puts Opus 5.5 at "about 90 percent as capable as Fable at coding" and keeps Fable for the largest problems, deadline-critical deliverables and professional prose editing. It also reports writing that "often buries the point" and one unconstrained run of 1 h 52 min. [Artificial Analysis](https://artificialanalysis.ai/models/releases/claude-opus-5-5) scores Opus 5.5 at 51 (`medium`) to 58 (`max`) against Fable 5.1's best of 53.
- **YouTube:** three launch videos (CodeRabbit review, "I Tested Opus 5.5 So You Don't Have To", "Stronger Coding Than Opus 5 for Less"). Only titles and descriptions could be read; no transcript was retrieved, so video content carries no weight here.
- **Reddit:** not indexed for these dates by the search tools used.

## 6. Assessment for this project (INFERRED from §1–§5)

- **Opus 5.5 as the default is well supported.** Anthropic's routing advice, the Claude Code default, the price cut (−20% per token, about −40% per typical task at default effort) and community reports all point the same way. For SuperClaude's main workloads (repository coding, review, refactoring, docs) Opus 5.5 is also the model Anthropic lists as best fit.
- **Its weak spots are known and prompt-tunable:** overthinking and token burn at `xhigh`/`max`, early turn ends in unattended runs, acting before exploring on multi-app work, and writing that can still bury the point without explicit rules. None of these calls for a model switch; they call for staying at default effort and for the prompting-guide lines in §2.
- **Fable 5.1 keeps a narrow, real niche:** multi-hour autonomous sessions, deep research carried to a finished document, and work that still falls short at `xhigh`/`max`. The opt-in must stay with the user because of the 2.5× list price and the headless billing behavior.
- **Evidence strength:** specification, pricing, defaults and routing advice are official and re-checked. Behavioral claims beyond the prompting guide rest on launch-week community reports (1–2 days old), and the YouTube evidence is titles only.

## 7. Conflicts and unknowns

- The Fable 5.1 overview page still says "For most workloads, start with Claude Opus 5". The choosing-a-model page says Opus 5.5 and is newer; this document follows it.
- Press claims that Opus 5.5 "beats Fable on every benchmark" overstate Anthropic's own "narrower than these scores suggest".
- The "40% cheaper" figure holds at default effort only.
- Whether switching `/effort` mid-session invalidates the prompt cache is unresolved: the docs mention a cache warning, and a staff post relayed by Latent Space says it no longer does in v2.1.280+.
- Unknown: Sonnet 5.5 / Haiku 5.5 dates (press: "in the coming weeks"); YouTube transcripts; Reddit threads; an Anthropic statement on subagent-spawn frequency.
- The `claude-api` skill's `model-migration.md`, the file `/sc:prompt` treats as its fact source, has no Opus 5.5 section as of 2026-09-23 (see [03-analysis.md §4](./03-analysis.md)).
