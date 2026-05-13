# SuperClaude Commands

Workflow entry points — user-facing slash commands Claude Code.

## Content Delivery

Commands managed by Claude Code native command system. Install to `~/.claude/commands/sc/` on `superclaude install`, reach as `/sc:*` slash commands.

## Available Commands

### Core

| Command | Description |
|---------|-------------|
| `/sc` | Show all SuperClaude commands |
| `/sc:help` | Help on SuperClaude usage |
| `/sc:init` | Interactive project env setup, first-session onboarding |
| `/sc:load` | Load project context via Serena MCP + auto memory |
| `/sc:save` | Persist context via Serena MCP + auto memory |

### Development

| Command | Description |
|---------|-------------|
| `/sc:implement` | Implement features, structured workflow |
| `/sc:build` | Build + compile projects |
| `/sc:test` | Run tests w/ coverage analysis |
| `/sc:analyze` | Analyze code quality + patterns |
| `/sc:improve` | Apply systematic improvements (interactive) |
| `/sc:auto-improve` | Autonomous overnight code improvement loop, objective metric (Karpathy AutoResearch pattern) |
| `/sc:explain` | Explain code behavior + architecture |
| `/sc:cleanup` | Clean code, kill dead code |
| `/sc:troubleshoot` | Debug + fix issues |

### Planning & Design

| Command | Description |
|---------|-------------|
| `/sc:design` | Design systems + architectures |
| `/sc:plan` | Detailed impl plans w/ TDD tasks |
| `/sc:brainstorm` | Interactive requirements discovery |
| `/sc:estimate` | Estimate effort + complexity |
| `/sc:workflow` | Define + execute workflows |
| `/sc:task` | Manage dev tasks |

### Research & Documentation

| Command | Description |
|---------|-------------|
| `/sc:research` | Deep web research, parallel search |
| `/sc:document` | Generate docs |
| `/sc:index-repo` | Repo indexing for context optimization |
| `/sc:reflect` | Task reflection + validation |
| `/sc:insight` | Capture session insights to JSONL for analysis |

### Git & Project Management

| Command | Description |
|---------|-------------|
| `/sc:git` | Git ops w/ smart commits + workflow |
| `/sc:review` | Code review w/ structured feedback |
| `/sc:pm` | Project Manager Agent orchestration |

### Advisory Panels

| Command | Description |
|---------|-------------|
| `/sc:business-panel` | Business strategy advisory panel |
| `/sc:spec-panel` | Tech spec panel |

### Utility

| Command | Description |
|---------|-------------|
| `/sc:agent` | Session controller — investigation, impl, review |
| `/sc:recommend` | Smart command recommendation engine |
| `/sc:select-tool` | MCP tool select via complexity scoring |
| `/sc:index` | Gen project docs + knowledge base |

## Authoring Rules

See `.claude/rules/command-authoring.md` for full authoring spec.

Validation: `uv run python -m pytest tests/unit/test_command_structure.py -v`

## Related

- `agents/` — Domain expert agents commands route to
- `modes/` — Cognitive overlays commands activate
- `skills/` — Execution containers w/ hooks + tool restrictions