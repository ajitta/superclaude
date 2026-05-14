---
status: deprecated
revised: 2026-05-15
---

# /sc:tdd-loop — Design

> **Deprecated 2026-05-15.** Parked, not built. R18 verdict: no evidence of recurring TDD-loop friction; `--loop` already owns the loop mechanics, halt, and reporting. Genuine delta is only the failure-classifier table — too thin to justify a new command + framework surface. Revisit only if a concrete recurring pain surfaces (`--loop` mis-routing a failure type, or a repeated manual checkpoint ritual). Until then: use `--loop` with explicit TDD intent.

## Problem

TDD inside a Claude session is manual: author writes a failing test → asks Claude to fix → reads pytest output → asks for patch refinement → repeat. Each round burns context. The `--loop` flag exists but is a general convergence loop — it has no TDD-specific failure routing and no per-green checkpointing.

## Goal

A `/sc:tdd-loop` command that takes a failing test and iterates autonomously: run → classify failure → propose minimal patch → apply → re-run. Commits each green checkpoint separately so bisecting stays cheap.

**v1 is a single markdown command file** — `src/superclaude/commands/sc/tdd-loop.md`. The classifier, halt rules, and checkpoint format are prompt guidance, not code. No Python scripts, no state files. This matches the content-framework architecture (markdown configures CC behavior; SuperClaude ships no runtime).

## Scope delta over `--loop`

`--loop` already covers: state success criteria → exec → self-eval → re-exec → stop on met / no-improvement / cap. `/sc:tdd-loop` adds only:

1. TDD-specific failure classification → patch-strategy routing.
2. Per-green checkpoint commit.
3. Structured halt diagnostics.

Everything else is inherited from `--loop` behavior — do not re-specify it.

## Success Criteria

- Given a single failing test, the loop drives it to green.
- When the first patch is wrong, the loop generates ≥3 distinct candidate approaches before applying the second patch (use `--vs` for candidate generation). "Distinct" = different failure-category response or different impl site — verifiable from the patch diffs.
- Each green produces an isolated commit: `test(<area>): make <test_name> pass`.
- The loop halts and asks the user when: (a) iteration cap hit, (b) same test fails 3× with different patches, (c) a cross-cutting refactor would be needed (auto-escalate to Verification Level 3-4).
- All side effects respect R06 (Scope) — no nearby cleanup, no extra tests unless strictly needed to disambiguate a failure.

## Iteration cap

Hard cap **10**. Rationale: 2× the framework `--loop` cap (5), because driving one red test to green may legitimately need more candidate patches than a general improve loop — but bounded well below the original 15 to cap worst-case cost. Not user-configurable in v1.

## Architecture

```
[/sc:tdd-loop tests/unit/test_x.py::test_y]
        │
        ▼
   [run target test] ──→ green? ──→ already passing, report + exit
        │ red
        ▼
   [classify failure] ──→ {missing-impl | wrong-logic | test-bug | env-issue}
        │
        ▼
   [propose minimal patch] ──→ Edit / Write   (env-issue → halt)
        │
        ▼
   [run affected-module suite] ──→ Verification Level 2
        │
        ├─ green ──→ commit checkpoint ──→ exit-check
        └─ red   ──→ retry budget? ──→ yes: refine (≥3 candidates) / no: halt
                                          │
                              exit-check ─┴─→ [run full suite] ──→ final report
```

Full suite runs **once, at loop exit** (Verification Level 3-4) — not per checkpoint. Per-checkpoint cost stays at the affected-module suite (~Level 2). Original design ran the full ~1,904-test suite on every green; worst case ≈13 min of pure suite runs. Rejected.

## Components

All three are prompt guidance in the command markdown — no code artifacts.

### Failure classifier

Heuristic on pytest output. Routes patch strategy by category.

| Category | Signal | Patch strategy |
|---|---|---|
| missing-impl | `AttributeError`, `ImportError`, `NameError`, `NotImplementedError` | Add the minimal symbol/file to satisfy the import or call |
| wrong-logic | `AssertionError` with expected vs actual | Modify the implementation, not the test. Do not weaken the assertion — if the assertion looks wrong, reclassify as test-bug and surface to user |
| test-bug | Test calls an API absent on the SUT, or fixture mis-wired | Fix the test, surface to user as "test correction" |
| env-issue | `OSError`, `PermissionError`, `Failed to canonicalize`, missing dep | Halt. Check `.claude/rules/gotchas/general.md` for a known match, cite it in the halt report |

### Checkpoint commit

After each green, the model writes the commit inline (reuse the `caveman-commit` skill — no constructor script):

```
test(<package>): make <test_name> pass

- Approach: <one-line patch summary>
- Verification: pytest tests/<…> (N passed, baseline +1)
```

### Halt diagnostics

On halt, emit a structured report — not a narrative:

```
HALT reason=cap-hit | strike-3 | env-issue | escalation
test=tests/unit/test_x.py::test_y
attempts=<n>
last_failure_category=<category>
diff_so_far=<git diff --stat>
next_human_step=<concrete prompt>
```

## Workflow

1. User invokes `/sc:tdd-loop tests/unit/test_x.py::test_y`. Optional `--no-commit` for dry-run (patch + verify, skip checkpoint commits).
2. Run the target test. If already green, report and exit.
3. Classify failure. `env-issue` → halt immediately.
4. Propose patch (Edit / Write — never a refactor). On a retry after red, generate ≥3 distinct candidates first.
5. Run the affected-module suite (Verification Level 2).
6. On green: commit checkpoint (unless `--no-commit`).
7. On exit (green reached or halt): run the full suite, emit final report.
8. Halt per the success criteria above.

In-session attempt tracking (count, prior categories, prior patch diffs) lives in the model's own context — the loop runs in one session. No external state file. Resume-after-interrupt is **out of scope for v1** (unproven need; revisit only if interrupted runs become common).

## Risk Mitigations

- **R06 Scope drift**: each iteration must touch only files in the failing import / assertion blast radius. Enforce by checking `git diff --name-only` against that radius before the checkpoint commit; reject and re-patch if it widens.
- **R18 Necessity**: every patch is the minimal red→green change. Reject "while I'm here" cleanups.
- **Self-modification creep**: the forbid-list is **repo-agnostic** — the loop never edits files outside the failing test's blast radius, and never edits its own command file or any `commands/`, `skills/`, `agents/` markdown in whatever repo it runs in. (The original spec hardcoded SuperClaude paths; `/sc:tdd-loop` ships to arbitrary repos, so the rule must be relative, not path-literal.)
- **Cost cap**: bounded by the 10-iteration hard cap. No token-counting env var — the model cannot reliably meter its own mid-run token use, and no enforcement mechanism exists.

## Relationship to `quality-engineer` agent

RULES.md agent routing sends `test` / `quality` work to `quality-engineer`. `/sc:tdd-loop` is the **autonomous red→green driver**; `quality-engineer` owns **test strategy / coverage / flake triage**. The command may delegate a `test-bug` classification to `quality-engineer` for a correctness opinion, but does not replace it. Resolve before `/sc:plan`: is that delegation in v1 or v2?

## Open Questions

- `test-bug` → `quality-engineer` delegation: v1 or v2?
- `SUPERCLAUDE_AUTO_SYNC` hook: a checkpoint commit may trigger a content sync (~0.5 s). Accept the overhead, or have the command suppress the hook for its duration? Leaning accept — suppression adds a moving part.

## Out of Scope (v1)

- **Spec mode** (markdown spec as input, tests-first generation) — punted to v2. The classifier + patch path is already the hard part; generating tests from a spec belongs in `/sc:brainstorm` → `/sc:plan` first.
- Resume-after-interrupt / external state file.
- Python scripts, ledger files, token-budget env vars.
- Multi-repo coordination.
- Performance regressions — TDD loop targets correctness only. Perf work routes to `performance-engineer`.

## Handoff

Approval → `/sc:plan` → `docs/plans/sc-tdd-loop-plan-…`. Implementation prerequisites: failing-test fixture set in `tests/fixtures/tdd_loop/` (to test the command's classifier behavior), `--no-commit` dry-run mode, and a decision on the `quality-engineer` delegation question above.
