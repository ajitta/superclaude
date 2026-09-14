---
status: draft
revised: 2026-08-23
---

# Hook Performance — Improvement Plan

Derived from [03-analysis.md](./03-analysis.md). Every lever below is ranked by measured
cost share, not by how tractable it looks. Nothing here is approved for implementation;
Phase 3 requires separate sign-off.

## Levers

Ranking revised after Phase 1. The original top lever was rejected on correctness; a lever
that did not exist before profiling now leads.

| Rank | Lever | Measured saving | Verdict |
|---|---|---|---|
| 1 | Cache the `gh pr view` call in `session_init.py` | 552ms → 0.05ms per cached session start on a feature branch | **Accepted, implemented** |
| 2 | Merge `destructive_guard.py` + `loop_guard.py` into one dispatcher process on the Bash PreToolUse matcher | ~24ms per Bash call, ~0.67s/session | **Rejected at this scope** — see below |
| 3 | Defer `tempfile` past the read-only paths in `superclaude.utils` and `loop_guard.py` | 2.3ms per PreToolUse call, ~0.07s/session | **Accepted, implemented** |
| 4 | Lazy-import `difflib` and the `superclaude.hooks` re-exports | **21ms/prompt** (62.8ms → 41.4ms), ~0.06s/session | **Accepted, implemented** — saving was larger than estimated |

Lever 1 is a single blocking network round-trip and was both the largest and the cheapest
to change. Lever 2 trades the failure isolation between two safety hooks for its saving and
is held back deliberately: levers 1 and 3 together recover roughly 0.6s per session on a
feature branch with no change to that isolation.

### Lever 2 — rejected: the installer cannot retire a hook registration

Merging the two Bash guards means `hooks.json` stops shipping the standalone
`destructive_guard.py` registration. `_merge_hook_arrays()` in
`cli/install_settings.py` does not remove a SuperClaude hook that a release stops
shipping: outside `--force`, "existing entries are authoritative and stay exactly as
written", and only newly shipped hooks are appended. `superclaude install` defaults to
`force=False`.

So an existing install upgrading normally would end up with **both** the retired
standalone registration and the new merged dispatcher. `destructive_guard`'s check would
run twice per Bash call and the spawn count would go **up**, inverting the lever's purpose.
Only a `--force` install would clean it up, and end users are not required to pass it.

Making lever 2 safe therefore requires a new installer capability — retiring
SuperClaude-owned hook registrations that a release has dropped — inside the code path
whose central invariant is that it must never remove a user's own hooks. That is a larger
and far riskier change than merging two scripts, and it buys ~0.67s/session on top of the
~0.6s levers 1, 3, and 4 already delivered without touching either the installer or the
guards' failure isolation.

Rejected at this scope. If hook-registration retirement is ever built for another reason,
re-open this lever then.

### Correction — lever 3 was over-estimated

The pre-implementation estimate of ~5.4ms per invocation (~0.47s/session) assumed `pathlib`
could also be dropped and that all four hot hooks would benefit. Neither held:

- `pathlib` is imported by `superclaude.utils` for its own return types, so removing it
  from a caller saves nothing.
- `destructive_guard.py` and `file_size_guard.py` do not import `superclaude.utils` at all
  — they were already lean. Only `loop_guard.py` and `context_loader.py` pay that cost.

Measured result after implementation: PreToolUse 31.4ms → 29.1ms, PostToolUse unchanged at
31.6ms (it still writes, so it still needs `tempfile`). **2.3ms, not 5.4ms** — about one
seventh of the estimated per-session saving.

### Rejected

- **Drop one of `loop_guard.py`'s two registrations.** PostToolUse is the only writer of
  error signatures and PreToolUse is the only enforcer; removing either disables the
  circuit breaker. Rejected on correctness — see 03-analysis.md Q1.
- **Optimise `loop_guard.py`'s logic.** Running it with `SUPERCLAUDE_LOOP_GUARD=0`, which
  skips all state I/O, is not faster (35.8ms vs 32.7ms). There is no logic cost to remove.
- **Interpreter flags (`-S`, `-E`).** Measured identical to a bare start.
- **Reducing file reads or file sizes in `context_loader.py`.** A 9x payload increase
  produced no runtime change.

All four are recorded in 03-analysis.md with their measurements so they are not
re-proposed.

### Out of scope

claude-mem's `worker-service.cjs` is the single largest hook cost observed (1,834.6ms
mean, 4,751ms max — larger than the whole SuperClaude hook set per session). It is a
third-party plugin and cannot be fixed from this repository. Reported to the user as an
observation only.

## Phases

**Phase 0 — observation reconciliation. Complete.** Results in 03-analysis.md.

**Phase 1 — profiling. Complete.** Two of three questions answered, one closed as
not-worth-settling: `loop_guard.py` needs both registrations (lever rejected),
`session_init.py`'s 848ms is a `gh pr view` network call (new lever 1), and
`context_loader.py`'s +94ms lost two hypotheses without gaining an answer — pursued no
further because the script is ~3% of per-session cost.

**Phase 2 — lever decisions. Complete.** Levers 1 and 3 accepted, lever 2 deferred, lever 4
left unstarted. The PR-status call was cached rather than removed, so the banner line is
unchanged and only its freshness moves.

**Phase 3 — implementation. Levers 1 and 3 landed.**

- `session_init.py` — `get_pr_status()` caches the rendered line per branch under
  `hook_state_dir()/pr_status_<project_key>.json` with a 600s TTL. The empty result is
  cached too, so a branch with no open PR stops paying the full round-trip to learn
  nothing. Fail-open on a missing, stale, or corrupt cache file.
- `superclaude/utils/__init__.py` — `tempfile` moved into `atomic_write_json()` and
  `hashlib` into `project_key()`; a comment records why new module-level imports do not
  belong there.
- `scripts/loop_guard.py` — `tempfile` moved into `_save_state()`, which only the
  PostToolUse path calls.
- `tests/unit/test_session_init.py` — new autouse fixture pinning `CLAUDE_PROJECT_DIR` for
  `TestGetPrStatus`. See "Regression found during implementation".
- `hooks/__init__.py` — the two re-exports now resolve through a PEP 562 `__getattr__`.
  Importing any submodule of the package runs this file, so the eager re-exports made
  `context_loader.py` load `inline_hooks` -> `yaml` on every prompt for a
  `parse_frontmatter` it never calls. No caller imports these names from the package, so
  the names are kept only to preserve the documented API.
- `scripts/context_loader.py` — `difflib` moved into `resolve_flags()` and
  `resolve_command_name()`; it only serves the fuzzy-suggestion path for a misspelled flag
  or command name, which most prompts never reach. Measured 62.8ms -> 41.4ms per prompt,
  confirmed over two runs.

Lever 2 is rejected (see above) and no lever remains open.

## Success criteria

- **Phase 0.** The 74ms `PreToolUse:Bash` figure is decomposed per script and its unexplained
  portion is attributed to a named cause. "Probably process spawn" does not qualify. — met.
- **Phase 1.** Each open question has an answer backed by a measurement or by a specific
  code path, not by inference from the code's shape. — met for Q1 and Q3; Q2 closed
  unresolved with its remaining hypothesis and the reason for stopping both recorded.
- **Phase 2.** Every lever carries an accept/reject verdict, a one-line reason, and a
  saving estimate in ms/session derived from measurement.
- **Phase 3** (if it runs). Per-session blocking time re-measured against the ~6.3s
  baseline; `uv run pytest` holds at its documented baseline; no behavioural regression —
  destructive-command blocking, loop detection, and Safe Read blocking all still fire.

## Regression found during implementation

Caching made `get_pr_status()` stateful, and `TestGetPrStatus` had been written against a
stateless function. Three tests failed once the cache landed: the cases share branch names
(`feature/foo`, `feature/bar`), so a test simulating "no PR for this branch" wrote an empty
line into the cache and the draft-PR test that ran after it read that empty string back.

The suite was also writing a real `pr_status_<key>.json` into the developer's own
`.claude/.superclaude_hooks/` — the exact failure `.claude/rules/gotchas/hooks.md` records
under `test-anchor-env`, where 19 stray `loop_guard_*.json` files reached a real state
directory the same way.

Fixed with an autouse fixture that pins `CLAUDE_PROJECT_DIR` to `tmp_path` and creates the
`<tmp>/.claude/superclaude` marker, giving each test its own cache. `monkeypatch.chdir`
alone would not work: `project_root()` reads the environment variable first. Verified after
the fix that the suite leaves no state file in the real directory.

## Risks

- **Registration count is gated by a test.** `test_hook_registration_note_matches_hooks_json`
  compares `hooks.json` against the count recorded in the codex documentation. Levers 1
  and 2 both change the count of 14, so the codex doc must move with them.
- **Path resolution.** Any edit to hook scripts keeps the `superclaude.utils` resolvers
  (`project_root()`, `claude_base()`, `hook_state_dir()`). Reverting to `Path.home()` or
  `Path.cwd()` reintroduces a silent scope bug — see `.claude/rules/gotchas/hooks.md`.
- **Failure isolation.** Lever 2 merges independent hooks into one process; a crash in one
  then takes the other down. Weigh against the saving before accepting.
- **Measurement contamination.** Timing probes run from outside this repository.
