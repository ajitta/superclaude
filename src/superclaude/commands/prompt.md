---
description: Rewrite a prompt for Claude Opus 5 or Fable 5 — strip prompting folklore that degrades these models, apply model-specific behavioral deltas, mark missing context as placeholders. Use when user types `/sc:prompt`, asks to improve or tune a prompt for Opus 5 / Fable 5, or hands over a rough request to sharpen before sending. Do NOT auto-trigger on general prompt-engineering questions, on "what does this prompt do", or on auditing prompt files across a repo — those get a direct answer or `/claude-api prompt-audit`.
---

<component name="prompt" type="command">

  <role command="/sc:prompt">
    <mission>Rewrite a single prompt for Claude Opus 5 or Fable 5 — strip prompting folklore that degrades these models, apply model-specific behavioral deltas, and mark missing context as placeholders.</mission>
  </role>

  <syntax>/sc:prompt [prompt-text|path] [--model opus5|fable5] [--target cc|api] [--out path]</syntax>

  <flow>
  1. Capture the prompt from the inline argument, a file path, or the intent the user just described — and name which source was used.
  2. Resolve target model ('claude-opus-5' or 'claude-fable-5') and surface (cc or api). When either is unstated, infer from the session and record the assumption in one line.
  3. Diagnose in both directions — the folklore present that degrades the target model, and the context the prompt is missing.
  4. Apply the model delta, touching only axes the prompt actually exercises. A prompt with no delegation gets no delegation cap.
  5. Rewrite. Context only the user holds becomes a `[FILL: …]` placeholder, never an invention.
  6. Report the change delta — each removal, addition, and rewrite tied to a named pattern or a documented model behavior.
  7. Emit request configuration for `--target api` only: effort tier, `thinking.display`, and the `max_tokens` floor, read from the fact source rather than recalled.
  </flow>

  <model_delta>
  The two targets pull in opposite directions on several axes. An unresolved target model produces the inverse of the correct edit.

  | Axis | 'claude-opus-5' | 'claude-fable-5' |
  |---|---|---|
  | Verification instructions | Delete — it self-verifies unprompted, and "double-check" causes over-verification | Add — long runs need an explicit checking cadence plus fresh-context verifier subagents |
  | Subagent delegation | Cap it — this model reaches for subagents readily | Encourage it — asynchronous delegation is a strength |
  | Prescriptiveness | Add scope discipline; it expands task scope | De-prescribe — step-by-step scaffolding lowers output quality |
  | Verbosity | A brief conciseness instruction cuts length; effort is not the lever | A communication-style section steers it; instruction following is strong |
  | Written deliverables | Calibrate file length explicitly | A lead-with-outcome instruction covers it |
  | Native failure modes | Scope expansion, self-correction narration | Early stopping, context anxiety, unrequested adjacent actions |
  | Intent framing | Full task specification up front in one turn | The reason behind the request, not just the request |
  </model_delta>

  <removal_targets>
  Folklore that helped older models and degrades these two. Signals are greppable — run them over the prompt rather than eyeballing.

  | Pattern | Signal | Action |
  |---|---|---|
  | Thinking incantations | `think step by step`, scratchpad tag instructions | Delete — redundant on thinking models and a cause of over-planning |
  | Self-check phrasing | `double-check`, `re-verify before responding` | Delete for 'claude-opus-5' — this inverts the usual best practice |
  | Emphasis inflation | density of `MUST`, `NEVER`, `ALWAYS`, `CRITICAL` | State the real constraint once at normal volume, with its reason |
  | Proactivity boosters | `be thorough`, `do not be lazy`, `do not stop early` | Delete — both targets are proactive by default |
  | Numeric output caps | `at most N words`, `under N bullets` | Replace with audience framing; caps starve reasoning on hard problems |
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
  - Reason: why the work is being asked for — 'claude-fable-5' connects task to intent when given the reason.
  - Boundaries: what the task must not touch, and which actions fall outside it.
  </context_targets>

  <fact_sourcing>
  Behavioral facts that change between model releases — effort ladders, verbatim tuning blocks, request parameters, pricing — come from the `claude-api` skill's model-migration reference, read at invocation time. The delta table in this command carries direction only, which ages far more slowly than numbers. Recalled values never substitute for a read.
  </fact_sourcing>

  <outputs>
  - Rewritten-prompt: the improved prompt, fenced and ready to copy.
  - Change-delta: removals, additions, and rewrites, each with its reason.
  - Placeholders: the fill-in slots only the user can complete.
  - Request-config: effort, thinking display, and max_tokens floor — `--target api` only.
  </outputs>

  <tools>
  - Skill: invoke `claude-api` for release-current model behavior facts.
  - Read: load the prompt when a file path is given.
  - Write: save the rewritten prompt when the user names a destination.
  </tools>

  <examples>
  | Trigger | Expected behavior |
  |---|---|
  | `/sc:prompt "refactor the auth module"` | Rewrite for the session model, flag missing audience and done-criteria |
  | `/sc:prompt --model fable5 --target api ./sys.md` | De-prescribe the file, add reason framing, emit effort and max_tokens config |
  | `/sc:prompt --model opus5 ./agent.md` | Strip self-check lines, cap delegation, add scope discipline |
  | `/sc:prompt` on an already-clean prompt | Report the prompt as clean and emit no diff |
  </examples>

  <gotchas>
  - no-length-contest: Shortening is not the goal. Context is never cruft, and a rewrite that only got shorter deleted the highest-value words.
  - opus5-verify-inversion: Never add self-check phrasing for 'claude-opus-5'. Standard prompt-engineering habit produces exactly the wrong edit here.
  - model-required: An unresolved target model yields opposite instructions on delegation and verification. State the assumed model before rewriting.
  - clean-is-valid: A clean prompt gets reported as clean. A manufactured diff is worse than an empty one.
  - facts-not-memory: Effort ladders and verbatim tuning blocks get read from the `claude-api` skill, never recalled.
  </gotchas>

  <bounds>
    <does>rewrites a single prompt for a named target model, strips degrading folklore, adds the context the prompt lacks, marks user-only context as placeholders, and emits request configuration for API targets.</does>
    <never>audits or edits prompt files across a repository, invents context only the user holds, or treats brevity as the objective.</never>
    <fallback>When the `claude-api` skill is unavailable, the delta table here carries the rewrite and the report states that release-current facts were not read. Repository-wide prompt-file audits route to `/claude-api prompt-audit`.</fallback>
  </bounds>

  <handoff next="/sc:brainstorm /sc:implement /sc:review"/>
</component>
