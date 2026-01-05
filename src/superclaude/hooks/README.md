# SuperClaude Hooks

Event-driven automation hooks for Claude Code integration.

## Overview

Hooks allow SuperClaude to automatically execute scripts at specific points during a Claude Code session. This enables features like automatic context loading, code formatting, and session management.

## Hook Configuration

Hooks are defined in `hooks.json` and support the following events:

### Available Hook Events

| Event | Trigger | Use Case |
|-------|---------|----------|
| `SessionStart` | When Claude Code session begins | Initialize context, load preferences |
| `UserPromptSubmit` | When user submits a prompt | Activate skills, load relevant context |
| `PostToolUse` | After a tool completes | Format code, validate outputs |
| `PreToolUse` | Before a tool executes | Validation, logging |

## Current Hooks

### SessionStart

- **session_init.py**: Initializes SuperClaude context and settings

### UserPromptSubmit

- **skill_activator.py**: Activates relevant skills based on prompt content
- **context_loader.py**: Loads appropriate context files dynamically

### PostToolUse (Edit|Write)

- **prettier_hook.py**: Auto-formats code after file modifications

## Configuration Structure

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",  // Optional: regex for tool matching
        "hooks": [
          {
            "type": "command",
            "command": "python script.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### Configuration Options

| Field | Type | Description |
|-------|------|-------------|
| `matcher` | string | Regex pattern to match tool names (optional) |
| `type` | string | Hook type: `command` |
| `command` | string | Script or command to execute |
| `timeout` | number | Maximum execution time in seconds |

### Template Variables

| Variable | Description |
|----------|-------------|
| `{{SCRIPTS_PATH}}` | Path to SuperClaude scripts directory |

## For Developers

### Adding New Hooks

1. Create the script in `scripts/` directory
2. Add hook configuration to `hooks.json`
3. Test the hook in a Claude Code session
4. Update this README

### Hook Script Guidelines

- Scripts should exit with code 0 on success
- Use stderr for error messages
- Keep execution time under the timeout limit
- Scripts receive context via environment variables
