---
description: Autonomous overnight code improvement loop driven by objective metric (Karpathy AutoResearch pattern). Use ONLY when user explicit type `/sc:auto-improve` — run long unattended loop mutate code, implicit trigger unsafe. Do NOT auto-trigger on phrase like "improve the code", "make it better", "optimize this".
disable-model-invocation: true
---

<component name="auto-improve" type="command">

  <role command="/sc:auto-improve">
    <mission>Run autonomous overnight code improvement loop driven by objective metric (Karpathy AutoResearch pattern) — mutator propose change, eval-cmd measure, single git lineage in isolated worktree</mission>
  </role>

  <syntax>/sc:auto-improve [project] --eval-cmd [sh] --metric [jmespath] [--budget 8h] [--smoke-cmd sh] [--cycle-timeout 600] [--mutator-model sonnet|opus|haiku] [--scope glob] [--status] [--dry-run]</syntax>

  <flow>
  1. Parse args + validate `--eval-cmd` and `--metric` present (unless `--status`)
  2. Phase 0 confirm: warn user `--eval-cmd` run unsandboxed, ask explicit y/n confirm before spawn worker (skip when `--status`)
  3. Spawn Python worker: `python -m superclaude.scripts.auto_improve [args]` background; write PID to worktree
  4. Print where follow progress (`tail -f [worktree]/results.tsv`) and exit immediately
  5. `--status` branch: read most-recent worktree results.tsv + PID, print morning summary, exit
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
  - improve-vs-auto: `/sc:improve` interactive variant; `/sc:auto-improve` autonomous overnight. Confirm intent before invoke — share tab-completion namespace
  - eval-cmd-blast-radius: `--eval-cmd` run unsandboxed inside worktree. Network calls, DB writes, external billing — all user responsibility. Do NOT pass command touch production resources
  - cc-session-end: Python worker survive Claude Code session exit (detached subprocess). To stop, kill PID listed in `[worktree]/auto_improve.pid`
  - mutator-tools: mutator agent tool surface restricted to Edit/Write/Read (Bash explicitly disabled) — cannot run shell command inside worktree
  </gotchas>

  <examples>
  | Input | Output |
  |---|---|
  | `/sc:auto-improve . --eval-cmd 'python eval.py' --metric 'pass_rate' --budget 4h --scope 'src/**'` | 4h loop optimising pass_rate inside src/ |
  | `/sc:auto-improve . --eval-cmd 'python bench.py' --metric 'latency_p99' --budget 1h --mutator-model opus` | 1h Opus-driven latency optimisation |
  | `/sc:auto-improve . --status` | print most-recent run summary |
  | `/sc:auto-improve . --eval-cmd 'echo {\"x\":1}' --metric 'x' --dry-run` | record baseline only, no mutations |
  </examples>

  <bounds>
    <does>autonomous overnight loop, single git lineage, isolated worktree, objective metric only.</does>
    <never>mutate main repo, run unsandboxed Bash via mutator, skip Phase 0 confirm, claim safety against external eval-cmd side effects.</never>
    <fallback>Ask user when --eval-cmd or --metric missing or ambiguous.</fallback>
  </bounds>

  <handoff next="/sc:auto-improve --status /sc:review"/>
</component>