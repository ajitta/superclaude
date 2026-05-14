# SuperClaude Scripts

Hook infra — Python + shell scripts for context loading, session mgmt, automation.

## Content Delivery

Scripts referenced by `hooks.json`, executed by Claude Code hook runtime. Not user-facing — power framework dynamic behavior behind scenes.

## Available Scripts

### Python Scripts

| Script | Purpose |
|--------|---------|
| `context_loader.py` | Dynamic context file loading — TRIGGER_MAP matching, session dedup, 8K token budget, hybrid injection |
| `session_init.py` | Session init — load SuperClaude context at startup |
| `token_estimator.py` | Context window usage estimation |
| `prettier_hook.py` | Code formatting hook via Prettier |
| `test_runner_hook.py` | Test execution hook |
| `context_reset.py` | Reset context loader state for fresh sessions |
| `file_size_guard.py` | Blocks Read on files >30KB to save tokens (`SUPERCLAUDE_SIZE_GUARD=0` to disable) |
| `loop_guard.py` | Circuit breaker — blocks Edit/Write/Bash after 5 identical errors in 15 min (`SUPERCLAUDE_LOOP_GUARD=0` to disable) |
| `parallel_ab/` | Parallel A/B harness — runs N variants of a prompt/skill via `claude -p`, aggregates observation JSON into matrix.md + decision.md. Entry: `python -m superclaude.scripts.parallel_ab <variants.yaml>`. Env: `AB_MAX_PARALLEL` (default 8), `AB_TIMEOUT_S` (overrides per-variant timeout). |

### Shell Scripts

| Script | Purpose |
|--------|---------|
| `session-init.sh` | Shell wrapper for session init |

## Key Architecture: context_loader.py

Context loader = primary on-demand delivery mechanism:
- **TRIGGER_MAP** — maps flags/keywords to content files (modes/, mcp/, core/BUSINESS_SYMBOLS)
- **Session dedup** — stops loading same content twice per session
- **8K token budget** — caps total on-demand context injection
- **Hybrid injection** — combines flag-based + keyword-based triggers

## Related

- `hooks/hooks.json` — Hook defs referencing these scripts
- `hooks/hook_tracker.py` — Session tracking for `once: true` hooks
- `modes/` — Content loaded by context_loader.py
- `mcp/` — Content loaded by context_loader.py