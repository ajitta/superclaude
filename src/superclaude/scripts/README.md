# SuperClaude Scripts

Hook infra — Python + shell scripts for context loading, session mgmt, automation.

## Content Delivery

Run by the Claude Code hook runtime as `superclaude hook <name>` (registry: `../cli/hook_dispatch.py`), i.e. from inside the installed package — nothing here is copied into the install tree. Directory-role SSOT: `../ARCHITECTURE.md` §scripts/.

## Available Scripts

### Python Scripts

| Script | Purpose |
|--------|---------|
| `context_loader.py` | Dynamic context file loading — TRIGGER_MAP matching, session dedup, 8K token budget, hybrid injection. Dry run: `superclaude context explain "<prompt>"` |
| `session_init.py` | Session init — load SuperClaude context at startup |
| `memory_staleness.py` | SessionStart warning for auto-memory entries whose `verified:` date is stale (`SUPERCLAUDE_MEMORY_STALE_DAYS`, default 90) |
| `insight_writer.py` | Insight capture/harvest for `/sc:insight` — SessionStart pending-count, PreCompact/SessionEnd transcript harvest |
| `token_estimator.py` | Context window usage estimation |
| `prettier_hook.py` | Code formatting hook via Prettier |
| `test_runner_hook.py` | Test execution hook (`SUPERCLAUDE_AUTO_TEST=0` to disable) |
| `context_reset.py` | Reset context loader state for fresh sessions. Manual: `superclaude context reset` |
| `file_size_guard.py` | Blocks Read on files >30KB to save tokens (`SUPERCLAUDE_SIZE_GUARD=0` to disable) |
| `loop_guard.py` | Circuit breaker — blocks Edit/Write/Bash after 5 identical errors in 15 min (`SUPERCLAUDE_LOOP_GUARD=0` to disable) |
| `destructive_guard.py` | Blocks irreversibly destructive Bash commands (`rm -rf /`, force-push to main/master) — stdlib-only, cannot fail open on missing jq/grep |

### Subpackages

Subpackages import `superclaude.*`, so they resolve only under an interpreter holding the package. Invoke them through the console entries (`superclaude auto-improve`, `superclaude parallel-ab`); inside a dev checkout `uv run python -m superclaude.scripts.<pkg>` is equivalent. A bare `python -m superclaude.scripts.<pkg>` outside a checkout raises ModuleNotFoundError.

| Package | Purpose |
|---|---|
| `auto_improve/` | Autonomous code-improvement loop — mutate/eval/report cycles in a worktree under a wall-clock budget. Entry: `superclaude auto-improve --eval-cmd ... --metric ...` (invoked by `/sc:auto-improve`). |
| `parallel_ab/` | Parallel A/B harness — runs N variants of a prompt/skill via `claude -p`, aggregates observation JSON into matrix.md + decision.md. Entry: `superclaude parallel-ab <variants.yaml>`. Env: `AB_MAX_PARALLEL` (default 8), `AB_TIMEOUT_S` (overrides per-variant timeout). |

## Related

- `hooks/hooks.json` — Hook defs referencing these scripts
- `hooks/hook_tracker.py` — Fallback session id + stale-session cleanup (`once: true` gating is CC-native)
- `modes/` — Content loaded by context_loader.py
- `mcp/` — Content loaded by context_loader.py