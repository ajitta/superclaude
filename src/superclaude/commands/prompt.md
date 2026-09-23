---
description: Rewrite a prompt for Claude Opus 5.5, Opus 5 or Fable 5.1 — strip prompting folklore that degrades these models, apply model-specific behavioral deltas, mark missing context as placeholders. Use when user types `/sc:prompt`, asks to improve or tune a prompt for Opus 5.5 / Opus 5 / Fable 5.1, or hands over a rough request to sharpen before sending. Do NOT auto-trigger on general prompt-engineering questions, on "what does this prompt do", or on auditing prompt files across a repo — those get a direct answer or `/claude-api prompt-audit`.
---

<component name="prompt" type="command">

  <role command="/sc:prompt">
    <mission>Rewrite a single prompt for Claude Opus 5.5, Opus 5 or Fable 5.1 — strip prompting folklore that degrades these models, apply model-specific behavioral deltas, and mark missing context as placeholders.</mission>
  </role>

  <syntax>/sc:prompt [prompt-text|path] [--model opus55|opus5|fable51] [--target cc|api] [--out path]</syntax>

  <flow>
  1. Capture the prompt from the inline argument, a file path, or the intent the user just described — and name which source was used.
  2. Resolve target model and surface (cc or api). Every flag resolves to a model ID first: `opus55` → 'claude-opus-5-5', `opus5` → 'claude-opus-5', `fable51` → 'claude-fable-5-1', and `fable5` is accepted as a legacy alias for 'claude-fable-5-1', since Fable 5 prompts run unchanged on Fable 5.1. When either is unstated, infer from the session: an Opus 5 or Opus 5.5 session resolves to its own ID in the Opus column, a Fable 5.x session to 'claude-fable-5-1', and a one-line assumption names the model ID and the column used. A session on any other model infers no target: ask for `--model`, or state the target assumed and why.
  3. Diagnose in both directions — the folklore present that degrades the target model, and the context the prompt is missing.
  4. Apply the model delta — read the target's section of the migration reference first, then touch only the axes the prompt actually exercises. A prompt with no delegation gets no delegation cap.
  5. Rewrite. Any context not read this session and not supplied by the user becomes a `[FILL: …]` placeholder, never an invention.
  6. Report the change delta. Removals tie to a named pattern or a documented model behavior; additions tie to their source — a file read this session, the user's own words, or a `[FILL: …]` slot. An addition with no source does not get reported, it gets deleted.
  7. Emit request configuration for `--target api` only: effort tier, `thinking.display`, and the `max_tokens` floor, read from the fact source rather than recalled.
  </flow>

  <model_delta>
  The two model families pull in opposite directions on several axes. An unresolved target model produces the inverse of the correct edit.

  This table is a mirror, not a source. Every row compresses the migration reference's `Behavioral shifts (prompt-tunable)` section for one family down to direction, and it is authoritative only while that reference is unreachable — when it is on the machine it gets read and it wins on conflict. The Opus column holds Opus 5 facts and carries them to 'claude-opus-5-5' unless a clause says otherwise. One exception holds until the reference gains an Opus 5.5 section: text marked `interim (Opus 5.5 prompting guide)`, in this table or in the request configuration below it, is a source for 'claude-opus-5-5', taken from the Opus 5.5 prompting guide at 'https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5' and What's new at 'https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5'. On an axis an interim mark names, it wins over the Opus 5 section read in its place; on every other axis that section wins over this table. The `--target cc` suppression is the command's own, because it comes from the harness rather than from the reference: Claude Code already injects scope discipline, task completion, self-correction, and the delegation cap, so rows marked † are `--target api` only — re-attaching them for cc adds tokens and no new information.

  | Axis | Opus (5 verified; 5.5 carried from 5 unless marked) | 'claude-fable-5-1' |
  |---|---|---|
  | Verification instructions | Delete — it self-verifies unprompted, and "double-check" causes over-verification | Keep only claim-grounding (report what a tool result shows); add a fresh-context, read-only verifier with a PASS/FAIL verdict only for long autonomous builds beyond what the model solves reliably alone |
  | Subagent delegation † | Cap it — this model reaches for subagents readily | Keep it; tell the lead to continue independent work while workers run, and to reuse a long-lived worker for follow-ups, since cache reads are cheap |
  | Tool-call batching | Issues parallel calls as expected | In loops where the next reads are implied rather than named it may issue one call per turn; append the one-sentence batching nudge each turn (a turn-scoped system message on `--target api`) |
  | Progress updates | Narrates readily; give it a cadence | Writes fewer updates; delete any hold-for-final line first, then add a when-and-what line only if the interface shows text between calls |
  | Task completion † | Pair scope discipline with "finish the whole task". `interim (Opus 5.5 prompting guide)`: for 'claude-opus-5-5' on fully unattended runs, add the guide's unattended-run paragraph at the end of the system prompt, present from the session's first request, as a `[FILL: …]` slot naming its URL, because the paragraph is not on the machine; leave it out of human-in-the-loop prompts | The same, and on autonomous workloads add the documented two-block autonomy text; leave it out of human-in-the-loop prompts |
  | Prescriptiveness † | Add scope discipline; it expands task scope | De-prescribe; state what to leave out (nearby fixes, extra committed test files) |
  | Verbosity and formatting | A brief conciseness instruction cuts length; effort is not the lever | Prose runs denser than Fable 5: define mannered prose as the anti-pattern; remove anti-formatting rules, because it under-formats |
  | Written deliverables | Calibrate file length explicitly | Lead with the outcome; at `xhigh` or `max` append the single-limit note naming `max_tokens` |
  | Native failure modes | Scope expansion, self-correction narration | Early stopping, unrequested adjacent actions, one call per turn in implied loops, whole-file rewrites, over-committed tests, memory answers at `low`, unmarked quotation of sources |
  | Intent framing | Full task specification up front in one turn | The reason behind the request, not just the request |

  Request configuration for 'claude-opus-5-5' on `--target api`, `interim (Opus 5.5 prompting guide)`: effort defaults to `medium` unless a removal row below sets it, with `xhigh` or `max` only where "you've measured a quality gain"; thinking cannot be disabled, so a `disabled` or `budget_tokens` thinking setting returns 400; `tool_choice` `any` or `tool` returns 400, so use `auto` with strict tools; the notes written between tool calls arrive as `thinking` blocks whose text is empty at the default display, so a harness that shows progress sets `display: "updates"` (beta, header `thinking-display-updates-2026-08-18`); changing the top-level `effort` between requests invalidates the prompt cache, and a per-message effort change (beta) keeps it; `max_tokens` 128,000 for long agentic turns. The thinking and `tool_choice` errors come from What's new, the rest from the prompting guide.
  </model_delta>

  <removal_targets>
  Folklore that helped older models and degrades these targets. This detector is the command's own, not a mirror: the reference describes model behavior, not the prompt habits that trip it. Signals are greppable — run them over the prompt rather than eyeballing. Where a row's action names a target model without giving its own reason, its direction comes from the delta rule above.

  | Pattern | Signal | Action |
  |---|---|---|
  | Thinking incantations | `think step by step`, `think carefully`, scratchpad tag instructions | Delete — redundant on thinking models and a cause of over-planning |
  | Reasoning write-out | `write out your reasoning`, `show your reasoning in the response`, `explain your chain of thought` | Delete for 'claude-opus-5-5' and 'claude-fable-5-1': their classifiers can decline such requests under the `reasoning_extraction` category, and on 'claude-opus-5-5' server-side fallback returns that decline instead of retrying it. On `--target api` set `thinking.display: "summarized"` so the caller reads the reasoning from the thinking blocks instead. Keep it for 'claude-opus-5', which has no such category and where a write-out can stand in for disabled thinking |
  | No-thinking rule | `do not think`, `respond without thinking`, `skip reasoning, just answer` | Delete for every target. 'claude-opus-5-5' and 'claude-fable-5-1' cannot turn thinking off; on 'claude-opus-5' the migration reference finds that such a rule increases tag leakage when thinking is disabled. On `--target api`, move the rule's intent to `effort: low` in the request configuration, overriding the target's default effort: lowering effort reduces thinking more reliably than a prompt rule does. For 'claude-opus-5-5', keep "Answer directly without deliberating." when it sits beside `effort: low`: the Opus 5.5 prompting guide offers that line for latency after lowering effort, provided quality is measured when it is added |
  | Self-check phrasing | `double-check`, `re-verify before responding` | Delete for 'claude-opus-5', and for 'claude-opus-5-5' as carried from it — this inverts the usual best practice |
  | Emphasis inflation | density of `MUST`, `NEVER`, `ALWAYS`, `CRITICAL` | State the real constraint once at normal volume, with its reason |
  | Proactivity boosters | `be thorough`, `do not be lazy`, bare `do not stop early` | Delete the slogans. Where the prompt drives autonomous multi-step work, replace them with the documented autonomy block (operating autonomously, reversible steps proceed, the assessment exception, check the last paragraph): a mechanism with a stated trigger, not a booster. On `--target cc` the harness already injects it, so add it only for `--target api` |
  | Narration suppression | `hold all findings for the final response`, `no commentary between steps` | Delete for 'claude-fable-5-1' — it already under-narrates |
  | Anti-formatting rules | `no bullet points`, `never use headers`, `avoid bold` | Replace with a conditional rule (lists when the content is multifaceted, plain prose when asked) for 'claude-fable-5-1' |
  | Verifiability switch | Opinion framing — `your thoughts on`, `reflect on`, or in Korean the noun for "thought" as the object of "describe" or "tell" — on a deliverable that needs checkable facts (dates, figures, symbols, terms) | Split into an explain request with scope, depth, and audience that names the checkable facts it must carry (dates, figures, names) and marks uncertain ones, then a separate judgment request with its criterion stated first; keep the framing when the deliverable is an opinion piece; when the prompt does not settle which, emit `[FILL: fact write-up / opinion piece]`. Applies to both families and both languages by decision, not by measurement: the Korean noun degrades anchors (36 runs, non-blind) and only the Fable target kept the framing (3/3); 'claude-opus-5' and English phrasing decomposed or slotted natively at baseline (2/2 each), so there the row makes an existing behavior deterministic |
  | Numeric output caps | `at most N words`, `under N bullets` | Replace with audience framing; caps starve reasoning on hard problems |
  | Severity filters | `only report high-severity`, `be conservative`, `high-confidence only` | Replace with report-everything-plus-severity-and-confidence; filtering during the pass depresses measured recall |
  | Step choreography | `STEP 1:` numbering over judgment work | State outcome, constraints, and verification; keep ordering only where order is real |
  | Prohibition walls | runs of three or more `Do not` / `Never` lines | Keep prohibitions whose failure reproduces; restate the rest positively |
  | Trait claims | `you tend to`, `don't be too verbose` | State the wanted behavior instead of the diagnosed flaw |
  | Expert persona as accuracy booster | A leading role clause — `You are a senior/world-class/expert/principal/twenty-year …`, `act as a …`, or in Korean an opener that names the model as an expert, often with a world's-best or top-tier qualifier, or asks it to answer as one — on a factual, diagnostic or code-writing deliverable (a lookup, a debugging question, a figure, a function to write) | Delete the clause and put the audience and quality-bar context from the context targets in its place; the change-delta names the cross-model evidence against the clause and does not suggest the clause is harmless to restore. Keep a role only when the deliverable is creative or stylistic prose, which code is not, or when the role is an evaluation lens with its own success criterion (an expert pair, a hostile reviewer), and then one sentence with no attribute the task does not use. Direction from cross-model measurement, not a Claude measurement: on knowledge benchmarks a persona left accuracy unchanged or lower, a longer persona hurt more, and attributes irrelevant to the task cost up to about thirty points. On code-writing prompts the row rests only on this framework's own finding that a seniority-implying agent description raised context hallucination and over-engineering; that measured hallucination and code shape, not correctness, and the report says so |
  | Embedded anchor | A prior estimate, suspected cause, or reference value stated before the ask — `probably the cache`, `should take about two days`, `the last run estimated 40%` — strongest when labeled as another model's or agent's output | Ask for the model's own estimate or diagnosis first, with its criterion stated, and for several independent candidates where one hint stands in for evidence; then present the prior as one input to compare against. The prior is another run's, model's or person's estimate or diagnosis, even when quoted exactly; an observed fact about the system stated with it (a version change, a measured slowdown) stays as evidence. Never rewrite the prior as `ignore the above` — an ignore instruction, chain-of-thought and reflection barely move an anchor, while stating the model's own criterion first reduces it, if modestly. Direction from measurement on non-Claude models; the labeled-prior effect and the one Claude result come from an unverified secondary summary |
  | Grader vocabulary | `you will be graded`, `hidden tests` | State every requirement; never describe the scoring apparatus |
  | Prefill scaffolding | trailing assistant turn, `output ONLY valid JSON`, stop-sequence guards | Replace with structured outputs — prefill errors on every target |
  </removal_targets>

  <context_targets>
  The rewrite adds as often as it removes. These are what only the author knows, and a prompt missing them gets generic output because the model fills the gap with safe defaults.

  - Audience: who reads the output and what they do with it.
  - Environment: the product, the codebase, and the constraints not visible from the request itself.
  - Quality-bar: what good means here, what done looks like, and how success gets checked — stated as an environment fact rather than an instruction to self-check.
  - Reason: why the work is being asked for — 'claude-fable-5-1' connects task to intent when given the reason.
  - Boundaries: what the task must not touch, and which actions fall outside it.
  - Compaction contract (`--target api`, client-side compaction only): the six things a summary must keep — problems and their resolutions, options tried or set aside, decisions and constraints stated exactly, current position, open items, and exact specifics.
  </context_targets>

  <fact_sourcing>
  Per-model behavioral facts — direction, effort ladders, verbatim tuning blocks, request parameters — are owned by the `claude-api` skill's model-migration reference, not by this command. The read happens whenever a model-conditional edit is about to enter the rewrite, which is the common case on every target rather than the rare one; only a prompt that exercises no delta axis skips it. Reach the reference as a file rather than by invoking the skill, whose own body is far larger than the section needed. The framework's prompt hook resolves the path and the target's line ranges into context at invocation — when that note is present, read the range it names; when it is absent, glob for the `model-migration` reference yourself, since the install root differs by machine and by scope and a fixed path is wrong. Then scope the read by anchoring on the `## Migrating to Claude <target>` heading and taking the first `### Behavioral shifts (prompt-tunable)` that follows it — that heading appears once per model in the file and by itself identifies none of them — plus the target's effort ladder on `--target api`. When a Grep for the target's own `## Migrating to Claude <model>` heading finds none, as for 'claude-opus-5-5' until upstream adds one, read the nearest earlier section of the same family, apply the interim text over it, and state in the report that the target had no section and which section was read instead. Never the guide whole, and never by line number, which moves with every release. Recalled values never substitute for a read, and the mirror table substitutes for one only while the reference is off the machine, its interim text only while the reference lacks the target's section.

  Environment facts — whether a file or directory exists, git state, project conventions, where a document lives — come from the repository, read at invocation time. An environment fact is either read or it is a `[FILL: …]` slot; there is no third source. Evidence wording ("confirmed", "measured") belongs only to a fact a tool call in this session actually returned.
  </fact_sourcing>

  <outputs>
  - Rewritten-prompt: the improved prompt, fenced and ready to copy.
  - Change-delta: a labeled section of its own — removals with their pattern, additions with their source. Never folded into the prose around the rewrite.
  - Placeholders: the fill-in slots only the user can complete.
  - Request-config: effort, thinking display, `max_tokens` floor, refusal fallback target, and the per-turn batching nudge placement — `--target api` only.
  </outputs>

  <tools>
  - Read: load the prompt when a file path is given, and load the anchored section of the `claude-api` model-migration reference — read as a file, which works whether or not the skill itself is installed.
  - Glob: locate that reference file, since its path is not fixed across machines.
  - Grep: confirm an environment fact — a path, a symbol, a convention — before it enters the rewrite, and locate the model anchor and the behavioral-shifts heading under it.
  - Bash: read-only repo state (`git status`, `git worktree list`, `ls`) when the prompt's subject is the repository itself.
  - Write: save the rewritten prompt when the user names a destination.
  </tools>

  <examples>
  | Trigger | Expected behavior |
  |---|---|
  | `/sc:prompt "refactor the auth module"` | Rewrite for the session model (an Opus 5.5 session reads the Opus column), flag missing audience and done-criteria |
  | `/sc:prompt --model fable51 --target api ./sys.md` | De-prescribe the file, add reason framing, emit effort and max_tokens config |
  | `/sc:prompt --model opus5 ./agent.md` | Strip self-check lines, cap delegation, add scope discipline |
  | `/sc:prompt --model opus55 --target api ./chat.md` | Delete `think carefully` and reasoning write-out lines, emit `medium` effort and the `display` setting, name the Opus 5 section read in place of a 5.5 one |
  | `/sc:prompt` on an already-clean prompt | Report the prompt as clean and emit no diff |
  | `/sc:prompt` on a folklore-clean but context-empty prompt | Report zero removals; emit only additions that name a source |
  </examples>

  <gotchas>
  - no-length-contest: Shortening is not the goal. Context is never cruft, and a rewrite that only got shorter deleted the highest-value words.
  - opus5-verify-inversion: Never add self-check phrasing for 'claude-opus-5', or for 'claude-opus-5-5', which carries its direction. Standard prompt-engineering habit produces exactly the wrong edit here.
  - model-required: An unresolved target model yields opposite instructions on delegation and verification. State the assumed model before rewriting.
  - clean-is-valid: A clean prompt gets reported as clean. A manufactured diff is worse than an empty one.
  - facts-not-memory: A model fact gets read from the migration reference, an environment fact (paths, git state, whether a directory is a subtree) from the repository. Neither gets recalled, and the mirror table does not stand in for a reference sitting unread on the machine — that is a stale answer, not a saved read. Two things are exceptions: text marked interim, only while the reference lacks the target's section, and the reasons the detector rows give for their targets, which are the command's own. The saving is in scoping the read to one anchored section; pulling the whole guide to source one number is its own defect. An unverified environment fact is the costliest defect this command can ship, because the user pastes the rewrite into a fresh session without re-checking it.
  - booster-vs-mechanism: The autonomy block is not a proactivity booster; deleting it under the booster rule reintroduces early stopping on 'claude-fable-5-1'.
  </gotchas>

  <bounds>
    <does>rewrites a single prompt for a named target model, strips degrading folklore, adds the context the prompt lacks, marks user-only context as placeholders, and emits request configuration for API targets.</does>
    <never>audits or edits prompt files across a repository, invents context it has not read, or treats brevity as the objective.</never>
    <fallback>When the migration reference is not on the machine, the mirror table here carries the rewrite and the report states that the reference was not read. When it is on the machine without a section for the target, the nearest earlier section of the family carries the rewrite with the interim text over it, and the report names the section read. Repository-wide prompt-file audits route to `/claude-api prompt-audit`.</fallback>
  </bounds>

  <handoff next="/sc:brainstorm /sc:implement /sc:review"/>
</component>
