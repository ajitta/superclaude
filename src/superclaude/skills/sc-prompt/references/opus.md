---
sources:
  - {file: "claude-api/shared/model-migration.md", section: "## Migrating to Claude Opus 5", retrieved: 2026-09-30}
  - {file: "claude-api/shared/model-migration.md", section: "## Migrating to Claude Opus 5.5", retrieved: 2026-09-30}
  - {url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5", retrieved: 2026-09-30}
  - {url: "https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5", retrieved: 2026-09-30}
  - {url: "https://platform.claude.com/docs/en/models/opus-5-5/migration-guide", retrieved: 2026-10-15}
---

# Opus: 'claude-opus-5' and 'claude-opus-5-5'

Each row compresses the reference's `### Behavioral shifts (prompt-tunable)` for Opus 5 down to direction. For 'claude-opus-5-5' each row is marked `(carried from Opus 5; not confirmed for 5.5)` and is reported as a candidate, not applied (SKILL.md), except clauses marked `(Opus 5.5 prompting guide)`, which come from that guide and the Opus 5.5 What's new page, not from the reference. Lines marked `(Opus 5.5 migration guide)` come from that page. A row marked `(--target api only)` applies only on that target.

## Behavioral delta

- Verification instructions (carried from Opus 5; not confirmed for 5.5): delete. The model self-verifies unprompted, and "double-check" causes over-verification.
- Subagent delegation (--target api only) (carried from Opus 5; not confirmed for 5.5): cap it; this model reaches for subagents readily.
- Tool-call batching (carried from Opus 5; not confirmed for 5.5): issues parallel calls as expected; no change.
- Progress updates (carried from Opus 5; not confirmed for 5.5): narrates readily; give it a cadence.
- Task completion (--target api only): pair scope discipline with "finish the whole task" (carried from Opus 5; not confirmed for 5.5). `(Opus 5.5 prompting guide)`: for 'claude-opus-5-5' on fully unattended runs, add the guide's unattended-run paragraph at the end of the system prompt, present from the session's first request, as a `[FILL: …]` slot naming 'https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5', because the paragraph is not on the machine. Leave it out of human-in-the-loop prompts.
- Prescriptiveness (--target api only) (carried from Opus 5; not confirmed for 5.5): add scope discipline; it expands task scope.
- Verbosity and formatting (carried from Opus 5; not confirmed for 5.5): a brief conciseness instruction cuts length; effort is not the lever.
- Written deliverables (carried from Opus 5; not confirmed for 5.5): calibrate file length explicitly.
- Native failure modes (carried from Opus 5; not confirmed for 5.5): scope expansion, self-correction narration.
- Tool use (carried from Opus 5; not confirmed for 5.5): no documented delta.
- Intent framing (carried from Opus 5; not confirmed for 5.5): full task specification up front in one turn.

## Request configuration: 'claude-opus-5-5', `--target api`

From the reference's `## Migrating to Claude Opus 5.5` section: its breaking changes, `### Text between tool calls comes back in thinking blocks` and `### Choosing an effort level`.

- Effort: `medium` unless a removal row sets it; `xhigh` or `max` only where "you've measured a quality gain". Changing the top-level `effort` between requests invalidates the prompt cache; a per-message effort change (beta) keeps it.
- Thinking cannot be disabled: a `disabled` or `budget_tokens` thinking setting returns 400.
- `tool_choice` `any` or `tool` returns 400; use `auto` with strict tools.
- Notes written between tool calls arrive as `thinking` blocks whose text is empty at the default display, so a harness that shows progress sets `display: "updates"` (beta, header `thinking-display-updates-2026-08-18`).
- `max_tokens`: for long agentic coding turns, emit 128,000, the model's maximum, which `(Opus 5.5 prompting guide)` says has worked well in Anthropic's testing, and name the reference's lower figure beside it: 64K "has worked well" for the same turns, in `### Breaking change 1: thinking can't be disabled`, outside the behavioral-shifts range the hook names, so read that subsection too. For other routes neither source gives a number: size it for the thinking plus the expected reply.
- Prefill `(Opus 5.5 migration guide)`: a prefilled assistant turn returns 400 on Opus 4.6 and later, 'claude-opus-5' included; use structured outputs.
- Refusals `(Opus 5.5 migration guide)`: the classifiers can decline under `reasoning_extraction`, and server-side fallback does not retry that category; the decline is returned to the caller. 'claude-opus-5' declines the same category: "As on Claude Opus 5, requests that push it to reproduce its internal reasoning in the response text may be declined with the `reasoning_extraction` category" (What's new in Claude Opus 5.5, retrieved 2026-10-15).
