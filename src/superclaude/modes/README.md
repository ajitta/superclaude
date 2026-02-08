# SuperClaude Modes

Behavioral modes that shift Claude's communication style and priorities for specific contexts.

## Available Modes

| Mode | Flag | Mission |
|------|------|---------|
| Brainstorming | `--brainstorm` | Collaborative discovery for requirements exploration |
| Business Panel | `--business-panel` | Multi-expert business analysis with adaptive strategies |
| Deep Research | `--research` | Systematic investigation and evidence-based reasoning |
| Introspection | `--introspect` | Meta-cognitive analysis and reasoning optimization |
| Orchestration | `--orchestrate` | Intelligent tool selection and resource efficiency |
| Task Management | `--task-manage` | Hierarchical task organization for multi-step operations |
| Token Efficiency | `--uc` | Symbol-enhanced communication for compressed clarity |

## How Modes Work

Modes are activated via flags (see `core/FLAGS.md`) or auto-detected from context. They modify:

- **Communication style** — how information is presented
- **Priorities** — what to optimize for
- **Tool selection** — which MCPs and tools to prefer
- **Thinking depth** — how much reasoning to apply

Modes can be combined (e.g., `--research --uc` for compressed research output).

## Related

- `core/FLAGS.md` — Flag definitions and auto-detection triggers
- `agents/` — Specialized personas (modes shape behavior, agents shape expertise)
- `commands/` — Slash commands that activate modes automatically
