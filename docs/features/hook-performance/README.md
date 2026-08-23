---
feature: hook-performance
phase: planning
owner: chosh1179
created: 2026-08-23
updated: 2026-08-23
---

# Hook Performance

Every SuperClaude hook runs as a blocking subprocess in the Claude Code loop, so its cost
is paid on every tool call, prompt, or session start that matches its event. This feature
measures where that time actually goes and derives improvement levers from the measurement
rather than from the shape of the code.

The work is split into phases. Phase 0 (complete) reconciled two disagreeing measurement
sources and reassigned the cost to the right scripts; three figures reported before that
reconciliation turned out to be misattributed. Phase 1 profiled the scripts Phase 0
identified as dominant and read the algorithms behind them. Phase 2 converted the profile into accept/reject decisions per
lever, and Phase 3 implemented the two that were accepted.

## Scope of evidence

| Source | Volume | Window |
|---|---|---|
| `~/.claude/projects/**/*.jsonl` hook attachment records | 5,300 records across 50 transcripts | 2026-08-21 → 2026-08-23 |
| Local wall-clock benchmarks (20 runs each, realistic stdin payloads) | 5 scripts | 2026-08-23 |
| `python -X importtime` module profiles | 4 scripts | 2026-08-23 |
| Direct subprocess timing (`git`, `gh`) | 3 commands | 2026-08-23 |
| `src/superclaude/hooks/hooks.json` | 14 registrations / 10 scripts | 2026-08-23 |

Transcripts only retain hook runs that produced output — a successful run with empty
output is never persisted. Any figure derived from them is a floor, not a total. See
[03-analysis.md](./03-analysis.md) "Measurement caveats".

## Documents

- [03-analysis.md](./03-analysis.md) — baseline measurements, Phase 0 reconciliation, cost attribution
- [05-plan.md](./05-plan.md) — levers, phase gates, success criteria, risks

## Status

- Phase 0 (observation reconciliation) — complete
- Phase 1 (profiling) — complete
- Phase 2 (lever decisions) — complete
- Phase 3 (implementation) — levers 1 and 3 landed; lever 2 deferred, lever 4 unstarted

Phase 1 rejected the lever Phase 0 had ranked first and surfaced a larger one that
profiling alone could reveal: a `gh pr view` network round-trip inside `session_init.py`,
552ms on every session start on a feature branch. That call is now cached per branch, and
`tempfile` no longer loads on the read-only hook paths. Measured together: about 0.6s per
session start on a feature branch, with the safety hooks left independent.
