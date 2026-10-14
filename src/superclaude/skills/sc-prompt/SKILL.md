---
name: sc-prompt
description: Rewrites a single prompt for Claude Opus 5.5, Sonnet 5.5, Opus 5 or Fable 5.1 - strips prompting folklore that degrades these models, applies model-specific deltas, marks missing context as placeholders. Use when asked to tune a prompt for these models. Not for prompt-engineering questions or repo-wide prompt audits (`/claude-api prompt-audit`).
argument-hint: "[prompt-text|path] [--model opus55|sonnet55|opus5|fable51] [--target cc|api] [--out path]"
---

# Rewrite a prompt for a target model

Arguments: $ARGUMENTS

- `--model opus55|sonnet55|opus5|fable51`: target model, resolved in step 2.
- `--target cc|api`: target surface, resolved in step 2.
- `--out <path>`: write the rewritten prompt there; without it nothing is written.

## Steps

1. **Capture** the prompt from the inline argument, a file path, or the intent the user just described, and name which source was used.
2. **Resolve** the target model and surface (`cc` or `api`). Flags map to model IDs: `opus55` → 'claude-opus-5-5', `sonnet55` → 'claude-sonnet-5-5', `opus5` → 'claude-opus-5', `fable51` → 'claude-fable-5-1'; `fable5` is a legacy alias for 'claude-fable-5-1', since Fable 5 prompts run unchanged on Fable 5.1. When either is unstated, infer it from the session (an Opus 5 or Opus 5.5 session to its own ID, Sonnet 5.5 to 'claude-sonnet-5-5', Fable 5.x to 'claude-fable-5-1') and state the assumption in one line naming the model ID. A session on any other model (an earlier Sonnet, Haiku) infers nothing: ask for `--model`, or state the target assumed and why. Never default to Opus: its verification edit is the inverse of Sonnet's.
3. **Diagnose** both directions: run the removal-target signals over the prompt (grep them rather than eyeballing), and check it against the context targets for what is missing.
4. **Apply** the model delta from "Model facts" below, touching only the axes the prompt exercises: a prompt with no delegation gets no delegation cap. Rows marked † are `--target api` only, because Claude Code already injects scope discipline, task completion, self-correction and the delegation cap.
5. **Rewrite**. Context not read this session and not supplied by the user becomes a `[FILL: …]` placeholder, never an invention.
6. **Report** the change delta. Each removal names its pattern or a documented model behavior; each addition names its source: a file read this session, the user's own words, or a `[FILL: …]` slot. An addition with no source is deleted, not reported.
7. **Emit** request configuration for `--target api` only: effort tier, `thinking.display` and the `max_tokens` floor, taken from the model facts rather than recalled.

## Model facts

Per-model direction is owned by the `claude-api` skill's model-migration reference (`claude-api/shared/model-migration.md`), read as a file rather than by invoking that skill, whose body is far larger than the section needed.

- The prompt hook names the reference's path and each model's line ranges when `/sc-prompt` is typed. Without that note, glob for `**/claude-api/shared/model-migration.md` under the `.claude` directories; the install root differs by machine and scope. When the note says no reference was found, search no further: the hook already searched the project's, the user's and `CLAUDE_CONFIG_DIR`'s `.claude` directories and Claude Code's bundled skills, and a copy elsewhere on disk (another project's scratch, a test fixture) is not this user's reference.
- Read only the target's section: anchor on `## Migrating to Claude <target>` and take the first `### Behavioral shifts (prompt-tunable)` after it (the heading repeats once per model), plus the target's effort ladder on `--target api`. Never the reference whole, never by line number, and never a recalled value in place of a read.
- Read the target's mirror file below on every run that applies a delta. It carries this skill's own additions (the † marks, prompting-guide lines the reference lacks) and stands in for the reference only while the reference is off the machine or has no section for the target; then the report says the reference or section was not read. On conflict the reference wins.
- Never read an earlier model's section in place of a missing one: the Opus 5 section carries the `high` default Opus 5.5 retired, and the Sonnet 5 section carries effort advice the Sonnet 5.5 section replaces.

Mirror files, one per target:

- `${CLAUDE_SKILL_DIR}/references/opus.md`: 'claude-opus-5' and 'claude-opus-5-5'
- `${CLAUDE_SKILL_DIR}/references/fable-5-1.md`: 'claude-fable-5-1'
- `${CLAUDE_SKILL_DIR}/references/sonnet-5-5.md`: 'claude-sonnet-5-5'

Environment facts (whether a file or directory exists, git state, project conventions) come from the repository at invocation time: read, or a `[FILL: …]` slot, with no third source. "Confirmed" or "measured" belongs only to a fact a tool call returned this session. An unverified environment fact is the costliest defect this skill can ship, because the user pastes the rewrite into a fresh session without re-checking it.

## Removal targets

Folklore that helped older models and degrades these targets. This detector is the skill's own. Where a row names a target without its own reason, the direction comes from that target's mirror file. Rows marked ‡ cite `${CLAUDE_SKILL_DIR}/references/evidence.md` in the change delta; read it when one of them fires.

| Pattern | Signal | Action |
|---|---|---|
| Thinking incantations | `think step by step`, `think carefully`, scratchpad tag instructions | Delete: redundant on thinking models and a cause of over-planning. 'claude-sonnet-5-5' only: when the prompt asks for a JSON answer to a task that needs a few steps of working out, replace it with the guide's line `Think the problem through before you answer.` at the end of the system prompt, under adaptive thinking; at `low` and `medium` the model often answers such tasks without thinking |
| Reasoning write-out | `write out your reasoning`, `show your reasoning in the response`, `explain your chain of thought` | Delete for 'claude-opus-5-5', 'claude-sonnet-5-5' and 'claude-fable-5-1': their classifiers can decline it under `reasoning_extraction`, and on the two 5.5 models server-side fallback returns that decline instead of retrying. On `--target api` set `thinking.display: "summarized"` (adaptive thinking only) so the caller reads the thinking blocks instead. Keep it for 'claude-opus-5', which has no such category and where a write-out can stand in for disabled thinking |
| No-thinking rule | `do not think`, `respond without thinking`, `skip reasoning, just answer` | Delete for every target: 'claude-opus-5-5' and 'claude-fable-5-1' cannot turn thinking off, and on 'claude-opus-5' the rule increases tag leakage when thinking is disabled. On `--target api` move its intent to `effort: low`, overriding the target's default. For 'claude-opus-5-5', keep "Answer directly without deliberating." beside `effort: low` (the Opus 5.5 guide's latency line), with quality measured when it is added |
| Self-check phrasing | `double-check`, `re-verify before responding` | Delete for 'claude-opus-5' and 'claude-opus-5-5'. For 'claude-sonnet-5-5' on prompts that change code, replace the slogan with the real-check requirement in its mirror file, keeping any concrete check the prompt names; on other prompts delete it |
| Tool discouragement | `only use tools when strictly necessary`, `minimize tool calls`, `avoid unnecessary tool calls` | Delete for 'claude-sonnet-5-5', which follows such lines literally and answers from training knowledge instead. For other targets delete only when the line contradicts work the prompt requires (running tests, looking up account data) and say so in the change delta; keep a concrete restriction (no network, a named tool) as a boundary |
| Emphasis inflation | density of `MUST`, `NEVER`, `ALWAYS`, `CRITICAL` | State the real constraint once at normal volume, with its reason |
| Proactivity boosters | `be thorough`, `do not be lazy`, bare `do not stop early` | Delete the slogans. Where the prompt drives autonomous multi-step work on `--target api`, put the documented autonomy block in their place (operating autonomously, reversible steps proceed, the assessment exception, check the last paragraph): a mechanism with a stated trigger, not a booster. On `--target cc` the harness already injects it |
| Narration suppression | `hold all findings for the final response`, `no commentary between steps` | Delete for 'claude-fable-5-1', which already under-narrates, and for 'claude-sonnet-5-5', whose guide and reference both say to remove such lines |
| Anti-formatting rules | `no bullet points`, `never use headers`, `avoid bold` | For 'claude-fable-5-1', replace with a conditional rule: lists when the content is multifaceted, plain prose when asked |
| Verifiability switch ‡ | Opinion framing (`your thoughts on`, `reflect on`, or in Korean the noun for "thought" as the object of "describe" or "tell") on a deliverable that needs checkable facts (dates, figures, symbols, terms) | Split into an explain request with scope, depth and audience that names the checkable facts it must carry and marks uncertain ones, then a separate judgment request with its criterion stated first. Keep the framing for an opinion piece; when the prompt does not settle which, emit `[FILL: fact write-up / opinion piece]`. Applies to every target and both languages |
| Numeric output caps | `at most N words`, `under N bullets` | Replace with audience framing; caps starve reasoning on hard problems |
| Severity filters | `only report high-severity`, `be conservative`, `high-confidence only` | Replace with report-everything-plus-severity-and-confidence; filtering during the pass depresses recall |
| Step choreography | `STEP 1:` numbering over judgment work | State outcome, constraints and verification; keep ordering only where order is real |
| Prohibition walls | runs of three or more `Do not` / `Never` lines | Keep prohibitions whose failure reproduces; restate the rest positively |
| Trait claims | `you tend to`, `don't be too verbose` | State the wanted behavior instead of the diagnosed flaw |
| Expert persona as accuracy booster ‡ | A leading role clause (`You are a senior/world-class/expert/principal/twenty-year …`, `act as a …`, or a Korean opener naming the model as a top expert) on a factual, diagnostic or code-writing deliverable | Delete the clause and put the audience and quality-bar context in its place; do not suggest the clause is harmless to restore. Keep a role only for creative or stylistic prose (code is not), or as an evaluation lens with its own success criterion (an expert pair, a hostile reviewer), and then as one sentence with no attribute the task does not use |
| Embedded anchor ‡ | A prior estimate, suspected cause or reference value stated before the ask (`probably the cache`, `should take about two days`, `the last run estimated 40%`), strongest when labeled as another model's or agent's output | Ask for the model's own estimate or diagnosis first, with its criterion stated, and for several independent candidates where one hint stands in for evidence; then present the prior as one input to compare against. The prior is another run's, model's or person's estimate, even when quoted exactly; an observed fact stated with it (a version change, a measured slowdown) stays as evidence. Never rewrite the prior as `ignore the above` |
| Grader vocabulary | `you will be graded`, `hidden tests` | State every requirement; never describe the scoring apparatus |
| Prefill scaffolding | trailing assistant turn, `output ONLY valid JSON`, stop-sequence guards | Replace with structured outputs; prefill errors on every target |

## Context targets

The rewrite adds as often as it removes. A prompt missing these gets generic output, because the model fills the gap with safe defaults.

- Audience: who reads the output and what they do with it.
- Environment: the product, the codebase, and constraints not visible from the request.
- Quality bar: what good means here, what done looks like and how success gets checked, stated as an environment fact rather than an instruction to self-check.
- Reason: why the work is asked for; 'claude-fable-5-1' connects task to intent when given the reason.
- Boundaries: what the task must not touch, and which actions fall outside it.
- Compaction contract (`--target api`, client-side compaction only): a summary keeps problems and their resolutions, options tried or set aside, decisions and constraints stated exactly, current position, open items, and exact specifics.

## Output

- The rewritten prompt, fenced and ready to copy.
- The change delta as its own labeled section, never folded into the prose around the rewrite.
- The `[FILL: …]` slots only the user can complete.
- `--target api` only: effort, thinking display, `max_tokens` floor, refusal fallback target, and where the per-turn batching nudge goes.

Tools: Read for the prompt file and the reference section, Glob to locate the reference, Grep to confirm an environment fact and find the model anchor, read-only Bash (`git status`, `git worktree list`, `ls`) when the prompt's subject is the repository, Write only for `--out`.

| Invocation | Expected behavior |
|---|---|
| `/sc-prompt "refactor the auth module"` | Rewrite for the session model (an Opus 5.5 session uses the Opus file), flag missing audience and done-criteria |
| `/sc-prompt --model fable51 --target api ./sys.md` | De-prescribe the file, add reason framing, emit effort and `max_tokens` config |
| `/sc-prompt --model opus5 ./agent.md` | Strip self-check lines, cap delegation, add scope discipline |
| `/sc-prompt --model opus55 --target api ./chat.md` | Delete `think carefully` and reasoning write-out lines, emit `medium` effort and the `display` setting, name the Opus 5.5 section read or say it was missing |
| `/sc-prompt --model sonnet55 --target api ./agent.md` | Turn `double-check` into the real-check requirement, delete `only use tools when strictly necessary`, emit `medium` effort for agentic coding |
| `/sc-prompt` on an already-clean prompt | Report the prompt as clean and emit no diff |
| `/sc-prompt` on a folklore-clean but context-empty prompt | Report zero removals; emit only additions that name a source |

## Gotchas

- Shortening is not the goal. Context is never cruft, and a rewrite that only got shorter deleted the highest-value words.
- A clean prompt gets reported as clean. A manufactured diff is worse than an empty one.
- Never add self-check phrasing for the Opus targets, where the usual prompt-engineering habit produces exactly the wrong edit; never delete Sonnet 5.5's verification requirement, replace the slogan with a real check.
- On an Opus 5.5 or Sonnet 5.5 session, a prompt passed inline that asks for written-out reasoning can be declined as `reasoning_extraction` before this skill runs. Tell the user to pass such a prompt as a file path.
- The autonomy block is not a proactivity booster: deleting it under the booster row reintroduces early stopping on 'claude-fable-5-1'.
- A mirror file never stands in for a reference sitting unread on the machine; that is a stale answer, not a saved read.

This skill rewrites one prompt. Auditing or editing prompt files across a repository belongs to `/claude-api prompt-audit`.
