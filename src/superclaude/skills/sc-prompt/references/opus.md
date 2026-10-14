---
sources:
  - {file: "claude-api/shared/model-migration.md", section: "## Migrating to Claude Opus 5", retrieved: 2026-09-30}
  - {file: "claude-api/shared/model-migration.md", section: "## Migrating to Claude Opus 5.5", retrieved: 2026-09-30}
  - {url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5", retrieved: 2026-09-30}
  - {url: "https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5", retrieved: 2026-09-30}
---

# Opus: 'claude-opus-5' and 'claude-opus-5-5'

Each row compresses the reference's `### Behavioral shifts (prompt-tunable)` for Opus 5 down to direction and carries it to 'claude-opus-5-5' unless a clause says otherwise. Text marked `(Opus 5.5 prompting guide)` comes from that guide and the Opus 5.5 What's new page, not from the reference. † = `--target api` only.

## Behavioral delta

- Verification instructions: delete. The model self-verifies unprompted, and "double-check" causes over-verification.
- Subagent delegation †: cap it; this model reaches for subagents readily.
- Tool-call batching: issues parallel calls as expected; no change.
- Progress updates: narrates readily; give it a cadence.
- Task completion †: pair scope discipline with "finish the whole task". `(Opus 5.5 prompting guide)`: for 'claude-opus-5-5' on fully unattended runs, add the guide's unattended-run paragraph at the end of the system prompt, present from the session's first request, as a `[FILL: …]` slot naming 'https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5', because the paragraph is not on the machine. Leave it out of human-in-the-loop prompts.
- Prescriptiveness †: add scope discipline; it expands task scope.
- Verbosity and formatting: a brief conciseness instruction cuts length; effort is not the lever.
- Written deliverables: calibrate file length explicitly.
- Native failure modes: scope expansion, self-correction narration.
- Tool use: no documented delta.
- Intent framing: full task specification up front in one turn.

## Request configuration: 'claude-opus-5-5', `--target api`

From the reference's `## Migrating to Claude Opus 5.5` section: its breaking changes, `### Text between tool calls comes back in thinking blocks` and `### Choosing an effort level`.

- Effort: `medium` unless a removal row sets it; `xhigh` or `max` only where "you've measured a quality gain". Changing the top-level `effort` between requests invalidates the prompt cache; a per-message effort change (beta) keeps it.
- Thinking cannot be disabled: a `disabled` or `budget_tokens` thinking setting returns 400.
- `tool_choice` `any` or `tool` returns 400; use `auto` with strict tools.
- Notes written between tool calls arrive as `thinking` blocks whose text is empty at the default display, so a harness that shows progress sets `display: "updates"` (beta, header `thinking-display-updates-2026-08-18`).
- `max_tokens`: the reference says 64K "has worked well" for long agentic coding turns, in `### Breaking change 1: thinking can't be disabled`, outside the behavioral-shifts range the hook names, so read that subsection too. `(Opus 5.5 prompting guide)`: 128,000.
