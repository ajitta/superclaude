# SuperClaude Scripts

Hook infra — Python + shell scripts for context loading, session mgmt, automation.

## Content Delivery

Referenced by `hooks.json`, executed by the Claude Code hook runtime — directory-role SSOT: `../ARCHITECTURE.md` §scripts/.

## Available Scripts

### Python Scripts

| Script | Purpose |
|--------|---------|
| `context_loader.py` | Dynamic context file loading — TRIGGER_MAP matching, session dedup, 8K token budget, hybrid injection |
| `session_init.py` | Session init — load SuperClaude context at startup |
| `memory_staleness.py` | SessionStart warning for auto-memory entries whose `verified:` date is stale (`SUPERCLAUDE_MEMORY_STALE_DAYS`, default 90) |
| `insight_writer.py` | Insight capture/harvest for `/sc:insight` — SessionStart pending-count, PreCompact/SessionEnd transcript harvest |
| `token_estimator.py` | Context window usage estimation |
| `prettier_hook.py` | Code formatting hook via Prettier |
| `test_runner_hook.py` | Test execution hook (`SUPERCLAUDE_AUTO_TEST=0` to disable) |
| `context_reset.py` | Reset context loader state for fresh sessions |
| `file_size_guard.py` | Blocks Read on files >30KB to save tokens (`SUPERCLAUDE_SIZE_GUARD=0` to disable) |
| `loop_guard.py` | Circuit breaker — blocks Edit/Write/Bash after 5 identical errors in 15 min (`SUPERCLAUDE_LOOP_GUARD=0` to disable) |
| `destructive_guard.py` | Blocks irreversibly destructive Bash commands (`rm -rf /`, force-push to main/master) — stdlib-only, cannot fail open on missing jq/grep |

### Subpackages

Subpackages run from the pip-installed package via `python -m superclaude.scripts.<pkg>`, not from the copied `~/.claude/superclaude/scripts/` dir.

| Package | Purpose |
|---|---|
| `auto_improve/` | Autonomous code-improvement loop — mutate/eval/report cycles in a worktree under a wall-clock budget. Entry: `python -m superclaude.scripts.auto_improve --eval-cmd ... --metric ...` (invoked by `/sc:auto-improve`). |
| `parallel_ab/` | Parallel A/B harness — runs N variants of a prompt/skill via `claude -p`, aggregates observation JSON into matrix.md + decision.md. Entry: `python -m superclaude.scripts.parallel_ab <variants.yaml>`. Env: `AB_MAX_PARALLEL` (default 8), `AB_TIMEOUT_S` (overrides per-variant timeout). |

## Related

- `hooks/hooks.json` — Hook defs referencing these scripts
- `hooks/hook_tracker.py` — Fallback session id + stale-session cleanup (`once: true` gating is CC-native)
- `modes/` — Content loaded by context_loader.py
- `mcp/` — Content loaded by context_loader.py