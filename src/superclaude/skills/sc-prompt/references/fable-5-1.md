---
sources:
  - {file: "claude-api/shared/model-migration.md", section: "## Migrating to Claude Fable 5.1", retrieved: 2026-09-30}
  - {file: "claude-api/shared/model-migration.md", section: "## Migrating to Claude Fable 5.1 from Claude Fable 5", retrieved: 2026-09-30}
  - {url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1", retrieved: 2026-10-15}
  - {url: "https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1", retrieved: 2026-10-15}
---

# Fable: 'claude-fable-5-1'

Each row compresses the reference's `### Behavioral shifts (prompt-tunable)` in both Fable sections down to direction. A `[FILL: guide, <section>]` below means a `[FILL: …]` slot naming 'https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1' and that section heading: the text is in the Fable 5.1 prompting guide, and this file does not carry it, so the slot stays unless the reference section read this run quotes the text. A row marked `(--target api only)` applies only on that target.

## Behavioral delta

- Verification instructions: keep only claim-grounding (report what a tool result shows). Add a fresh-context, read-only verifier with a PASS/FAIL verdict only for long autonomous builds beyond what the model solves reliably alone.
- Subagent delegation (--target api only): keep it; tell the lead to continue independent work while workers run, and to reuse a long-lived worker for follow-ups, since cache reads are cheap.
- Tool-call batching: in loops where the next reads are implied rather than named it may issue one call per turn; append the guide's one-sentence batching nudge each turn as `[FILL: guide, Batch independent tool calls in agent loops]` (a turn-scoped system message on `--target api`).
- Progress updates: writes fewer updates; delete any hold-for-final line first, then add a when-and-what line only if the interface shows text between calls.
- Task completion (--target api only): pair scope discipline with "finish the whole task", and on autonomous workloads add the guide's two-block autonomy text as `[FILL: guide, Finish the whole task]`; leave it out of human-in-the-loop prompts.
- Prescriptiveness (--target api only): de-prescribe; state what to leave out (nearby fixes, extra committed test files).
- Verbosity and formatting: prose runs denser than Fable 5; define mannered prose as the anti-pattern, and remove anti-formatting rules, because it under-formats.
- Written deliverables: lead with the outcome; at `xhigh` or `max` append the guide's note on the single output limit, with the request's `max_tokens` value in it, as `[FILL: guide, Leave room for long outputs at xhigh and max effort]`.
- Native failure modes: early stopping, unrequested adjacent actions, one call per turn in implied loops, whole-file rewrites, over-committed tests, memory answers at `low`, unmarked quotation of sources.
- Tool use: see memory answers at `low` under native failure modes.
- Intent framing: give the reason behind the request, not just the request.

## Request configuration: `--target api`

From the Fable 5.1 What's new page, not the reference.

- Thinking cannot be disabled: a `disabled` or `budget_tokens` thinking setting returns 400.
- A prefilled assistant turn returns 400; use structured outputs.
