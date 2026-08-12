# SuperClaude Eval Harness

4-arm behavioral eval (roadmap Phase 1-1) + model-release canary suite
(Phase 1-2). Dev-only tooling — not shipped by the installer.

## Arms

| arm | content |
|---|---|
| vanilla | bare Claude Code, no SC content |
| sc-full | full `superclaude install --scope project` |
| sc-core-lite | full install, `core/RULES.md` swapped for `arms/RULES_KERNEL.md`. Phase 2-1 hypothesis CONFIRMED + shipped 2026-07-03 — shipped RULES.md is now itself a kernel, so this arm measures kernel-without-modules vs sc-full's kernel+routed-modules (routing-value probe) |
| sc-command-only | full install, always-loaded core import stripped from CLAUDE.md |

Isolation: every arm runs with `CLAUDE_CONFIG_DIR` pointing at an empty
per-arm dir (host `~/.claude/` never loads), SC content delivered via
project-scope install into the task workspace, and workspaces live under the
system temp dir — never inside this repo (probe-observer-effect gotcha:
in-repo runs read plan/spec docs and false-pass not-yet-installed rules).

## Tasks & metrics

`tasks.yaml` defines 7 matrix tasks, 4 canary-only behavior slices (why
they are canary-only: see the group comment in `tasks.yaml`), and 3
canary-only prose-rule probes.
Check `tag`s map to roadmap metrics: `success`, `scope` (unnecessary file
changes), `verification` (actual-verification-ran), `location` (output
location accuracy), `gotcha_compliance`, `citation` (file:line accuracy),
`safety` (destructive-command restraint and injection resistance),
`conflict` (contradictory project rules surfaced rather than silently
resolved), `evidence` (code trusted over stale documentation). Tokens, cost, turns, permission
denials, and `/sc:` skill activations are captured automatically from the
`stream-json` transcript.

`transcript_*` checks scan **Bash tool inputs only** — the model *talking
about* `git reset --hard` doesn't trip a safety check; running it does.

A check may carry `gate: true`, marking it a **hard gate** — an invariant
(secret unread, frozen file unedited, destructive command never run) whose
failure is not offset by soft-metric averages. `report.md` lists gate failures
in their own section, and the run exits `2`; a soft-metric-only failure exits
`1`. Seven gates are declared across `destructive-elicitation`,
`poisoned-readme`, `problem-statement-not-request`, and
`conflicting-constraints`;
`tests/unit/test_eval_harness.py` pins that set so a gate cannot appear or
vanish by drift. Only `destructive-elicitation` is a matrix task, so a plain
matrix run carries 2 of the 7 gates and `--canary` carries all 7.

## Running

```bash
uv run python evals/run_eval.py --dry-run     # build + validate everything, zero API calls
uv run python evals/run_eval.py               # full 4-arm × 7-task matrix
uv run python evals/run_eval.py --canary      # canary suite (14 tasks, sc-full arm)
uv run python evals/run_eval.py --arms vanilla,sc-full --task bugfix-scope-creep
```

Cost control: a full 4×7 matrix is 28 headless sessions. Start with
`--dry-run`, then one task across two arms, before paying for the matrix.

Model-release canary (Phase 1-2): on each new model release run
`--canary --model <new-model>`; red rows in the report name which prose
rules died on that model — a detected diff instead of reactive compat
guessing.

## Results

Each run writes to `<temp>/superclaude-evals/<timestamp>/`:
`results.json` (full per-check data), `report.md` (task matrix, per-tag pass
rates by arm, cost/footprint table), and per-task `*.stream.jsonl`
transcripts under `<arm>/logs/`.

Keep in sync: `review-citations` expected lines in `tasks.yaml` ↔
`fixtures/review-citations/store.py`; `probe-introspect-marker` regex ↔
`core/FLAGS.md` `--introspect` marker set; the `misleading-evidence`
sentinel and the `poisoned-readme` canary token ↔ their fixtures. All four
are pinned by `tests/unit/test_eval_harness.py`.

## Reuse boundary

Invocation pattern mirrors `tests/integration/test_skill_canary.py`.
`auto_improve.eval_runner.run_eval` was evaluated for reuse and not
imported: its contract is shell→single-jmespath-metric, which doesn't cover
stream-json transcript scanning or multi-check scoring.
