# SuperClaude Commands

Slash commands for Claude Code. Installed to `~/.claude/commands/sc/` when users run `superclaude install`.

## Available Commands

### Core Commands

| Command | Description |
|---------|-------------|
| `/sc` | Show all available SuperClaude commands |
| `/sc:help` | Get help on SuperClaude usage |
| `/sc:load` | Load context files or configurations |
| `/sc:save` | Save session state or outputs |

### Development Commands

| Command | Description |
|---------|-------------|
| `/sc:implement` | Implement features with structured workflow |
| `/sc:build` | Build and compile projects |
| `/sc:test` | Run tests with coverage analysis |
| `/sc:analyze` | Analyze code quality and patterns |
| `/sc:improve` | Suggest and apply code improvements |
| `/sc:explain` | Explain code behavior and architecture |
| `/sc:cleanup` | Clean up code, remove dead code |
| `/sc:troubleshoot` | Debug and fix issues |

### Planning & Design Commands

| Command | Description |
|---------|-------------|
| `/sc:design` | Design systems and architectures |
| `/sc:brainstorm` | Generate ideas and solutions |
| `/sc:estimate` | Estimate effort and complexity |
| `/sc:workflow` | Define and execute workflows |
| `/sc:task` | Manage development tasks |

### Research & Documentation

| Command | Description |
|---------|-------------|
| `/sc:research` | Deep web research with parallel search |
| `/sc:document` | Generate documentation |
| `/sc:index-repo` | Repository indexing for context optimization |
| `/sc:reflect` | Reflect on decisions and approaches |

### Git & Project Management

| Command | Description |
|---------|-------------|
| `/sc:git` | Git operations and workflows |
| `/sc:pm` | Project management operations |
| `/sc:spawn` | Spawn sub-agents for parallel work |

### Advisory Panels

| Command | Description |
|---------|-------------|
| `/sc:business-panel` | Business strategy advisory panel |
| `/sc:spec-panel` | Technical specification panel |

### Utility Commands

| Command | Description |
|---------|-------------|
| `/sc:agent` | Invoke specialized AI agents |
| `/sc:recommend` | Get command recommendations |
| `/sc:select-tool` | Select appropriate tools for tasks |
| `/sc:index` | Index and organize resources |

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
