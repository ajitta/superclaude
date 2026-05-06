---
status: draft
revised: 2026-05-06
---

# Harness-level "Expose more" follow-ups

## Context

This document tracks harness-layer follow-ups that pair with the prompt-layer fixes shipped on 2026-05-06:

- `gotchas/general.md` + `commands/agent.md` — sub-agent summary is advisory; revalidation required
- `RULES.md` R12 — bounded-proceed default; ask only for irreversible / high-blast / security
- `RULES.md` R15 + `<verification_ladder>` — 5-level verification scaling with auto-escalation triggers
- `RULES.md` `<sub_agent_decision>` — delegate packet IN schema + OUT pointer

The prompt-layer changes set policy. They do not enforce it. Karpathy's framing applies: *"LLM은 instruction을 잊는다. Harness는 잊지 않는다."* The items below move enforcement from prompt to harness for the verify-side UX axis (Generate less is already strong; Expose more is weak).

## Follow-up items

### 1. PostToolUse diff exposure

Goal: surface change scope after every Edit/Write so the user can verify in seconds, not minutes.

Sketch:
- New script `src/superclaude/scripts/diff_exposer.py`
- PostToolUse matcher `Edit|Write` (after the existing `prettier_hook.py`)
- Output to stderr: changed file path, +/- line counts, file count if batched
- Threshold warning: if a single tool call modifies >5 files OR >200 lines, flag "scope check: confirm this matches the task"
- Off-by-default for trivial cases: <10-line single-file edits stay silent

Rationale: today the user only sees the diff if they look. Karpathy's "fast verification loop" needs the diff visible without action. Pairs with R06 (Scope) and R12 (bounded-proceed surface diff).

Risk: noisy in dev loops where many small edits chain. Mitigate with the threshold-based silence.

### 2. Forbidden-path block

Goal: prevent agent from editing files outside the declared task scope.

Sketch:
- Optional task-scope manifest in `.claude/task-scope.txt` (one glob per line) declared at task start
- PreToolUse Edit|Write hook checks tool_input.file_path against the manifest
- Block with reason if outside scope; require explicit user override (touch a marker file or unset env)
- Default: no manifest → no block (backward compatible)
- Best-effort: agent declares scope in R20 success criteria and harness ratifies

Rationale: R06 (Scope) is prompt-only today. Models drift on long sessions (gotcha `compaction-drift`). Mechanical scope enforcement closes the leak the prompt cannot.

Risk: too rigid for exploratory work. Manifest must be opt-in, and "set scope: src/auth/**" should be a one-liner, not a ceremony.

### 3. Sub-agent evidence schema validation

Goal: the new `gotchas` rule says the summary "must cite {files inspected, commands run, evidence, assumptions, risks}". Today this is honor-system. Mechanize it.

Sketch:
- Update `src/superclaude/scripts/` with `subagent_evidence_check.py`
- Hook on SubagentStop (or PostToolUse Task) — inspect the agent's final message
- Required fields: `files_inspected`, `commands_run`, `evidence` (file:line citations), `assumptions`, `residual_risks`
- If any required field is missing, append a system reminder asking the main agent to request the missing fields from the sub-agent (or to revalidate manually before acting)
- Soft enforcement (reminder, not block) to avoid breaking when sub-agent legitimately has nothing to report in a field

Rationale: pairs the prompt-level revalidation rule with a structural check. Without the schema gate, "advisory" decays back to "trust by habit" within a few sessions.

Risk: false positives on simple delegations where most fields are empty. Mitigate by allowing explicit "n/a" values.

## Sequencing

Recommended order — each builds on the previous:

1. **Diff exposure** first — lowest risk, highest UX payoff, no opt-in needed.
2. **Evidence schema** second — depends on the prompt-layer rule already shipped today; harness-side is a 2-3 day add.
3. **Forbidden-path block** last — most disruptive; needs the diff-exposure + scope-declaration UX in place so users have a way to see when the block is right vs. wrong.

## Success criteria

- Diff exposure: PostToolUse Edit/Write emits one-line diff summary in <50ms; threshold warning fires on >5 files or >200 lines; verified by integration test that asserts hook output shape.
- Forbidden-path: hook blocks an Edit outside `.claude/task-scope.txt` with a clear reason; allows Edit when no manifest is present; verified by `tests/integration/test_scope_block.py`.
- Evidence schema: SubagentStop hook detects missing required field and emits a system reminder; verified by fixture sub-agent output that omits `evidence` field.

## Out of scope

- Replacing R15 with a tool-only check (the prompt-level ladder remains primary; harness only exposes evidence)
- Diff exposure for non-Edit tools (Bash, NotebookEdit) — leave to a later iteration
- Cross-session task-scope persistence — start with per-session manifests
