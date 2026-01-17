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
| `PreToolUse` | Before a tool executes | Validation, logging, input modification |
| `Stop` | When session ends | Cleanup, state persistence |
| `SubagentStop` | When a subagent completes | Subagent result handling |
| `Setup` | Via `--init`, `--init-only`, `--maintenance` flags | Repository setup, maintenance |
| `PreCompact` | Before conversation compaction | Context preservation |
| `PermissionRequest` | Tool permission requested | Auto-approve/deny logic |
| `Notification` | Idle/completion notifications | Custom alerts |

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
| `timeout` | number | Maximum execution time (default: 10 min since v2.1.3) |
| `once` | boolean | Execute only once per session (v2.1.0+) |

### Template Variables

| Variable | Description |
|----------|-------------|
| `{{SCRIPTS_PATH}}` | Path to SuperClaude scripts directory |
| `${CLAUDE_SESSION_ID}` | Current session ID (v2.1.9+) |
| `${CLAUDE_PROJECT_DIR}` | Project directory path (v1.0.58+) |
| `${CLAUDE_PLUGIN_ROOT}` | Plugin root directory (for plugins) |

## Hook Frontmatter (v2.1.0+)

Skills, agents, and slash commands can define inline hooks:

```yaml
---
hooks:
  PreToolUse:
    - matcher: "Bash"
      command: "python validate.py"
  PostToolUse:
    - matcher: "Edit|Write"
      command: "python format.py"
  Stop:
    - command: "python cleanup.py"
---
```

### PreToolUse Return Values

PreToolUse hooks can return JSON to modify behavior:

```json
{
  "decision": "allow|deny|ask",
  "updatedInput": { "modified": "tool inputs" },
  "additionalContext": "Context injected to model (v2.1.9+)"
}
```

### SessionStart Input Fields (v2.1.2+)

```json
{
  "agent_type": "agent-name",  // If --agent specified
  "hook_event_name": "SessionStart"
}
```

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
