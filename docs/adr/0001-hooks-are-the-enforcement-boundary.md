# ADR-0001: Guarantees live in hooks, everything else is model-followed prose

- **Status:** accepted
- **Date:** 2026-08-31 (record written; the boundary has been in force since the
  guards shipped)
- **Deciders:** chosh1179 (maintainer)

## Context

Almost everything this framework ships is prose that a probabilistic model may
or may not follow. Compliance degrades in the ways the repo has already
recorded: rules from session start drift after auto-compaction, and a
differently-tuned model weights the same sentence differently — which is why the
`evals/` matrix measures behavior per arm instead of assuming it.

A subset of behaviors cannot be left to that. Reading a 30KB file destroys the
context budget for the rest of the session; `rm -rf /` and a force-push to
`master` are unrecoverable; a command that has failed identically five times
will fail a sixth. For these, "the model usually complies" is not a property
worth having.

Claude Code exposes a hook layer that runs before and after tool calls,
independent of what the model decided.

## Decision

Behavior that must hold regardless of the model's judgment is implemented as a
Claude Code hook; everything else stays prose. Three `PreToolUse` guards carry
the guarantees today:

- `file_size_guard.py` — blocks a full-file `Read` above 30KB unless the caller
  paginates (`limit`/`pages`); small and config files are exempt.
- `destructive_guard.py` — two tiers: hard-deny for irreversible commands, and
  `permissionDecision: "ask"` for reversible-but-risky ones, which prompts
  interactively and resolves to deny in headless `-p` sessions.
- `loop_guard.py` — circuit breaker; `PostToolUse` records failing call
  signatures and `PreToolUse` blocks the sixth identical failure inside a
  15-minute window.

Each guard honors a `SUPERCLAUDE_*_GUARD=0` escape hatch: the boundary is drawn
against the model's judgment, not against a human who deliberately opts out.

A new "this must never happen" requirement gets a hook and a test, not another
rule line.

## Consequences

- **Positive:** the guarantee is independent of model, model version, and
  context pressure, and it is testable — `tests/unit/test_safety_hooks.py`,
  `test_file_size_guard.py`, `test_loop_guard.py` assert it directly. Prose has
  no equivalent assertion.
- **Positive:** the always-loaded rule set stays a kernel. Because guarantees
  are not carried by repetition, `core/RULES.md` can hold four rule classes
  instead of twenty, and every session pays less context for it.
- **Negative:** hooks run on every matching tool call, and a buggy guard blocks
  legitimate work. The warn tier denies in headless mode by design, so an
  automated run can be stopped by a prompt nobody can answer.
- **Negative:** hooks are Claude Code-specific and bound to the `hooks.json`
  schema; a harness change can silently break enforcement. They also merge into
  the user's own settings, so the installer must preserve user hooks by marker
  rather than overwriting.
- **Neutral:** adding a guarantee now costs Python plus tests instead of one
  markdown line. That raised bar is the intended filter, not a side effect.

## Alternatives Considered

- **More and louder prose rules** (emphasis, repetition, restating rules in
  several files) — rejected: it decays exactly where it is needed most, after
  compaction and deep into long sessions, and every added line taxes every
  session whether or not the risk is present.
- **A wrapper CLI or proxy in front of Claude Code that filters commands** —
  rejected: it makes the framework a runtime to operate, contradicting the
  no-engine goal in `docs/PRD.md`, and duplicates a hook layer the harness
  already provides.
- **Permission allow/deny rules in `settings.json` alone** — kept for coarse
  cases, rejected as the mechanism: they match command strings without the
  state a guard can inspect, and cannot express a decision that depends on
  prior tool calls, which is precisely what `loop_guard` needs.
