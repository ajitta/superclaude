# SuperClaude Scripts

Hook infrastructure — Python and shell scripts for context loading, session management, and automation.

## Content Delivery

Scripts are referenced by `hooks.json` and executed by Claude Code's hook runtime. They are not user-facing — they power the framework's dynamic behavior behind the scenes.

## Available Scripts

### Python Scripts

| Script | Purpose |
|--------|---------|
| `context_loader.py` | Dynamic context file loading — TRIGGER_MAP matching, session dedup, 8K token budget, hybrid injection |
| `session_init.py` | Session initialization — load SuperClaude context at startup |
| `skill_activator.py` | Task-aware skill activation based on context |
| `skill_watcher.py` | Watch for skill file changes (hot reload) |
| `token_estimator.py` | Context window usage estimation |
| `prettier_hook.py` | Code formatting hook using Prettier |
| `test_runner_hook.py` | Test execution hook |
| `clean_command_names.py` | Utility for cleaning/normalizing command names |
| `context_reset.py` | Reset context loader state for fresh sessions |

### Shell Scripts

| Script | Purpose |
|--------|---------|
| `session-init.sh` | Shell wrapper for session initialization |
| `skill-activator.sh` | Shell wrapper for skill activation |

## Key Architecture: context_loader.py

The context loader is the primary on-demand delivery mechanism:
- **TRIGGER_MAP** — maps flags/keywords to content files (modes/, mcp/, core/BUSINESS_SYMBOLS)
- **Session dedup** — prevents loading the same content twice per session
- **8K token budget** — limits total on-demand context injection
- **Hybrid injection** — combines flag-based and keyword-based triggers

## Related

- `hooks/hooks.json` — Hook definitions that reference these scripts
- `hooks/hook_tracker.py` — Session tracking for `once: true` hooks
- `modes/` — Content loaded by context_loader.py
- `mcp/` — Content loaded by context_loader.py
