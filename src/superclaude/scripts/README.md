# SuperClaude Scripts

Utility scripts for automation, session management, and hook integrations.

## Available Scripts

### Python Scripts

| Script | Description |
|--------|-------------|
| `session_init.py` | Initialize Claude Code session with SuperClaude context |
| `context_loader.py` | Load and merge context files dynamically |
| `skill_activator.py` | Activate skills based on task requirements |
| `prettier_hook.py` | Code formatting hook using Prettier |
| `validate_confidence_context.py` | PreToolUse confidence-check context validation hook |
| `clean_command_names.py` | Utility for cleaning/normalizing command names |

### Shell Scripts

| Script | Description |
|--------|-------------|
| `session-init.sh` | Shell wrapper for session initialization |
| `skill-activator.sh` | Shell wrapper for skill activation |

## Usage

### Session Initialization

Session scripts are automatically invoked when Claude Code starts with SuperClaude:

```bash
# Manually trigger session init (if needed)
python -m superclaude.scripts.session_init
```

### Context Loading

```python
from superclaude.scripts.context_loader import load_context

context = load_context(["agents/deep-research.md", "modes/precision.md"])
```

### Hook Integration

Scripts in this directory can be referenced in `hooks/hooks.json` for event-driven automation:

```json
{
  "PreToolUse": {
    "Bash": "python -m superclaude.scripts.prettier_hook"
  }
}
```

## For Developers

### Adding New Scripts

1. Create the script in this directory
2. Add Python entry point in `__init__.py` if needed
3. Update this README
4. If it's a hook script, register it in `hooks/hooks.json`

### Script Guidelines

- Python scripts should be importable as modules
- Shell scripts should be POSIX-compliant
- Include docstrings and usage examples
- Handle errors gracefully with clear messages
