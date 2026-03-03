# SuperClaude Commands

Slash commands for Claude Code. Installed to `~/.claude/commands/sc/` when users run `superclaude install`.

## Available Commands

### Core Commands

| Command | Description |
|---------|-------------|
| `/sc` | Show all available SuperClaude commands |
| `/sc:help` | Get help on SuperClaude usage |
| `/sc:load` | Session lifecycle: load project context via Serena MCP + auto memory |
| `/sc:save` | Session lifecycle: persist context via Serena MCP + auto memory |

### Development Commands

| Command | Description |
|---------|-------------|
| `/sc:implement` | Implement features with structured workflow |
| `/sc:analyze` | Analyze code quality and patterns |
| `/sc:improve` | Apply systematic improvements to quality, performance, and maintainability |
| `/sc:explain` | Explain code behavior and architecture |

### Planning & Design Commands

| Command | Description |
|---------|-------------|
| `/sc:brainstorm` | Interactive requirements discovery through Socratic dialogue |
| `/sc:workflow` | Define and execute workflows |
| `/sc:task` | Manage development tasks |

### Research & Documentation

| Command | Description |
|---------|-------------|
| `/sc:research` | Deep web research with parallel search |
| `/sc:index-repo` | Repository indexing for context optimization |
| `/sc:reflect` | Task reflection and validation using Serena MCP analysis |

### Git & Project Management

| Command | Description |
|---------|-------------|
| `/sc:pm` | Project Manager Agent: orchestrate sub-agents and manage workflows |
| `/sc:spawn` | Meta-system task orchestration with intelligent breakdown and delegation |

### Migrated to Skills

The following were migrated from commands to skills (auto-triggering, hooks, tool restrictions):

| Skill | Description |
|-------|-------------|
| `sc-build` | Build, compile, package with error handling |
| `sc-cleanup` | Dead code removal + structure optimization |
| `sc-design` | System architecture + API design |
| `sc-document` | Focused documentation generation |
| `sc-estimate` | Development time/effort estimates |
| `sc-git` | Intelligent git operations + PR integration |
| `sc-test` | Test execution + coverage analysis |
| `sc-troubleshoot` | Issue diagnosis + resolution |

### Advisory Panels

| Command | Description |
|---------|-------------|
| `/sc:business-panel` | Business strategy advisory panel |
| `/sc:spec-panel` | Technical specification panel |

### Utility Commands

| Command | Description |
|---------|-------------|
| `/sc:agent` | Session controller orchestrating investigation, implementation, and review |
| `/sc:recommend` | Intelligent command recommendation engine for optimal command selection |
| `/sc:select-tool` | Intelligent MCP tool selection based on complexity scoring |
| `/sc:index` | Generate comprehensive project documentation and knowledge base |

## Usage

Commands are invoked in Claude Code with the `/sc:` prefix:

```
/sc:implement Add user authentication
/sc:test --coverage
/sc:research "best practices for API design"
```

## For Developers

### File Location

- **Source**: `src/superclaude/commands/`
- **Installed to**: `~/.claude/commands/sc/`

### Adding New Commands

1. Create a new `.md` file in this directory
2. Follow the existing command structure
3. Update this README with the new command
4. Test with `superclaude install` and verify in Claude Code

### Command File Structure

Each command file should include:
- Clear description of the command's purpose
- Parameter definitions (if any)
- Execution workflow
- Output format expectations
