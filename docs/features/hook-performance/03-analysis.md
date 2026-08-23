---
status: draft
revised: 2026-08-23
---

# Hook Performance — Measurement and Attribution

## Hook inventory

`src/superclaude/hooks/hooks.json` registers 14 hooks across 10 distinct scripts. Each
runs as `{{PYTHON_BIN}} {{SCRIPTS_PATH}}/<script>.py`, i.e. one Python process per
registration per matching event.

| Event | Matcher | Timeout | Script |
|---|---|---|---|
| SessionStart | startup | 10s | `session_init.py` |
| SessionStart | startup | 5s | `memory_staleness.py` |
| SessionStart | clear\|compact\|startup | 5s | `context_reset.py` |
| SessionStart | clear\|compact\|startup | 5s | `insight_writer.py` |
| PreCompact | * | 10s | `insight_writer.py` |
| SessionEnd | * | 10s | `insight_writer.py` |
| UserPromptSubmit | * | 5s | `context_loader.py` |
| PreToolUse | Read | 5s | `file_size_guard.py` |
| PreToolUse | Bash | 5s | `destructive_guard.py` |
| PreToolUse | Edit\|Write\|Bash | 5s | `loop_guard.py` |
| PostToolUse | Edit\|Write | 30s | `prettier_hook.py` |
| PostToolUse | Edit\|Write | 120s | `test_runner_hook.py` |
| PostToolUse | Edit\|Write\|Bash | 5s | `loop_guard.py` |
| Stop | * | 10s | `insight_writer.py` |

A single `Bash` tool call therefore spawns two SuperClaude processes: `destructive_guard`
on PreToolUse and `loop_guard` on both PreToolUse and PostToolUse — three spawns per Bash
call in total.

## Phase 0 — observation reconciliation

Two measurement sources disagreed, in both directions, so neither could be trusted until
the disagreement was explained.

### T0-1 — Per-script attribution

Session transcripts were re-aggregated on the hook record's `command` field rather than
its `hookName`. `hookName` is `event:matcher`, so it merges every hook registered on the
same event — including third-party plugin hooks — into one bucket.

| Script | Event | n | mean | p50 | p95 | max |
|---|---|---|---|---|---|---|
| `worker-service.cjs` (claude-mem) | SessionStart | 19 | 1,834.6ms | — | — | 4,751ms |
| `worker-service.cjs start` (claude-mem) | SessionStart | 19 | 1,004.1ms | — | — | 4,155ms |
| `session_init.py` | SessionStart | 14 | 848.1ms | 877 | 1,179 | 1,274ms |
| `insight_writer.py` | SessionStart | 5 | 500.6ms | — | — | 789ms |
| `context_reset.py` | SessionStart | 10 | 285.0ms | 113 | 336 | 1,268ms |
| `context_loader.py` | UserPromptSubmit | 32 | 186.2ms | 169 | 237 | 567ms |
| `stop-memory-eval.sh` (claude-mem) | Stop | 103 | 105.6ms | — | — | 316ms |
| `loop_guard.py` | PreToolUse | 1,479 | 83.2ms | 51 | 124 | 1,981ms |
| `destructive_guard.py` | PreToolUse | 1,434 | 66.8ms | 48 | 114 | 1,971ms |
| `file_size_guard.py` | PreToolUse | 86 | 55.9ms | 48 | 88 | 273ms |
| `loop_guard.py` | PostToolUse | 1,443 | 52.9ms | — | — | 2,618ms |

Three earlier figures were misattributed by the `hookName` bucketing:

- **"SessionStart 763ms, max 4,751ms"** is not SuperClaude. claude-mem's
  `worker-service.cjs` dominates that bucket at 1,834.6ms mean; SuperClaude's
  `session_init.py` is second at 848.1ms.
- **"UserPromptSubmit 41ms"** was a bucket average diluted by cheaper third-party hooks.
  `context_loader.py` alone is 186.2ms.
- **"PreToolUse:Bash 74ms"** is three hooks mixed: `loop_guard` 83.2ms +
  `destructive_guard` 66.8ms + a third-party inline shell hook at 22.2ms.

### T0-2 — Realistic-payload benchmarks

Local wall-clock, 20 runs per script, fed the stdin JSON shape Claude Code actually sends.

The first benchmark round was invalid: `context_loader.py` **deduplicates per session**,
so 19 of 20 runs sharing one `session_id` took the cheap no-output path. Re-run with a
fresh `session_id` per iteration.

| Script | Local wall-clock | Recorded p50 | Gap |
|---|---|---|---|
| `destructive_guard.py` | 24.2ms | 48ms | +24ms |
| `file_size_guard.py` | 26.5ms | 48ms | +21ms |
| `loop_guard.py` | 34.8ms | 51ms | +16ms |
| `context_loader.py` (fresh session, injecting) | 74.9ms | 169ms | **+94ms** |

### T0-3 — What `durationMs` measures

The three small guards sit a consistent **+16 to +24ms** above their local wall-clock.
That constant is the same order as a bare interpreter start (18.1ms), so `durationMs`
includes process spawn and harness overhead, not just script execution. This was settled
by inference from the existing data; registering a temporary instrumented hook was not
necessary.

`context_loader.py`'s +94ms is not explained by that constant and carries into Phase 1.

## Cost decomposition

Measured with `python -X importtime` against a bare-interpreter floor of 18.1ms
(`python -c pass`, 20 runs).

```
loop_guard.py     34.8ms = interpreter 18.1 + imports 9.0 + own logic 7.7
                           imports: json 3.9 / superclaude.utils 2.9 / tempfile 2.4

context_loader.py 74.9ms = interpreter 18.1 + imports 17.2 + own logic 39.6
                           imports: yaml 7.8 (via superclaude.hooks.inline_hooks)
                                    hook_tracker 5.3 (pulls dataclasses + inspect)
                                    difflib 3.8
```

`loop_guard.py` spends **78% of its runtime on process start and imports**; its own logic
is 7.7ms.

## Per-session cost attribution

Normalised from the 50-transcript window.

| Script | Calls/session | Cost/session | Share of SuperClaude total |
|---|---|---|---|
| `loop_guard.py` (Pre + Post) | ~58 | ~4.0s | 63% |
| `destructive_guard.py` | ~29 | ~1.9s | 30% |
| `session_init.py` | 0.28 | ~0.24s | 4% |
| `context_loader.py` | 0.64 (recorded only) | ~0.12s | 2% |
| `file_size_guard.py` | 1.7 | ~0.10s | 2% |

SuperClaude total: **~6.3s of blocking time per session.** Third-party hooks
(claude-mem `worker-service.cjs`, `stop-memory-eval.sh`, caveman) add ~1.4s.

`loop_guard.py` alone is 63% of the SuperClaude figure, because it is the only script
registered on both PreToolUse and PostToolUse for the same `Edit|Write|Bash` matcher.

## Already falsified — do not retry

- **Interpreter flags.** `python -S` (skip `site`) measures identically to a bare start
  (10ms at `/usr/bin/time` resolution, 18.1ms at loop resolution). `-S`/`-E` are not a
  lever.
- **File I/O volume.** Raising `context_loader.py`'s injection payload from 1,696 bytes
  (`--c7 --serena`) to 14,938 bytes (`--all-mcp --verbose-context`) left runtime unchanged
  at 74.3ms vs 74.9ms. Content size is not the cost driver, so "read fewer/smaller files"
  would buy nothing.

## Measurement caveats

- **Silent successes are invisible.** Claude Code does not persist a hook run that
  produced no output. `context_loader.py` shows 32 records against 144 prompts in the same
  window — the 112 non-injecting runs, roughly 55ms each, appear nowhere in the transcript
  statistics. Every transcript-derived total in this document is a floor.
- **Recorded `context_loader` runs are biased to the expensive path** for the same reason:
  only the injecting runs emit output, so its 169ms p50 describes injection, not the
  common case.
- **Third-party hooks share the buckets.** Any aggregation keyed on `hookName` mixes
  SuperClaude and plugin hooks; key on `command`.
- **Probe from outside the repo.** Behavioural probes run with `claude -p` from inside
  this repository contaminate the baseline (the probed model reads the plan documents in
  repo context). Timing probes must run outside it.

## Phase 1 — profiling

### Q1 — Does `loop_guard.py` need both registrations? Yes. Lever rejected.

The two registrations are structurally complementary, not redundant:

- **PostToolUse is the only writer.** `_handle_post()` appends an error entry when
  `tool_response` indicates failure, and clears every entry for that signature on success.
- **PreToolUse is the only enforcer.** `_handle_pre()` reads the counter and blocks when a
  signature has accumulated 5 or more errors inside the 15-minute window. It writes
  nothing.

Dropping PostToolUse means no signature is ever recorded, so PreToolUse never blocks.
Dropping PreToolUse means signatures accumulate and nothing ever acts on them. Either way
the circuit breaker stops working. **The highest-ranked lever is rejected on correctness.**

### `loop_guard.py` has no optimisable logic

Setting `SUPERCLAUDE_LOOP_GUARD=0` makes the script approve immediately, skipping all state
I/O. It measures **35.8ms** against **32.7ms** for the full enabled run — no saving, because
the env check happens after module-level imports have already run.

| Path | Local wall-clock |
|---|---|
| PreToolUse (read only) | 32.7ms |
| PostToolUse (success, writes state) | 33.8ms |
| Disabled via env (immediate approve) | 35.8ms |
| Bare interpreter floor (`python -c pass`) | 18.1ms |

Every path costs the same. **100% of `loop_guard.py`'s runtime is interpreter start plus
imports; its own logic is inside the noise.** Only reducing the number of spawned processes,
or reducing what each process imports, can move this number.

### Import cost is stdlib, not SuperClaude

`superclaude.utils` is 12.9ms cumulative but only 162µs of that is its own code. The weight
is the standard library it pulls in:

| Module | Cumulative | Needed by |
|---|---|---|
| `json` | 4.4ms | both paths (stdin parse, decision output); pulls `re` |
| `tempfile` | 3.0ms | `_save_state()` only — the PostToolUse path |
| `pathlib` | 2.4ms | path construction; `os.path` would do |
| `hashlib` | 1.1ms | `project_key()` |

Lazy-importing `tempfile` and replacing `pathlib` with `os.path` in the hot guards is worth
about 5.4ms per invocation with no behaviour change.

### Q2 — `context_loader.py`'s +94ms: two hypotheses refuted, one untestable

- **CPU contention at session start — refuted.** Splitting the 32 records by position in
  their transcript gives first-in-session 195.5ms (n=18) against later 174.2ms (n=14). The
  21ms difference does not account for a 94ms gap, and later runs are still far above the
  74.9ms local figure.
- **Prompt length — refuted.** A 4,853-character prompt measures 71.4ms against 79.8ms for
  a 32-character one. Trigger-regex scanning does not scale with prompt size here.
- **Remaining hypothesis: per-event harness overhead.** PreToolUse costs about +20ms over
  local wall-clock; UserPromptSubmit would have to cost about +95ms. Plausible, since a
  UserPromptSubmit hook's stdout is injected into the conversation rather than parsed as a
  decision. **Not testable from existing transcripts** — no trivial UserPromptSubmit hook
  exists in the window to use as a probe, and settling it would require registering an
  instrumented hook.

**Stopped here deliberately.** `context_loader.py` is roughly 3% of per-session hook cost;
the answer would not change any lever's ranking.

### Q3 — `session_init.py`'s 848ms is a network call

The script runs three subprocesses. Timed directly (5 runs each):

| Subprocess | Cost |
|---|---|
| `gh pr view --json state,reviewDecision,isDraft,url` | **552ms** |
| `git status --porcelain` | 15ms |
| `git branch --show-current` | 9ms |

`gh pr view` is a network round-trip to GitHub, executed on every session start. It is
skipped when the current branch is `main` or `master` (`get_pr_status()` returns early), so
the cost lands on feature branches only — where most work happens. The remaining ~250ms of
the 848ms mean covers interpreter start, `hook_tracker` initialisation, the multi-directory
CLAUDE.md scan, and stale-session cleanup.

### Caveat on all SessionStart figures

A trivial third-party `printf` shell hook records a **1,322.4ms mean on SessionStart**
against 22.2ms on PreToolUse and 16.1ms on PostToolUse. A hook that does nothing cannot
take 1.3 seconds of its own work, so SessionStart `durationMs` includes queueing or
serialisation behind other SessionStart hooks. **Treat every SessionStart duration in this
document as an upper bound on script work.** The `gh pr view` figure above is unaffected —
it was measured directly, not derived from transcripts.
