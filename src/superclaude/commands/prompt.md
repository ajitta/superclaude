---
description: Rewrite a prompt for Claude Opus 5 or Fable 5.1 — strip prompting folklore that degrades these models, apply model-specific behavioral deltas, mark missing context as placeholders. Use when user types `/sc:prompt`, asks to improve or tune a prompt for Opus 5 / Fable 5.1, or hands over a rough request to sharpen before sending. Do NOT auto-trigger on general prompt-engineering questions, on "what does this prompt do", or on auditing prompt files across a repo — those get a direct answer or `/claude-api prompt-audit`.
---

<component name="prompt" type="command">

  <role command="/sc:prompt">
    <mission>Rewrite a single prompt for Claude Opus 5 or Fable 5.1 — strip prompting folklore that degrades these models, apply model-specific behavioral deltas, and mark missing context as placeholders.</mission>
  </role>

  <syntax>/sc:prompt [prompt-text|path] [--model opus5|fable51] [--target cc|api] [--out path]</syntax>

  <flow>
  1. Capture the prompt from the inline argument, a file path, or the intent the user just described — and name which source was used.
  2. Resolve target model ('claude-opus-5' or 'claude-fable-5-1') and surface (cc or api). `fable5` is accepted as a legacy alias for the Fable column, since Fable 5 prompts run unchanged on Fable 5.1. When either is unstated, infer from the session and record the assumption in one line.
  3. Diagnose in both directions — the folklore present that degrades the target model, and the context the prompt is missing.
  4. Apply the model delta, touching only axes the prompt actually exercises. A prompt with no delegation gets no delegation cap.
  5. Rewrite. Any context not read this session and not supplied by the user becomes a `[FILL: …]` placeholder, never an invention.
  6. Report the change delta. Removals tie to a named pattern or a documented model behavior; additions tie to their source — a file read this session, the user's own words, or a `[FILL: …]` slot. An addition with no source does not get reported, it gets deleted.
  7. Emit request configuration for `--target api` only: effort tier, `thinking.display`, and the `max_tokens` floor, read from the fact source rather than recalled.
  </flow>

  <model_delta>
  The two targets pull in opposite directions on several axes. An unresolved target model produces the inverse of the correct edit.

  On `--target cc` the Claude Code harness already injects scope discipline, task completion, self-correction, and the delegation cap. Rows marked † are `--target api` only — re-attaching them for cc adds tokens and no new information.

  | Axis | 'claude-opus-5' | 'claude-fable-5-1' |
  |---|---|---|
  | Verification instructions | Delete — it self-verifies unprompted, and "double-check" causes over-verification | Keep only claim-grounding (report what a tool result shows); add a fresh-context, read-only verifier with a PASS/FAIL verdict only for long autonomous builds beyond what the model solves reliably alone |
  | Subagent delegation † | Cap it — this model reaches for subagents readily | Keep it; tell the lead to continue independent work while workers run, and to reuse a long-lived worker for follow-ups, since cache reads are cheap |
  | Tool-call batching | Issues parallel calls as expected | In loops where the next reads are implied rather than named it may issue one call per turn; append the one-sentence batching nudge each turn (a turn-scoped system message on `--target api`) |
  | Progress updates | Narrates readily; give it a cadence | Writes fewer updates; delete any hold-for-final line first, then add a when-and-what line only if the interface shows text between calls |
  | Task completion † | Pair scope discipline with "finish the whole task" | The same, and on autonomous workloads add the documented two-block autonomy text; leave it out of human-in-the-loop prompts |
  | Prescriptiveness † | Add scope discipline; it expands task scope | De-prescribe; state what to leave out (nearby fixes, extra committed test files) |
  | Verbosity and formatting | A brief conciseness instruction cuts length; effort is not the lever | Prose runs denser than Fable 5: define mannered prose as the anti-pattern; remove anti-formatting rules, because it under-formats |
  | Written deliverables | Calibrate file length explicitly | Lead with the outcome; at `xhigh` or `max` append the single-limit note naming `max_tokens` |
  | Native failure modes | Scope expansion, self-correction narration | Early stopping, unrequested adjacent actions, one call per turn in implied loops, whole-file rewrites, over-committed tests, memory answers at `low`, unmarked quotation of sources |
  | Intent framing | Full task specification up front in one turn | The reason behind the request, not just the request |
  </model_delta>

  <removal_targets>
  Folklore that helped older models and degrades these two. Signals are greppable — run them over the prompt rather than eyeballing.

  | Pattern | Signal | Action |
  |---|---|---|
  | Thinking incantations | `think step by step`, scratchpad tag instructions | Delete — redundant on thinking models and a cause of over-planning |
  | Self-check phrasing | `double-check`, `re-verify before responding` | Delete for 'claude-opus-5' — this inverts the usual best practice |
  | Emphasis inflation | density of `MUST`, `NEVER`, `ALWAYS`, `CRITICAL` | State the real constraint once at normal volume, with its reason |
  | Proactivity boosters | `be thorough`, `do not be lazy`, bare `do not stop early` | Delete the slogans. Where the prompt drives autonomous multi-step work, replace them with the documented autonomy block (operating autonomously, reversible steps proceed, the assessment exception, check the last paragraph): a mechanism with a stated trigger, not a booster. On `--target cc` the harness already injects it, so add it only for `--target api` |
  | Narration suppression | `hold all findings for the final response`, `no commentary between steps` | Delete for 'claude-fable-5-1' — it already under-narrates |
  | Anti-formatting rules | `no bullet points`, `never use headers`, `avoid bold` | Replace with a conditional rule (lists when the content is multifaceted, plain prose when asked) for 'claude-fable-5-1' |
  | Numeric output caps | `at most N words`, `under N bullets` | Replace with audience framing; caps starve reasoning on hard problems |
  | Severity filters | `only report high-severity`, `be conservative`, `high-confidence only` | Replace with report-everything-plus-severity-and-confidence; filtering during the pass depresses measured recall |
  | Step choreography | `STEP 1:` numbering over judgment work | State outcome, constraints, and verification; keep ordering only where order is real |
  | Prohibition walls | runs of three or more `Do not` / `Never` lines | Keep prohibitions whose failure reproduces; restate the rest positively |
  | Trait claims | `you tend to`, `don't be too verbose` | State the wanted behavior instead of the diagnosed flaw |
  | Grader vocabulary | `you will be graded`, `hidden tests` | State every requirement; never describe the scoring apparatus |
  | Prefill scaffolding | trailing assistant turn, `output ONLY valid JSON`, stop-sequence guards | Replace with structured outputs — prefill errors on both targets |
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
  Behavioral facts that change between model releases — effort ladders, verbatim tuning blocks, request parameters, pricing — come from the `claude-api` skill's model-migration reference, read at invocation time. The delta table in this command carries direction only, which ages far more slowly than numbers. Recalled values never substitute for a read.

  Environment facts — whether a file or directory exists, git state, project conventions, where a document lives — come from the repository, read at invocation time. An environment fact is either read or it is a `[FILL: …]` slot; there is no third source. Evidence wording ("confirmed", "measured") belongs only to a fact a tool call in this session actually returned.
  </fact_sourcing>

  <outputs>
  - Rewritten-prompt: the improved prompt, fenced and ready to copy.
  - Change-delta: a labeled section of its own — removals with their pattern, additions with their source. Never folded into the prose around the rewrite.
  - Placeholders: the fill-in slots only the user can complete.
  - Request-config: effort, thinking display, `max_tokens` floor, refusal fallback target, and the per-turn batching nudge placement — `--target api` only.
  </outputs>

  <tools>
  - Skill: invoke `claude-api` for release-current model behavior facts.
  - Read: load the prompt when a file path is given.
  - Grep: confirm an environment fact — a path, a symbol, a convention — before it enters the rewrite.
  - Bash: read-only repo state (`git status`, `git worktree list`, `ls`) when the prompt's subject is the repository itself.
  - Write: save the rewritten prompt when the user names a destination.
  </tools>

  <examples>
  | Trigger | Expected behavior |
  |---|---|
  | `/sc:prompt "refactor the auth module"` | Rewrite for the session model, flag missing audience and done-criteria |
  | `/sc:prompt --model fable51 --target api ./sys.md` | De-prescribe the file, add reason framing, emit effort and max_tokens config |
  | `/sc:prompt --model opus5 ./agent.md` | Strip self-check lines, cap delegation, add scope discipline |
  | `/sc:prompt` on an already-clean prompt | Report the prompt as clean and emit no diff |
  | `/sc:prompt` on a folklore-clean but context-empty prompt | Report zero removals; emit only additions that name a source |
  </examples>

  <gotchas>
  - no-length-contest: Shortening is not the goal. Context is never cruft, and a rewrite that only got shorter deleted the highest-value words.
  - opus5-verify-inversion: Never add self-check phrasing for 'claude-opus-5'. Standard prompt-engineering habit produces exactly the wrong edit here.
  - model-required: An unresolved target model yields opposite instructions on delegation and verification. State the assumed model before rewriting.
  - clean-is-valid: A clean prompt gets reported as clean. A manufactured diff is worse than an empty one.
  - facts-not-memory: Model facts (effort ladders, verbatim tuning blocks) get read from the `claude-api` skill; environment facts (paths, git state, whether a directory is a subtree) get read from the repository. Neither gets recalled. An unverified environment fact is the costliest defect this command can ship, because the user pastes the rewrite into a fresh session without re-checking it.
  - booster-vs-mechanism: The autonomy block is not a proactivity booster; deleting it under the booster rule reintroduces early stopping on 'claude-fable-5-1'.
  </gotchas>

  <bounds>
    <does>rewrites a single prompt for a named target model, strips degrading folklore, adds the context the prompt lacks, marks user-only context as placeholders, and emits request configuration for API targets.</does>
    <never>audits or edits prompt files across a repository, invents context it has not read, or treats brevity as the objective.</never>
    <fallback>When the `claude-api` skill is unavailable, the delta table here carries the rewrite and the report states that release-current facts were not read. Repository-wide prompt-file audits route to `/claude-api prompt-audit`.</fallback>
  </bounds>

  <handoff next="/sc:brainstorm /sc:implement /sc:review"/>
</component>
