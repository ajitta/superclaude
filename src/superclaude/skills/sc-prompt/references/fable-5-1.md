---
sources:
  - {file: "claude-api/shared/model-migration.md", section: "## Migrating to Claude Fable 5.1", retrieved: 2026-09-30}
  - {file: "claude-api/shared/model-migration.md", section: "## Migrating to Claude Fable 5.1 from Claude Fable 5", retrieved: 2026-09-30}
---

# Fable: 'claude-fable-5-1'

Each row compresses the reference's `### Behavioral shifts (prompt-tunable)` in both Fable sections down to direction. † = `--target api` only.

## Behavioral delta

- Verification instructions: keep only claim-grounding (report what a tool result shows). Add a fresh-context, read-only verifier with a PASS/FAIL verdict only for long autonomous builds beyond what the model solves reliably alone.
- Subagent delegation †: keep it; tell the lead to continue independent work while workers run, and to reuse a long-lived worker for follow-ups, since cache reads are cheap.
- Tool-call batching: in loops where the next reads are implied rather than named it may issue one call per turn; append the one-sentence batching nudge each turn (a turn-scoped system message on `--target api`).
- Progress updates: writes fewer updates; delete any hold-for-final line first, then add a when-and-what line only if the interface shows text between calls.
- Task completion †: pair scope discipline with "finish the whole task", and on autonomous workloads add the documented two-block autonomy text; leave it out of human-in-the-loop prompts.
- Prescriptiveness †: de-prescribe; state what to leave out (nearby fixes, extra committed test files).
- Verbosity and formatting: prose runs denser than Fable 5; define mannered prose as the anti-pattern, and remove anti-formatting rules, because it under-formats.
- Written deliverables: lead with the outcome; at `xhigh` or `max` append the single-limit note naming `max_tokens`.
- Native failure modes: early stopping, unrequested adjacent actions, one call per turn in implied loops, whole-file rewrites, over-committed tests, memory answers at `low`, unmarked quotation of sources.
- Tool use: see memory answers at `low` under native failure modes.
- Intent framing: give the reason behind the request, not just the request.
