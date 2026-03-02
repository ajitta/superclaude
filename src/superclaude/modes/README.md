# SuperClaude Modes

Behavioral modes that shift Claude's communication style and priorities for specific contexts.

## Available Modes

| Mode | Flag | File |
|------|------|------|
| Brainstorming | `--brainstorm` | `brainstorming.md` |
| Business Panel | `--business-panel` | `business-panel.md` |
| Deep Research | `--research` | `deep-research.md` |
| Introspection | `--introspect` | `introspection.md` |
| Orchestration | `--orchestrate` | `orchestration.md` |
| Task Management | `--task-manage` | `task-management.md` |
| Token Efficiency | `--token-efficient` or `--uc` | `token-efficiency.md` |

### Supporting Configuration

| File | Purpose |
|------|---------|
| `research-config.md` | Deep research strategy settings, depth profiles, and tool routing |

## How Modes Work

Modes are activated via flags (see `core/FLAGS.md`) or auto-detected from context. They modify:

- **Communication style** — how information is presented
- **Priorities** — what to optimize for
- **Tool selection** — which MCPs and tools to prefer
- **Thinking depth** — how much reasoning to apply

Modes can be combined (e.g., `--research --uc` for compressed research output).

## Injection Behavior

- **Explicit flag** (e.g., `--brainstorm`): Full `.md` file injection
- **Natural language** (e.g., "brainstorm ideas"): Compact instruction injection (saves ~30-50% tokens)
- **Exception**: `token-efficiency.md` always gets full injection (symbol table required)

## Related

- `core/FLAGS.md` — Flag definitions and auto-detection triggers
- `agents/` — Specialized personas (modes shape behavior, agents shape expertise)
- `commands/` — Slash commands that activate modes automatically
