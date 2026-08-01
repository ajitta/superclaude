---
status: draft
revised: 2026-08-02
---

# Context & Prompt Engineering Guidelines for Claude Opus 5 / Fable 5

Research basis for realigning SuperClaude's content framework to the Claude 5 model family.

## Sources

All fetched 2026-08-02. Anthropic first-party only — no secondary commentary was used as evidence.

| Source | URL |
|---|---|
| Prompting Claude Opus 5 | `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5` |
| Prompting Claude Fable 5 | `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5` |
| Prompting best practices (all current models) | `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices` |
| Effective context engineering for AI agents | `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents` |
| Model migration guide | `https://platform.claude.com/docs/en/about-claude/models/migration-guide` |

## Why this matters for a content framework

SuperClaude is not application code — it is a permanently-resident instruction surface. `CLAUDE_SC.md` imports `FLAGS.md`, `PRINCIPLES.md`, and `RULES.md` into every session, and `context_loader.py` injects further modules on trigger. Every sentence in that surface competes for the same attention budget as the user's actual task.

That makes two Anthropic findings directly load-bearing here, in a way they are not for ordinary prompts:

Anthropic frames context as **"a finite resource with diminishing marginal returns"**, caused by *context rot* — as tokens accumulate, recall and long-range reasoning precision degrade. The stated goal is **"the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."** An always-loaded framework pays that cost on every turn, before the task starts.

And for Fable 5 specifically: **"Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality. Review and consider removing older instructions if default performance is better."** A framework whose value proposition is prescription now has a burden of proof it did not have on Opus 4.x.

The through-line of this research: **capability increases convert instructions into liabilities.** An instruction that compensated for a weakness the model no longer has does not become neutral — it becomes an active distortion, because the model follows it.

## Part 1 — Behavioral deltas that invalidate prior-model scaffolding

### 1.1 Self-verification became native (Opus 5)

> "Claude Opus 5 verifies its own work without being told to. If your prompt contains explicit verification instructions ('include a final verification step for any non-trivial task,' 'use a subagent to verify'), remove them: instructions like these cause over-verification on Claude Opus 5, and removing them reduces wasted tokens with no loss in quality. The same applies to legacy harness scaffolding that adds separate verification steps."

And on self-correction:

> "Avoid instructing re-checks it already performs ('double-check your answer,' 're-verify before responding'); like verification instructions, these compound with the model's own behavior and add cost without improving results."

**The distinction that must not be collapsed.** This is the highest-risk misreading in the whole realignment, so state it precisely:

- **Remove:** instructions telling the model to *perform additional verification work* — extra passes, verification steps, verifier subagents, "double-check before answering."
- **Keep:** instructions constraining *what the model may claim* — cite real output, never assert a pass without evidence.

The second category is not merely permitted, it is explicitly recommended for Fable 5:

> "Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging."

Anthropic reports this "nearly eliminated fabricated status reports even on tasks designed to elicit them."

So the correct posture is: **anti-fabrication yes, extra-verification no.** Rules that say "prove it before you claim it" survive. Rules that say "verify again, then verify that" go.

### 1.2 Subagent delegation reversed direction

Opus 4.8 *under*-delegated and needed encouragement. Opus 5 does the opposite:

> "Claude Opus 5 delegates to subagents more readily than prior models. Delegation pays off on genuinely independent, sizeable tracks of work, but it multiplies cost and time when applied to small tasks."

Anthropic's damping language is specific, and one clause matters more than the rest:

> "Delegate to a subagent only for large tasks that are genuinely independent and parallelizable, such as a wide multi-file investigation. Do not delegate work you can finish yourself in a handful of tool calls, **and do not use subagents to verify or double-check your own work.** If one subagent can complete the task, use one rather than several, and keep spawn counts low."

That clause is the intersection of 1.1 and 1.2: a verifier subagent is now doubly wrong — it is both redundant verification and unnecessary delegation.

Fable 5 diverges here in a way that matters for orchestration design. It is not damped; it is *re-shaped*:

> "Claude Fable 5 dispatches parallel subagents more readily than prior models. Use subagents frequently, provide explicit guidance about when delegation is appropriate, and prefer asynchronous communication between orchestrator and subagents over blocking until each subagent returns. Long-lived subagents that keep their context across subtasks save time and cost through cache reads and avoid bottlenecking on the slowest subagent."

So delegation guidance must become **model-conditional**: cap and damp for Opus 5; for Fable 5, keep delegation but shift the pattern from blocking fan-out to long-lived asynchronous workers.

Note the one place Anthropic still endorses verifier subagents — Fable 5, long-running builds only: *"Separate, fresh-context verifier subagents tend to outperform self-critique."* This is scoped to multi-hour autonomous runs, not to ordinary tasks, and does not reopen 1.1.

### 1.3 Verbosity rose, and `effort` does not control it

> "Claude Opus 5's default user-facing responses run longer than prior Opus models'. The effort parameter controls how much the model thinks rather than how much it says: lowering effort can reduce thinking volume without reliably shortening the visible response. To control response length, prompt for it explicitly."

Three separate surfaces need separate instructions, and conflating them is a common failure:

1. **Conversational response length** — needs an explicit conciseness instruction.
2. **Inter-tool-call narration** — Opus 5 "narrates readily"; needs a cadence instruction.
3. **Written deliverables on disk** — "files that Claude Opus 5 writes to disk (reports, Markdown documents, summaries) are often longer than on prior models"; needs its own length calibration.

Lowering `effort` addresses none of them.

### 1.4 Compression is the wrong lever for brevity

This is the finding most likely to contradict an existing token-efficiency design. Anthropic, on Fable 5:

> "Being readable and being concise are different things, and readability matters more.
>
> The way to keep output short is to be selective about what you include (drop details that don't change what the reader would do next), **not to compress the writing into fragments, abbreviations, arrow chains like A → B → fails, or jargon.**"

And on the end-of-run summary specifically:

> "When you write the summary at the end, drop the working shorthand. Write complete sentences. Spell out terms. Don't use arrow chains, hyphen-stacked compounds, or labels you made up earlier. ... If you have to choose between short and clear, choose clear."

Two independent reasons this is not merely stylistic:

**Anthropic names the exact constructs.** Arrow chains and abbreviations are not inferred from a general principle — they appear verbatim in the guidance as things not to do. This is the primary evidence and it stands on its own.

**The token saving is likely near zero anyway.** BPE tokenizers split invented abbreviations (`cfg`, `impl`, `req`) into subword pieces, while the full word is typically a single frequent token; `→` is its own token where `to` is also one. *This mechanism is not measured in this repository* — Claude's tokenizer is not available offline and `count_tokens` requires API credentials that were not present in this session. Treat it as a hypothesis to test with `client.messages.count_tokens` against `claude-opus-5` before citing a number. Two independent corroborations point the same way: this repo's own harness-engineering research already lists "Token efficiency symbols → context windows growing, models compress better" among practices to retire (`docs/research/2026-03-28-harness-engineering-comprehensive-research-ajitta.md:374,595`), and the bundled caveman plugin states the same tokenizer argument as its rationale for banning invented abbreviations and causal arrows.

The decision does not depend on the measurement: even if compression saved tokens, Anthropic's guidance names it as the wrong lever, and the readability cost is asserted by the model vendor.

The legitimate compression lever is *selection*: drop content whose absence does not change what the reader does next. That is the same test as the deletion test already in `content-quality.md`.

### 1.5 Surfacing the context budget causes context anxiety (Fable 5)

> "In very long sessions, Claude Fable 5 can occasionally suggest a new session, offer to summarize and hand off, or trim its own work. This is most often triggered when the harness shows a remaining-token countdown to the model. Avoid surfacing explicit context-budget counts where possible."

If a countdown must be shown, Anthropic's mitigation is reassurance:

> "You have ample context remaining. Do not stop, summarize, or suggest a new session on account of context limits. Continue the work."

The cross-model guidance is consistent — where the harness compacts, *say so*, so the model does not wrap up early:

> "Your context window will be automatically compacted as it approaches its limit, allowing you to continue working indefinitely from where you left off. Therefore, do not stop tasks early due to token budget concerns."

Note the tension with 1.4's genuine use case. Percentage-triggered token-efficiency behavior is defensible as a *transport* guard against context-window overflow. What is not defensible is instructing the model to monitor and reason about its own remaining budget — that is the documented trigger.

### 1.6 "Show your reasoning" is now a refusal risk (Fable 5)

The single hardest constraint found, because it fails closed rather than degrading:

> "Don't instruct Claude to reproduce its reasoning in the response. Prompts, skills, or harness instructions that tell the model to echo, transcribe, or explain its internal reasoning as response text can trigger the `reasoning_extraction` refusal category on Claude Fable 5, causing elevated fallbacks to Claude Opus 4.8. **Audit existing skills and system prompts for reflection or show-your-thinking instructions when migrating.** If your application needs reasoning visibility, read the structured `thinking` blocks from adaptive thinking instead."

A `reasoning_extraction` refusal returns HTTP 200 with `stop_reason: "refusal"` — not an error. Without a configured fallback the request simply stops.

The boundary is between **transcription** and **analysis**. "Explain your internal reasoning as response text" is in scope. "State the assumption you are making and the evidence for it" is not — that is a claim about the world, reconstructed for the reader, and it is what B5-style grounding asks for. Introspection features should be worded on the analysis side of that line and should never ask for verbatim thinking.

### 1.7 Aggressive language now overtriggers

> "If your prompts were designed to reduce undertriggering on tools or skills, these models may now overtrigger. The fix is to dial back any aggressive language. Where you might have said 'CRITICAL: You MUST use this tool when...', you can use more normal prompting like 'Use this tool when...'."

Named anti-patterns: blanket `Default to using [tool]`, and `If in doubt, use [tool]` — the latter to be deleted outright, not softened.

This is in tension with a real prior finding: recent Opus models read hedging (`should`, `might`, `consider`) as optional. Both are true, and they resolve cleanly because they act on different axes:

- **Mood** — declarative/imperative, not hedged. `never` beats `should not`. **Keep.**
- **Volume** — no `CRITICAL:`, no all-caps `MUST`, no "if in doubt." **Remove.**

Write `Use X when Y`, not `CRITICAL: You MUST always use X`. The first is declarative and calm; the second is declarative and shouted. Only the shouting overtriggers.

### 1.8 Scope expansion (Opus 5) and unrequested action (Fable 5)

Opus 5 "can also expand the scope of a task, adding steps that weren't requested or applying its own judgment about what the task should be." Anthropic's scope instruction adds a clause that pure scope-limiting language misses — **"Finish the whole task"** — because scope discipline alone can be over-applied into premature "done" claims on partial work.

Fable 5's failure mode is adjacent but distinct — unrequested *actions* rather than unrequested scope (drafting an email, creating defensive git branches). Its mitigation is a deliverable-type rule:

> "When the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one."

### 1.9 Effort is now the primary cost lever, and defaults do not port

Opus 5: default is `high`; "use `low` and `medium` liberally as your primary control for token cost and response time wherever quality holds, and step up to `xhigh` for demanding coding and agentic work. If you carried effort defaults over from a prior model, re-run an effort sweep on your own evals."

Fable 5: `high` default, `xhigh` for capability-sensitive work, `medium`/`low` for routine — and "lower effort settings on Claude Fable 5 still perform well and often exceed `xhigh` performance on prior models."

The reflex of reaching for `xhigh` by default is a prior-model habit and is now usually wrong.

### 1.10 Thinking-disabled is a trap on Opus 5

Thinking is on by default and can be disabled only at effort `high` or below. With it disabled, two artifacts appear: tool calls written into visible text (the call never runs, no error is raised, and the leaked text pollutes later turns in an agentic loop), and internal XML tag leakage.

> "If your system prompt contains a rule instructing the model not to think or not to reason, remove it; that kind of instruction increases tag leakage."

Also counterintuitive: naming thinking tags specifically is *less* effective than a generic "do not include internal or system XML tags."

Primary mitigation is not to disable thinking — "for most tasks, thinking enabled at `low` effort performs better than thinking disabled at similar cost."

## Part 2 — The guideline

Rules for authoring always-loaded or on-demand agent content for the Claude 5 family. Each carries its evidence.

### G1 — Do not instruct verification the model already performs

Remove instructions to add verification steps, run verification passes, or spawn verifier subagents. Keep — and strengthen — rules that constrain claims: cite the actual output, never assert a pass without it, say explicitly when something is unverified.

*Test:* does the sentence create work, or constrain a claim? Creates work → cut. Constrains a claim → keep.

### G2 — Make delegation guidance damping and model-conditional

Default posture is damping, because Opus 5 over-delegates: no subagent for work finishable in a handful of tool calls, never a subagent to verify, one rather than several, low spawn counts, and a deterministic cap where the harness allows one. Where Fable 5 is the target, keep delegation frequent but specify asynchronous, long-lived workers rather than blocking fan-out.

### G3 — Control length by selection, never by compression

Brevity comes from dropping content that would not change what the reader does next. Never from arrow chains, invented abbreviations, hyphen-stacked compounds, or fragments. When short and clear conflict, choose clear. Instrument the three length surfaces separately: conversational response, inter-tool narration, written deliverables.

### G4 — Never instruct reasoning transcription

No component asks the model to echo, transcribe, or explain its internal reasoning as response text. Introspection and self-analysis features are worded as claims about decisions, assumptions, and evidence — not as reproductions of thinking. Emoji thinking-markers and "expose your thinking" phrasing are the specific shapes to avoid.

### G5 — Keep the mood declarative, drop the volume

Declarative and imperative statements; no hedging verbs. But no `CRITICAL:`, no shouted `MUST`, no "if in doubt use X," no blanket "default to using X." State the trigger condition instead: `Use X when Y`.

### G6 — Do not make the model reason about its own context budget

Percentage-based transport guards may exist in the harness. Instructions telling the model to monitor its remaining budget, or harness output showing it a countdown, are removed. Where the harness compacts, tell the model that compaction happens and that it should not stop early.

### G7 — Bound scope on both sides

Constrain unrequested scope *and* require task completion in the same breath, because scope discipline alone degrades into premature "done." Add the assessment-vs-action rule: when the user is describing, asking, or thinking out loud, the deliverable is the assessment.

### G8 — Give the why, not only the what

Motivation generalizes where bare prohibitions do not — Anthropic's own example contrasts "NEVER use ellipses" against "your response will be read aloud by a text-to-speech engine, so never use ellipses." For Fable 5 this is explicitly a performance lever: "Claude Fable 5 tends to perform better when it understands the intent behind a request."

### G9 — Prescribe less; earn each instruction from an observed failure

Fable 5 degrades under prescription tuned for prior models. Anthropic's development method is minimal-first: "Begin with a minimal prompt using your strongest model, then iteratively add clarifications based on observed failure modes." Every retained instruction should trace to a failure actually seen — matching the existing `content-quality.md` rule that failures drive edits.

### G10 — Right altitude, and minimal ≠ short

"Specific enough to guide behavior effectively, yet flexible enough to provide the model with strong heuristics." And: "Minimal does not necessarily mean short; you still need to give the agent sufficient information up front." Load-bearing detail stays regardless of length; content that changes no outcome goes regardless of length.

### G11 — Prefer just-in-time context to pre-loading

Keep lightweight references — file paths, queries, pointers — and load at runtime. The hybrid Anthropic endorses is exactly the existing architecture: a small always-loaded core plus on-demand retrieval. This validates the `RULES.md` kernel + on-demand `RULES_*.md` module split; the pressure it creates is on what remains in the always-loaded tier.

### G12 — Curate tools and components so selection is unambiguous

"If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better." Overlapping component descriptions are a correctness defect, not a cosmetic one — they misfire in both directions (wrong pick, and no pick).

### G13 — Set effort deliberately, per route

Default `high`. `low`/`medium` liberally where quality holds — the primary cost and latency control. `xhigh` for demanding coding and agentic work. Do not carry prior-model effort defaults forward. Do not reach for `xhigh` reflexively, and do not disable thinking to save cost — lower the effort instead.

### G14 — Support long-horizon work with state, not with exhortation

Structured state in structured formats (`tests.json`), freeform progress notes, git as the checkpoint log, and a memory surface — "one lesson per file with a one-line summary at the top." For Fable 5 this is a documented performance lever, not just hygiene.

## Part 3 — Anti-pattern reference

| Anti-pattern | Why it fails on Claude 5 | Replacement |
|---|---|---|
| "Include a final verification step" | Compounds with native self-verification; pure token cost (Opus 5) | Delete. Keep only "cite the output you actually got" |
| Verifier subagent for ordinary tasks | Redundant verification *and* unnecessary delegation | Verify inline; reserve fresh-context verifiers for multi-hour autonomous runs |
| "Double-check your answer" | Re-check the model already performs | Delete |
| Arrow chains and invented abbreviations for brevity | Named anti-pattern; saves ~0 tokens; costs comprehension | Select what to include; write complete sentences |
| "Information density > readability" | Inverts Anthropic's stated priority | "If you have to choose between short and clear, choose clear" |
| "Monitor your context usage proactively" | Documented context-anxiety trigger (Fable 5) | Harness-side guard; tell the model compaction exists so it does not stop early |
| "Expose your thinking" / emoji thinking markers | `reasoning_extraction` refusal risk (Fable 5) | Surface decisions, assumptions, and evidence — not reasoning transcripts |
| `CRITICAL: You MUST use X` | Overtriggers on instruction-sensitive models | `Use X when Y` |
| "If in doubt, use X" | Named overtrigger phrase | Delete |
| Lowering `effort` to shorten a response | Effort governs thinking, not visible output length | Explicit conciseness instruction |
| Disabling thinking to cut cost (Opus 5) | Tool calls leak into text and never run; XML tag leakage | Keep thinking on at `low`/`medium` effort |
| "Only report high-severity issues" in review prompts | Followed literally; suppresses real findings | Report everything with confidence and severity; filter in a separate pass |
| Prescriptive step-by-step for capabilities the model has | Degrades Fable 5 output | State the goal and the constraints; let the model sequence |
| Scope limits without a completion clause | Degrades into premature "done" on partial work | Pair "stay in scope" with "finish the whole task" |

## Applicability boundary

Two things this research does **not** establish, stated so downstream work does not overclaim:

**Model coverage.** The Opus 5 and Fable 5 guides are model-specific by construction. Sonnet 5 has its own guide, not audited here. Where SuperClaude runs on a non-Claude-5 model, some guidance inverts outright — Opus 4.8 *under*-delegated and *under*-reached for tools, the precise opposite of Opus 5. Guidance derived here should be written so it does not actively harm older targets, and Section 1.2's model-conditional framing is the template.

**Measurement.** Every claim here is Anthropic's published behavioral guidance, not a measurement taken against this repository. The framework has a working method for behavioral probes — `claude -p` from *outside* the repo, per the `probe-observer-effect` gotcha — and high-severity changes deriving from this document should be A/B probed that way before being treated as settled.
