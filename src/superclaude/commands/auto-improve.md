---
description: Autonomous overnight code improvement loop driven by an objective metric (Karpathy AutoResearch pattern)
---

<component name="auto-improve" type="command">

  <role>
    /sc:auto-improve
    <mission>Run an autonomous overnight code improvement loop driven by an objective metric (Karpathy AutoResearch pattern) — mutator proposes changes, eval-cmd measures, single git lineage in an isolated worktree</mission>
  </role>

  <syntax>/sc:auto-improve [project] --eval-cmd [sh] --metric [jmespath] [--budget 8h] [--smoke-cmd sh] [--cycle-timeout 600] [--mutator-model sonnet|opus|haiku] [--scope glob] [--status] [--dry-run]</syntax>

  <flow>
  1. Parse args + validate `--eval-cmd` and `--metric` are present (unless `--status`)
  2. Phase 0 confirm: warn user that `--eval-cmd` runs unsandboxed and ask for explicit y/n confirm before spawning the worker (skip when `--status`)
  3. Spawn Python worker: `python -m superclaude.scripts.auto_improve [args]` in background; write PID to worktree
  4. Print where to follow progress (`tail -f [worktree]/results.tsv`) and exit immediately
  5. `--status` branch: read most-recent worktree's results.tsv + PID, print morning summary, exit
  </flow>

  <outputs>
| Artifact | Purpose |
|---|---|
| `[repo]/.worktrees/auto-improve-[ts]/results.tsv` | 8-column lineage (cycle_id, timestamp, commit_hash, metric_value, status, desc, tokens_used, wall_seconds) |
| `[repo]/.worktrees/auto-improve-[ts]/.git` | single git lineage of accepted mutations |
| stdout | morning summary on completion or `--status` query |
  </outputs>

  <tools>
  - Bash: spawn Python worker subprocess + read results.tsv
  - Read: spec/plan reference at start
  </tools>

  <gotchas>
  - improve-vs-auto: `/sc:improve` is the interactive variant; `/sc:auto-improve` is autonomous overnight. Confirm intent before invoking — they share tab-completion namespace
  - eval-cmd-blast-radius: `--eval-cmd` runs unsandboxed inside the worktree. Network calls, DB writes, external billing — all the user's responsibility. Do NOT pass commands that touch production resources
  - cc-session-end: the Python worker survives Claude Code session exit (it's a detached subprocess). To stop it, kill the PID listed in `[worktree]/auto_improve.pid`
  - mutator-tools: mutator agent's tool surface is restricted to Edit/Write/Read (Bash explicitly disabled) — it cannot run shell commands inside the worktree
  </gotchas>

  <examples>
  | Input | Output |
  |---|---|
  | `/sc:auto-improve . --eval-cmd 'python eval.py' --metric 'pass_rate' --budget 4h --scope 'src/**'` | 4h loop optimising pass_rate inside src/ |
  | `/sc:auto-improve . --eval-cmd 'python bench.py' --metric 'latency_p99' --budget 1h --mutator-model opus` | 1h Opus-driven latency optimisation |
  | `/sc:auto-improve . --status` | print most-recent run's summary |
  | `/sc:auto-improve . --eval-cmd 'echo {\"x\":1}' --metric 'x' --dry-run` | record baseline only, no mutations |
  </examples>

  <bounds>
    <should>autonomous overnight loop, single git lineage, isolated worktree, and objective metric only.</should>
    <avoid>mutate main repo, run unsandboxed Bash via mutator, skip Phase 0 confirm, and claim safety against external eval-cmd side effects.</avoid>
    <fallback>Ask the user when --eval-cmd or --metric is missing or ambiguous.</fallback>
  </bounds>

  <handoff next="/sc:auto-improve --status /sc:review"/>
</component>
