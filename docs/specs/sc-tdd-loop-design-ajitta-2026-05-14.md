---
status: draft
revised: 2026-05-14
---

# /sc:tdd-loop — Design

## Problem

TDD inside a Claude session is currently manual: author writes a failing test → asks Claude to fix → reads pytest output → asks for patch refinement → repeat. Each round burns context. The 1,904-passing baseline and the 9-test regression suite added during the Serena hook investigation prove the substrate is ready for an autonomous loop, but no command yet bundles the cycle.

## Goal

A `/sc:tdd-loop` command that takes a failing test (or a written spec) and iterates autonomously: run, classify failure, propose minimal patch, apply, re-run. Cap at 15 iterations; commit each green checkpoint separately so bisecting stays cheap.

## Success Criteria

- Given a single failing test, the loop drives it to green with ≥3 distinct candidate patches considered when the first patch is wrong.
- A green checkpoint produces an isolated commit with a structured message (`test(<area>): make <test_name> pass`).
- The loop halts and asks the user when: (a) iteration cap hit, (b) same test fails 3 times with different patches, (c) cross-cutting refactor would be needed (auto-escalate to Verification Level 3-4).
- All side effects respect R06 (Scope) — no nearby cleanup, no extra tests written unless the loop strictly needs them to disambiguate a failure.

## Architecture

```
[/sc:tdd-loop input_test]
        │
        ▼
   [classify failure] ──→ {missing-impl | wrong-logic | test-bug | env-issue}
        │
        ▼
   [propose minimal patch] ──→ Edit / Write
        │
        ▼
   [run affected tests first] ──→ pytest -k <test> + targeted module suite
        │
        ├─ green ──→ [run full suite] ──→ commit checkpoint ──→ next test (if multi-test input)
        └─ red   ──→ [retry budget?] ──→ yes: refine + loop / no: halt with diagnostics
```

## Components

### Failure classifier

Heuristic on pytest output. No model call required for the classifier itself; the loop just routes patch strategy by category.

| Category | Signal | Patch strategy |
|---|---|---|
| missing-impl | `AttributeError`, `ImportError`, `NameError`, `NotImplementedError` | Add the minimal symbol/file to satisfy the import or call |
| wrong-logic | `AssertionError` with expected vs actual values | Modify the implementation, not the test |
| test-bug | Test uses an API that doesn't exist on the SUT, or fixture mis-wired | Fix the test, surface to user as "test correction" |
| env-issue | `OSError`, `PermissionError`, `Failed to canonicalize`, missing dep | Halt; route to `gotchas/general.md` matchers |

### Iteration ledger

`.claude/.tdd-loop-state.json` (gitignored). Tracks per-test attempt count, last patch sha, failure category history. Enables the 3-strike halt rule without re-reading transcripts.

```json
{
  "session_id": "…",
  "tests": {
    "tests/unit/test_x.py::test_y": {
      "attempts": 2,
      "last_classification": "wrong-logic",
      "patches": ["sha1...", "sha2..."]
    }
  }
}
```

### Checkpoint commit

After each green:

```
test(<package>): make <test_name> pass

- Approach: <one-line patch summary>
- Verification: pytest tests/<…> (N passed, baseline +1)
```

Commit message constructor lives in `src/superclaude/scripts/tdd_loop/checkpoint.py`. Reuse existing Conventional Commits helper (likely `caveman-commit`).

### Halt diagnostics

When halting, emit a structured report (not a long narrative):

```
HALT reason=cap-hit | strike-3 | env-issue | escalation
test=tests/unit/test_x.py::test_y
attempts=15
last_failure_category=wrong-logic
diff_so_far=<git diff>
next_human_step=<concrete prompt>
```

## Workflow

1. User invokes `/sc:tdd-loop tests/unit/test_x.py::test_y` (single test) or `/sc:tdd-loop docs/specs/<spec>.md` (spec mode: tests-first generation).
2. Loop reads `.tdd-loop-state.json`; resumes if interrupted.
3. Runs the target test; classifies failure if red.
4. Proposes patch (Edit / Write — never a refactor). Records sha + category in ledger.
5. Re-runs affected tests; on green, runs the full suite (Verification Level 2 → 3 if any cross-package).
6. Commits checkpoint, advances to next test if list mode.
7. Halts per the success criteria above.

## Risk Mitigations

- **R06 Scope drift**: The loop must not touch files unrelated to the failing import / assertion line. Enforce via `git diff --name-only` allow-list per iteration.
- **R18 Necessity**: Every patch must be the minimal change to flip red→green. Reject "while I'm here" cleanups in pre-commit.
- **Self-modification creep**: Forbid edits to `.claude/`, `src/superclaude/skills/`, `pyproject.toml`. The loop should never rewrite its own prompt.
- **Cost cap**: Set `TDD_LOOP_MAX_TOKENS` env (default ~250K input across run). Halt if exceeded.

## Open Questions

- Should spec mode (input is a markdown spec, not a test) be in the first cut, or punted to v2? Leaning v2 — first cut takes failing tests only, since the classifier + patch path is already complex.
- How to verify a wrong-logic fix isn't a tautology? Possible mitigation: require any patch under `wrong-logic` to also touch a non-test file.
- Interaction with `SUPERCLAUDE_AUTO_SYNC` hook: a checkpoint commit may trigger a sync. Either disable the hook during the loop or accept the overhead (≈0.5 s/checkpoint).

## Out of Scope

- Multi-repo coordination.
- Generating new tests from a vague feature description (that belongs in `/sc:brainstorm` → `/sc:plan` first).
- Performance regressions — TDD loop targets correctness only. Perf work routes to `performance-engineer` agent.

## Handoff

Approval → `/sc:plan` → `docs/plans/sc-tdd-loop-plan-…`. Implementation prerequisites: failing-test fixture set in `tests/fixtures/tdd_loop/`, classifier unit tests, ledger schema validation, dry-run mode (`--no-commit`).
