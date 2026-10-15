# superclaude Commands

Workflow entry points — user-facing slash commands Claude Code.

## Content Delivery

Commands managed by Claude Code native command system. Install to `~/.claude/commands/sc/` on `superclaude install`, reach as `/sc:*` slash commands.

## Available Commands

### Core

| Command | Description |
|---------|-------------|
| `/sc:sc` | Command dispatcher — routes to other `/sc:*` commands (on request) |
| `/sc:help` | Help on superclaude usage |
| `/sc:init` | Interactive project env setup, first-session onboarding |
| `/sc:load` | Load project context via `.claude/memories/` + auto memory |
| `/sc:save` | Persist context via `.claude/memories/` + auto memory |

### Development

| Command | Description |
|---------|-------------|
| `/sc:implement` | Implement features, structured workflow |
| `/sc:build` | Build + compile projects |
| `/sc:test` | Run tests with coverage analysis |
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
| `/sc:plan` | Detailed impl plans with TDD tasks |
| `/sc:intent` | Capture a request in the requester's own words before analysis |
| `/sc:brainstorm` | Interactive requirements discovery |
| `/sc:estimate` | Estimate effort + complexity |
| `/sc:roadmap` | Generate task plan from PRD (distinct from harness Workflow tool) |
| `/sc:task` | Manage dev tasks |
| `/sc:promote-feature` | Promote standalone docs sharing a slug into a feature folder |

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
| `/sc:git` | Git ops with smart commits + workflow |
| `/sc:review` | Code review with structured feedback |
| `/sc:pm` | Multi-agent orchestration by brainstorm, direct or wave strategy (on request) |

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
| `/sc:select-tool` | MCP tool selection by task type |
| `/sc:index` | Gen project docs + knowledge base |

## Authoring Rules

See `.claude/rules/command-authoring.md` for full authoring spec.

Validation: `uv run python -m pytest tests/unit/test_command_structure.py -v`

## Related

- `agents/` — Domain expert agents commands route to
- `modes/` — Cognitive overlays commands activate
