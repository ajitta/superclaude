---
sources:
  - {file: "claude-api/shared/model-migration.md", section: "## Migrating to Claude Sonnet 5.5", retrieved: 2026-09-30}
  - {url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5", retrieved: 2026-09-30}
---

# Sonnet: 'claude-sonnet-5-5'

Each row mirrors the reference's `## Migrating to Claude Sonnet 5.5` section and the Sonnet 5.5 prompting guide. A `[FILL: guide]` below means a `[FILL: …]` slot naming 'https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5': the paragraph is in the prompting guide, not the reference, and is not on the machine. † = `--target api` only.

## Behavioral delta

- Verification instructions: on prompts that change code, replace self-check slogans with a real-check requirement: run the tests, type-checker, build or the changed command before reporting done; a syntax-only check or one that failed to start does not count; name any check not run and why. Most needed at `low`, where it can report a change done without one.
- Subagent delegation †: no direction below `xhigh`. At `xhigh` or `max` add the guide's stop-and-report line, so it does not start its own review rounds or reviewer subagents unasked, as `[FILL: guide]`.
- Tool-call batching: no documented delta.
- Progress updates: delete any hold-for-final line; notes longer than a sentence or two arrive as thinking blocks, so add a when-and-what line only if the interface shows them.
- Task completion †: at `low` and `medium` on agentic coding it can check in before the work is done; add the guide's keep-working paragraph (stop only when blocked or before a risky step) as `[FILL: guide]`. Leave it out of human-in-the-loop prompts that want check-ins.
- Prescriptiveness †: it adds unrequested tests, docs and supporting files at every effort; add the guide's no-unrequested-additions line (mention, don't do) as `[FILL: guide]`. On open-ended asks for ideas or a plan, say to give them and stop.
- Verbosity and formatting: carried from Sonnet 5: length tracks task complexity, and a brief conciseness instruction cuts it.
- Written deliverables: no documented delta.
- Native failure modes: early check-in at `low`/`medium`, unrequested supporting files, self-started review at `xhigh`/`max`, answers from training knowledge where a search would catch a change, skipped checks at `low`, near-miss tool-name casing.
- Tool use: follows tool-discouraging lines literally and can answer from training knowledge; delete those lines (removal row), and where a search tool exists add the guide's check-current-specifics line.
- Intent framing: full task specification up front; for a JSON answer to a multi-step task, see the thinking-incantations removal row.

## Request configuration: `--target api`

- Effort: `medium` for agentic coding and multistep tool use, `low` for chat, classification and extraction, `high` (the API default) when the workload is unstated, and `xhigh` or `max` only where a quality gain was measured. The levels are recalibrated, so a Sonnet 5 setting does not carry over. To get less thinking, lower effort; asking for less in the prompt does not reliably reduce it.
- `thinking: {"type": "disabled"}` returns 400. Prefer adaptive thinking at `low` effort; where a route must stay thinking-off, send `between_tools` at `high` or below with no other field in `thinking` and no per-message effort change.
- `tool_choice` `any` or `tool` returns 400; use `auto` with strict tools.
- A progress UI on adaptive thinking sets `display: "updates"` (beta, header `thinking-display-updates-2026-08-18`); `between_tools` returns the notes without it and rejects any `display` field.
- `max_tokens`: 128,000 for agentic coding per the prompting guide; the reference gives 64,000 as a starting point for long agentic coding turns (its `### Breaking change 1` subsection of the Sonnet 5.5 section, outside the behavioral-shifts range the hook names, so read that subsection too). Leave room for thinking on every route. With structured outputs, treat `stop_reason: "max_tokens"` as failed even when the text parses.
- Refusal fallback: server-side fallback retries only `cyber` and `frontier_llm`, on Sonnet 5.
