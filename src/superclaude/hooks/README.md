# SuperClaude Hooks

Event-driven automation hooks for Claude Code integration.

## Overview

Hooks allow SuperClaude to automatically execute scripts at specific points during a Claude Code session. This enables features like automatic context loading, code formatting, and session management.

## Hook Configuration

Hooks are defined in `hooks.json` and support the following events:

### Available Hook Events

| Event | Trigger | Can Block? | Use Case |
|-------|---------|------------|----------|
| `SessionStart` | When Claude Code session begins | No | Initialize context, load preferences |
| `UserPromptSubmit` | When user submits a prompt | No | Activate skills, load relevant context |
| `PreToolUse` | Before a tool executes | Yes (exit 2) | Validation, logging, input modification |
| `PermissionRequest` | Tool permission requested | Yes (exit 2) | Auto-approve/deny logic |
| `PostToolUse` | After a tool succeeds | No | Format code, validate outputs |
| `PostToolUseFailure` | After a tool fails | No | Error handling, retry logic |
| `Notification` | Idle/completion notifications | No | Custom alerts |
| `SubagentStart` | When a subagent spawns | No | Subagent initialization |
| `SubagentStop` | When a subagent completes | No | Subagent result handling |
| `Stop` | When Claude finishes responding | No | Cleanup, state persistence |
| `PreCompact` | Before conversation compaction | No | Context preservation |
| `SessionEnd` | When session terminates | No | Final cleanup, session summary |
| `Setup` | Via `--init`, `--init-only`, `--maintenance` flags | N/A | Repository setup, maintenance |

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
| `type` | string | Hook type: `command`, `prompt` (LLM-evaluated), or `agent` (plugins only) |
| `command` | string | Script or command to execute |
| `timeout` | number | Maximum execution time (default: 10 min since v2.1.3) |
| `once` | boolean | Execute only once per session (v2.1.20+) |

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
      hooks:
        - type: command
          command: "python validate.py"
          timeout: 30
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "python format.py"
  Stop:
    - hooks:
        - type: command
          command: "python cleanup.py"
---
```

**Supported frontmatter events:** Only `PreToolUse`, `PostToolUse`, and `Stop` can be used in frontmatter hooks. All other events require `settings.json` or plugin `hooks.json`.

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

### Exit Codes

| Code | Meaning | Effect |
|------|---------|--------|
| 0 | Success | Allow tool execution (PreToolUse), continue normally |
| 2 | Block | Block tool execution with stderr as reason (PreToolUse/PermissionRequest only) |
| Other | Error | Logged but does not block execution |

### Environment Variables

| Variable | Scope | Description |
|----------|-------|-------------|
| `$CLAUDE_PROJECT_DIR` | All events | Project root directory |
| `$CLAUDE_PLUGIN_ROOT` | Plugins only | Plugin installation directory |
| `$CLAUDE_ENV_FILE` | SessionStart | Write env vars here to persist them |
| `$CLAUDE_CODE_REMOTE` | All events | Set if running in remote context |
| `$TOOL_NAME` | Tool events | Current tool name |
| `$TOOL_INPUT` | Tool events | Tool input (JSON) |

### Stdin JSON Input

Hook scripts receive JSON via stdin with common and event-specific fields:

**Common fields (all events):**
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/dir",
  "permission_mode": "default|plan|acceptEdits|dontAsk|bypassPermissions",
  "hook_event_name": "PreToolUse"
}
```

**Event-specific fields:**

| Event | Additional Fields |
|-------|-------------------|
| `PreToolUse`/`PostToolUse` | `tool_name`, `tool_input`, `tool_result` (Post only) |
| `PostToolUseFailure` | `tool_name`, `tool_input`, `error`, `is_interrupt` |
| `UserPromptSubmit` | `user_prompt` |
| `Stop`/`SubagentStop` | `reason`, `stop_hook_active` |
| `SubagentStop` | `agent_id`, `agent_transcript_path` |
| `SessionStart` | `agent_type` (if `--agent` specified) |

### Hook Script Guidelines

- Scripts should exit with code 0 on success (or code 2 to block in PreToolUse/PermissionRequest)
- Use stderr for error/block messages
- Keep execution time under the timeout limit
- Scripts receive context via environment variables and stdin (JSON)
