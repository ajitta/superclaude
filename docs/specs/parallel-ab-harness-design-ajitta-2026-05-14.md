---
status: draft
revised: 2026-05-14
---

# Parallel A/B Harness — Design

## Problem

Empirical validation of prompt/skill variants currently runs serially. The Karpathy four-axes audit read 35 command files in sequence; the `[RNN]` rename touched 48 files one by one. Both bloat main-thread context and waste wall-clock. Insights report flagged this as a quick-win target.

## Goal

Launch N (typically 4-8) parallel sub-agents, each running one variant against the same scenario, capture structured observations, and aggregate into a comparison matrix. Outcome: 10× faster A/B validation without polluting main context.

## Success Criteria

- N variants run concurrently via the `Task` tool or `claude -p` (whichever has lower per-invocation overhead on Windows).
- Each variant emits a JSON observation conforming to the schema below.
- An aggregator script merges N JSON files into a single comparison matrix written under `docs/experiments/<topic>-<date>/`.
- Main thread receives only the matrix + 1-line decision recommendation, never the raw variant outputs.

## Architecture

Orchestrator (main thread or `/sc:auto-improve` style command) → N runners (sub-agents) → 1 aggregator (Python script under `src/superclaude/scripts/`).

```
[orchestrator]
     │
     ├─→ runner-A (variant A) ─→ obs-A.json
     ├─→ runner-B (variant B) ─→ obs-B.json
     ├─→ runner-C (variant C) ─→ obs-C.json
     └─→ runner-D (variant D) ─→ obs-D.json
                                      │
                                      ▼
                              [aggregator.py]
                                      │
                                      ▼
                      docs/experiments/<topic>/matrix.md
```

## Components

### Variant spec (YAML)

```yaml
# docs/experiments/<topic>/variants.yaml
scenario:
  input: "/sc:brainstorm rate limiter for a markdown framework"
  baseline_skill: brainstorm
variants:
  - id: A
    flag: --vs
    extra_args: ""
  - id: B
    flag: --vs[k:5]
    extra_args: ""
  - id: C
    flag: --vs[k:3,tau:0.05]
    extra_args: ""
  - id: D
    flag: ""  # baseline
    extra_args: ""
runner:
  cli: "claude -p"
  model: "claude-haiku-4-5"
  timeout_seconds: 60
  bare: true                # --bare disables auto-skills load
  oauth_fallback: true      # retry without --bare if auth needs full skills
```

### Observation schema

```json
{
  "variant_id": "B",
  "exit_status": "ok",
  "tool_calls": [{"name": "Grep", "count": 3}, {"name": "Read", "count": 2}],
  "files_touched": [],
  "clarifying_questions": 1,
  "tokens": {"input": 1240, "output": 3200},
  "wall_seconds": 18.4,
  "final_output_sha256": "…",
  "axes": {
    "think_before": "explicit assumption stated",
    "simplicity": "k=5 → 5 perspectives, no extra blocks",
    "surgical": "no file edits attempted",
    "goal_driven": "criterion implicit — no test target stated"
  }
}
```

### Aggregator

`src/superclaude/scripts/ab_aggregator.py` — reads N JSON files, emits `matrix.md` with side-by-side table + Karpathy-axes scoring (3-grade) + one-line recommendation. No model call needed; pure tabulation.

## Workflow

1. Author writes `variants.yaml` under `docs/experiments/<topic>/`.
2. Orchestrator (via `Task` tool, parallel sub-agents) launches N runners with isolated env (`AB_VARIANT_ID=A`, etc.).
3. Each runner: clean `claude -p` invocation, capture stdout/stderr, write observation JSON.
4. Aggregator merges JSON → `matrix.md` + `decision.md` (1-paragraph).
5. Main thread reads only the two .md files; raw outputs stay under `experiments/`.

## Open Questions

- `claude -p --bare` auth: when `~/.claude/auth.json` is missing the `--bare` flag may fail to authenticate. Current escape hatch is conditional fallback. Worth a CLAUDE.md gotcha entry.
- Cost ceiling: 8 parallel Haiku runs at 60 s each ≈ $0.02-0.10 per experiment. Set a per-experiment cap (env var) before opening this to autonomous loops.
- `Task` tool vs `claude -p`: `Task` keeps everything in-process (lower latency, shared cache) but the variants run in *the same model* unless we use sub-agent overrides. `claude -p` truly forks; pick per-experiment based on whether the variant tests prompt content (Task) or end-to-end CLI behavior (`claude -p`).

## Out of Scope

- Live skill mutation between iterations (covered by `sc-tdd-loop-design`).
- Statistical significance testing — 4-8 runs is too few. Treat outputs as anecdotal evidence, not science.
- UI/dashboard. Matrix + decision are markdown only.

## Handoff

Once approved, drive to plan via `/sc:plan` → `docs/plans/parallel-ab-harness-plan-…`. Implementation gated on (a) variant-spec parser test, (b) aggregator unit tests, (c) one end-to-end run against `/sc:brainstorm`.
