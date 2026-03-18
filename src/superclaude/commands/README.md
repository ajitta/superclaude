# SuperClaude Commands

Workflow entry points — user-facing slash commands for Claude Code.

## Content Delivery

Commands are managed by Claude Code's native command system. Installed to `~/.claude/commands/sc/` on `superclaude install`, accessible as `/sc:*` slash commands.

## Available Commands

### Core

| Command | Description |
|---------|-------------|
| `/sc` | Show all available SuperClaude commands |
| `/sc:help` | Get help on SuperClaude usage |
| `/sc:init` | Interactive project environment setup for first-session onboarding |
| `/sc:load` | Load project context via Serena MCP + auto memory |
| `/sc:save` | Persist context via Serena MCP + auto memory |

### Development

| Command | Description |
|---------|-------------|
| `/sc:implement` | Implement features with structured workflow |
| `/sc:build` | Build and compile projects |
| `/sc:test` | Run tests with coverage analysis |
| `/sc:analyze` | Analyze code quality and patterns |
| `/sc:improve` | Apply systematic improvements |
| `/sc:explain` | Explain code behavior and architecture |
| `/sc:cleanup` | Clean up code, remove dead code |
| `/sc:troubleshoot` | Debug and fix issues |

### Planning & Design

| Command | Description |
|---------|-------------|
| `/sc:design` | Design systems and architectures |
| `/sc:plan` | Create detailed implementation plans with TDD tasks |
| `/sc:brainstorm` | Interactive requirements discovery |
| `/sc:estimate` | Estimate effort and complexity |
| `/sc:workflow` | Define and execute workflows |
| `/sc:task` | Manage development tasks |

### Research & Documentation

| Command | Description |
|---------|-------------|
| `/sc:research` | Deep web research with parallel search |
| `/sc:document` | Generate documentation |
| `/sc:index-repo` | Repository indexing for context optimization |
| `/sc:reflect` | Task reflection and validation |

### Git & Project Management

| Command | Description |
|---------|-------------|
| `/sc:git` | Git operations with intelligent commits and workflow |
| `/sc:review` | Code review with structured feedback |
| `/sc:pm` | Project Manager Agent orchestration |
| `/sc:spawn` | Meta-system task orchestration with delegation |

### Advisory Panels

| Command | Description |
|---------|-------------|
| `/sc:business-panel` | Business strategy advisory panel |
| `/sc:spec-panel` | Technical specification panel |

### Utility

| Command | Description |
|---------|-------------|
| `/sc:agent` | Session controller for investigation, implementation, review |
| `/sc:recommend` | Intelligent command recommendation engine |
| `/sc:select-tool` | MCP tool selection based on complexity scoring |
| `/sc:index` | Generate project documentation and knowledge base |

## Authoring Rules

See `.claude/rules/command-authoring.md` for the complete authoring specification.

Validation: `uv run python -m pytest tests/unit/test_command_structure.py -v`

## Related

- `agents/` — Domain personas that commands route to
- `modes/` — Cognitive overlays activated by commands
- `skills/` — Execution containers with hooks and tool restrictions
