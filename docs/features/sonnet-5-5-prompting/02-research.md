---
status: draft
revised: 2026-09-30
---

# 02 — External research: Claude Sonnet 5.5

Claude Sonnet 5.5 (`claude-sonnet-5-5`) was released on 2026-09-28. It is the second model in the 5.5 family, after Opus 5.5 (2026-09-22). From Claude Code v2.1.284 the `sonnet` alias resolves to it. The account default stays Opus 5.5.

Method: the official pages were downloaded as Markdown (`<page>.md`) and read in full. Claims marked **OFFICIAL** quote them. **INFERRED** marks this document's own reasoning. Community coverage was skimmed and left out: it added nothing the official pages don't say.

Sources:

- [Announcement](https://www.anthropic.com/claude-sonnet-5-5)
- [What's new in Claude Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5)
- [Migration guide](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide)
- [Prompting Claude Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5) (179 lines; line numbers below refer to its `.md` form)
- [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5), the baseline the 5.5 guide builds on
- [Claude Code model configuration](https://code.claude.com/docs/en/model-config)
- [claude.dev: Building with Claude Sonnet 5.5](https://claude.dev/blog/building-with-claude-sonnet-5-5/)
- `claude-api` skill `shared/model-migration.md`, anthropics/skills commit `8a1541c` (2026-09-29): "Update claude-api skill: Claude Opus 5.5 default, Claude Sonnet 5.5, build-eval"

## 1. Specification (OFFICIAL)

| Item | Sonnet 5.5 | Sonnet 5 | Opus 5.5 |
|---|---|---|---|
| Model ID | `claude-sonnet-5-5` (no date suffix; Bedrock `anthropic.claude-sonnet-5-5`) | `claude-sonnet-5` | `claude-opus-5-5` |
| Context / max output | 1M native / 128K (300K on Batches with a beta header) | 1M / 128K | 1M / 128K |
| Price per MTok (in / out / cache read) | $2 / $10 / $0.20 | same | $4 / $20 / $0.20 |
| Default effort, Claude API | `high` | `high` | `medium` |
| Default effort, Claude Code | `medium` | `high` | `medium` |
| Thinking with no `thinking` field | Adaptive, on | Adaptive, on | Always on |
| Lowest thinking setting | `between_tools` (`disabled` → 400) | `disabled` | none (always on) |
| Minimum cacheable prompt | 512 tokens | 1,024 | |
| Knowledge cutoff | June 2026 | | June 2026 |

- Announcement: "runs 30%+ faster, and costs up to 30% less for most work", because it "typically needs far fewer tokens to do the same work" at an unchanged per-token price.
- Positioning: "Where Opus 5.5 is built for complex work requiring careful judgment, Sonnet 5.5 is strongest at well-scoped everyday tasks, fixing bugs, and creating polished documents, slides, and spreadsheets." The prompting guide (line 9): "For the hardest long-horizon work, an Opus model is the better choice."
- It is the first Sonnet to launch with cyber safeguards and fallbacks. Biology safeguards are the same as Sonnet 5's.

## 2. Breaking API changes from Sonnet 5 (OFFICIAL, What's new)

Five changes break code, and one changes the response shape:

1. **`thinking: {"type": "disabled"}` returns 400.** Send `between_tools` instead. It is accepted only at `low`, `medium` and `high` effort (400 at `xhigh`/`max`), it takes no other field, and it blocks per-message effort changes. Only Sonnet 5.5 accepts it, so a router that resends the same body to another model must drop it. The reference's preferred route (model-migration.md, breaking change 1) is "Try adaptive thinking at `low` effort first."
2. **Forced tool use returns 400** (`tool_choice` `any`/`tool`). Use `auto` with `strict: true`, or structured outputs.
3. **Thinking blocks are bound to the model and the conversation.** Sonnet 5.5 reads blocks from Sonnet 5, Opus 4.8, Haiku 4.5 and earlier, "but not from Claude Opus 5, Claude Opus 5.5, or any Claude Fable or Claude Mythos model. No other model reads Claude Sonnet 5.5 thinking blocks." Editing the system prompt, the tools or an earlier message before a block returns 400 on accounts created on or after 2026-08-31.
4. **`computer_20251124` returns 400** on the Claude API and Google Cloud. Use `computer_toolset_20260801`.
5. **The advisor tool rejects Opus 4.8, Opus 4.7 and Sonnet 5 as advisors.**
6. **Response shape:** notes longer than a sentence or two, written between tool calls, arrive as progress-update `thinking` blocks. Their text is empty at the default `display`. Shorter remarks stay `text`.

Also: five refusal categories (`cyber`, `bio`, `frontier_llm`, `reasoning_extraction`, `general_harms`). Server-side fallback retries only `cyber` and `frontier_llm`, on Sonnet 5.

## 3. Prompting deltas (OFFICIAL, Prompting Claude Sonnet 5.5)

The guide opens: "Existing Claude Sonnet 5 prompts should perform well without changes, and the patterns in Prompting Claude Sonnet 5 remain a reasonable starting point." The reference narrows this: its Sonnet 5.5 section replaces "all of [Sonnet 5's] effort advice ... and the prompts to make the model think more or less, because the levels are recalibrated".

Each item below gives what the guide says and, in the right-hand clause, whether it adds to or reverses current practice.

| # | Topic (guide line) | What the guide says | Direction |
|---|---|---|---|
| G1 | Effort (29-39) | Levels are recalibrated. Start at `high` on the API; `medium` for well-specified agentic coding; `medium`/`low` for chat. "Asking it in the system prompt to think less doesn't reliably reduce its thinking." From `medium` up it thinks before almost every reply, even a greeting. For agentic coding, `max_tokens` 128,000 | Lower effort, don't prompt for less thinking |
| G2 | Carrying work through (45-53) | At `low`/`medium` on agentic coding it "sometimes checks in before the work is done". Two-paragraph fix: keep working until done, stop only when blocked or before a risky step; then "Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it." | **New** failure mode (early check-in) |
| G3 | Unrequested additions (55) | Adds tests, docs and small supporting files "at every effort level, and more at higher effort". Use only the second paragraph of G2 to limit it | Scope creep in files, not in the requested change |
| G4 | Thoroughness at `xhigh`/`max` (57-63) | Starts its own review rounds, sometimes with reviewer subagents. A stop-and-report paragraph "cut session cost by about a third, with no change in quality" | Cap self-started review |
| G5 | Open-ended requests (65-69) | Can start building when only ideas were wanted. One-line fix: give ideas, options or a plan, then stop | New |
| G6 | Running without up-front thinking (71-78) | `between_tools` ≤ `high`. "Remove any instruction that tells the model not to think": such rules raise internal-XML-tag leakage | Same as Opus 5 |
| G7 | Reasoning tasks with JSON output (80-103) | At `low`/`medium` it often answers without thinking. With adaptive thinking, add "Think the problem through before you answer." at the end of the system prompt. At `high` this brings accuracy close to `xhigh`. Without structured outputs, parse the last JSON value, not first-`{` to last-`}` | **Reverses** the generic "delete thinking incantations" rule for this task class |
| G8 | Progress updates (105-119) | Set `display: "updates"`; remove "hold all findings for the final response"; the harness may add a reminder after about five silent steps, at most two or three times | Same as Opus 5.5 |
| G9 | Tool use in chat and knowledge work (121-131) | "Sometimes answers from its training knowledge when a web search would catch details that have changed." Remove "only use tools when strictly necessary" and "minimize tool calls" (the reference: "it follows these literally"). Add a search-first line | **New**: tool under-use |
| G10 | Mid-turn user messages (133-142) | Trained against indirect prompt injection. It can read a genuine user message placed right after a tool result, or inside a `tool_result`, as an injection. Per-step harness text (a token countdown, per-step instructions) causes this | **New**: harness placement matters |
| G11 | Verification on coding tasks (144-152) | "At `low` effort ... it sometimes reports a change as done without running a check that exercises it." The verification paragraph: run a real check; a syntax-only check does not count; install declared dependencies with the project's own package manager; otherwise say which check did not run | **Reverses** the Opus 5 "delete verification instructions" direction |
| G12 | Tolerant tool calls (154-159) | Occasionally calls a tool by a name that differs only in letter case. Accept the call, or return `is_error` with the exact name | Harness-side |
| G13 | Complex visual inputs (161-163) | Crop, zoom or code tools beat raising effort on charts | Harness-side |
| G14 | Refusals (165-179) | Five categories. "If your prompts ask the model to include its reasoning in the response, remove those instructions, because they invite `reasoning_extraction` declines." | Same as Opus 5.5 |

The reference (model-migration.md L2195-2225) adds two items the guide does not have:

- **Remove workarounds for what got better:** refusal steering, tool-call retry shims, and "instructions like 'do not be lazy'".
- **Settled answers in multi-turn chat:** an optional line that tells the model to treat its earlier answers as done.

## 4. Claude Code facts (OFFICIAL, model-config, v2.1.284)

- "From Claude Code v2.1.284 ... the `sonnet` alias resolves to Sonnet 5.5 on the Claude API. It runs at `medium` effort by default, with the 1M context window native." The `default` model stays Opus 5.5 (claude.dev blog).
- "You can't turn thinking off on Opus 5.5, Sonnet 5.5, or the Fable models." `alwaysThinkingEnabled: false` and `MAX_THINKING_TOKENS=0` have no effect on them.
- Effort guidance (model-config table): `medium` is "the default on Opus 5.5 and Sonnet 5.5, where it fits day-to-day engineering work with a clear scope"; `high` fits "work where verification matters or edge cases are likely, such as fixing a bug in an existing codebase".
- Content fallback: "Sonnet 5.5: cybersecurity-flagged requests re-run on Sonnet 5. Biology-flagged requests end with a refusal instead, because Sonnet 5.5 has no biology fallback model." Fallback from Sonnet 5.5 also needs an Opus target that resolves in the deployment.
- Sonnet 5.5 has no fast mode.

## 5. Upstream fact source now covers both 5.5 models

The `claude-api` skill's `shared/model-migration.md` is the fact source that `/sc:prompt` and `context_loader.py` read (opus-5-5-default-model 03-analysis §4). At commit `8a1541c` (2026-09-29) it gained both sections that were missing:

| Heading | Line | Behavioral-shifts range the loader would emit |
|---|---|---|
| `## Migrating to Claude Opus 5.5` | 1867 | L2044-2071 |
| `## Migrating to Claude Sonnet 5.5` | 2072 | L2195-2225 |

The ranges were computed by running `migration_reference_ranges()` on the downloaded file with the two anchors added in memory. The shipped anchor list returns only `claude-opus-5` and `claude-fable-5-1`. That removes the gate on P4 of [../opus-5-5-default-model/04-design.md](../opus-5-5-default-model/04-design.md) ("P4 still waits for the `claude-api` skill to publish an Opus 5.5 migration section").

The new Opus 5.5 section also weakens a carried assumption. Its first behavioral shift reads: "Instructions tuned for Claude Opus 5's behavior (the verbosity, over-verification, and scope prompts ...) may no longer be needed - keep them as the starting point, then re-test each." The `/sc:prompt` Opus column carries Opus 5 facts to Opus 5.5 "unless marked". Under that rule this is a re-test flag, not a reversal.

## 6. Assessment (INFERRED)

- **Two families now pull in opposite directions on verification.** The Opus column says "delete verification instructions: it self-verifies". Sonnet 5.5 at `low` needs one added (G11). An unresolved target on a Sonnet session produces the wrong edit. The `model-required` gotcha in `/sc:prompt` exists for exactly this case.
- **One generic removal rule is wrong for Sonnet 5.5.** "Thinking incantations: delete" contradicts G7, which recommends one specific think-first line for JSON reasoning tasks under adaptive thinking.
- **Several deltas land on harness behavior SuperClaude already has:** per-edit hook messages (G10), a verification kernel (G11), a scope kernel (G2/G3) and a research workflow (G9). [03-analysis.md](./03-analysis.md) checks each against the source, and [03a-analysis-probes.md](./03a-analysis-probes.md) measures the ones that could be run headless.
- **Model choice stays the user's.** Sonnet 5.5 is half Opus 5.5's list price on input and output. At a cache read of $0.20 it costs the same as Opus 5.5 on the tokens that dominate agentic cost. The official routing puts well-scoped work on Sonnet and judgment-heavy, long-horizon work on Opus. The framework has no signal for which kind a task is, so, like the Fable decision, the switch is the user's.
