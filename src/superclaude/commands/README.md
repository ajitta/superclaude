# SuperClaude Commands

Slash commands for Claude Code. Installed to `~/.claude/commands/sc/` when users run `superclaude install`.

## Available Commands

### Core Commands

| Command | Description |
|---------|-------------|
| `/sc` | Show all available SuperClaude commands |
| `/help` | Get help on SuperClaude usage |
| `/load` | Load context files or configurations |
| `/save` | Save session state or outputs |

### Development Commands

| Command | Description |
|---------|-------------|
| `/implement` | Implement features with structured workflow |
| `/build` | Build and compile projects |
| `/test` | Run tests with coverage analysis |
| `/analyze` | Analyze code quality and patterns |
| `/improve` | Suggest and apply code improvements |
| `/explain` | Explain code behavior and architecture |
| `/cleanup` | Clean up code, remove dead code |
| `/troubleshoot` | Debug and fix issues |

### Planning & Design Commands

| Command | Description |
|---------|-------------|
| `/design` | Design systems and architectures |
| `/brainstorm` | Generate ideas and solutions |
| `/estimate` | Estimate effort and complexity |
| `/workflow` | Define and execute workflows |
| `/task` | Manage development tasks |

### Research & Documentation

| Command | Description |
|---------|-------------|
| `/research` | Deep web research with parallel search |
| `/document` | Generate documentation |
| `/index-repo` | Repository indexing for context optimization |
| `/reflect` | Reflect on decisions and approaches |

### Git & Project Management

| Command | Description |
|---------|-------------|
| `/git` | Git operations and workflows |
| `/pm` | Project management operations |
| `/spawn` | Spawn sub-agents for parallel work |

### Advisory Panels

| Command | Description |
|---------|-------------|
| `/business-panel` | Business strategy advisory panel |
| `/spec-panel` | Technical specification panel |

### Utility Commands

| Command | Description |
|---------|-------------|
| `/agent` | Invoke specialized AI agents |
| `/recommend` | Get command recommendations |
| `/select-tool` | Select appropriate tools for tasks |
| `/index` | Index and organize resources |

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
