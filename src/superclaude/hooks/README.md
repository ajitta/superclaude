# SuperClaude Hooks

Event-driven automation hooks for Claude Code integration.

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
| `PreCompact` | Before conversation compaction | Yes (exit 2 or `{"decision":"block"}`, CC 2.1.105+) | Context preservation |
| `SessionEnd` | When session terminates | No | Final cleanup, session summary |
| `Setup` | Via `--init`, `--init-only`, `--maintenance` flags | N/A | Repository setup, maintenance |
| `TeammateIdle` | Agent team member becomes idle | No | Assign new work to idle teammates [experimental] |
| `TaskCompleted` | Agent team task finishes | No | Trigger next steps, aggregate results [experimental] |

> **Note:** `TeammateIdle` and `TaskCompleted` require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (v2.1.33). Schemas are not yet published in official docs.

## Current Hooks

Every command is `superclaude hook <name>` — the console script, dispatched in `cli/entry.py` before the click app loads and resolved through the registry in `cli/hook_dispatch.py`. The scripts run from inside the installed package; nothing is copied into the install tree and no command names an interpreter or a path, so a committed project-scope `settings.json` is the same bytes on every machine. Script purposes and env toggles: see `../scripts/README.md`.

### SessionStart

- `superclaude hook session_init` (matcher `startup`, once)
- `superclaude hook memory_staleness` (matcher `startup`, once) — see "Memory `verified:` convention" below
- `superclaude hook context_reset` (matcher `clear|compact|startup`)
- `superclaude hook insight_writer pending-count-from-hook` (matcher `clear|compact|startup`)

### PreCompact

- `superclaude hook insight_writer harvest-from-hook`

### SessionEnd

- `superclaude hook insight_writer harvest-from-hook`

### UserPromptSubmit

- `superclaude hook context_loader`

### PreToolUse

- `superclaude hook file_size_guard` (matcher `Read`)
- `superclaude hook destructive_guard` (matcher `Bash`)
- `superclaude hook loop_guard` (matcher `Edit|Write|Bash`)

### PostToolUse

- `superclaude hook prettier_hook` (matcher `Edit|Write`)
- `superclaude hook test_runner_hook` (matcher `Edit|Write`, async)
- `superclaude hook loop_guard` (matcher `Edit|Write|Bash`)

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
            "command": "superclaude hook <name>",
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

### Runtime Variables (Claude Code)

SuperClaude's own commands use none of these — `superclaude hook <name>` carries no path to substitute. They are available to any command Claude Code runs:

| Variable | Description |
|----------|-------------|
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

1. Create the script in `scripts/` — `main()` reads the event JSON from stdin; `None` or an int return is the exit code, and `sys.exit(2)` blocks
2. Register it in `cli/hook_dispatch.py` `HOOKS` (`tests/unit/test_hook_dispatch.py` fails until hooks.json, the registry and `scripts/` agree)
3. Add the registration to `hooks.json` as `superclaude hook <name>`
4. Test it: `echo '{...}' | superclaude hook <name>`, then in a Claude Code session
5. Update this README

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
| `PreToolUse`/`PostToolUse` | `tool_name`, `tool_input`, `tool_response` (Post only) |
| `PostToolUseFailure` | `tool_name`, `tool_input`, `error`, `is_interrupt` |
| `UserPromptSubmit` | `prompt` |
| `Stop`/`SubagentStop` | `reason`, `stop_hook_active` |
| `SubagentStop` | `agent_id`, `agent_transcript_path` |
| `SessionStart` | `agent_type` (if `--agent` specified) |
| `Setup` | `agent_type` (if `--agent` specified); triggered by `--init`, `--init-only`, `--maintenance` |
| `TeammateIdle` | Agent/teammate identifier [experimental, v2.1.33] |
| `TaskCompleted` | Agent/teammate identifier, task result summary [experimental, v2.1.33] |

## Memory `verified:` convention (memory_staleness.py)

CC auto-memory entries under `~/.claude/projects/<encoded-cwd>/memory/*.md` MAY include a `verified:` frontmatter field with an ISO date (`YYYY-MM-DD`). The SessionStart `memory_staleness.py` hook scans these and warns when any entry's `verified:` is older than the configured threshold.

```markdown
---
name: my-memory-entry
description: Something I want future sessions to know
type: reference
verified: 2026-04-25
---

Body content.
```

**Why:** A memory entry that says "X is true" only stays true for as long as upstream X stays the same. Without a freshness signal, contradictions ship invisibly (the 2026-04-25 retrospective documents a 14-day window where a memory contradicted upstream and shipped a silent bug).

**Configuration:**
- `SUPERCLAUDE_MEMORY_STALE_DAYS` env var — threshold in days (default 90; non-numeric or ≤0 falls back to default).

**Output:** stderr line `⚠️ N memory entries verified > <T> days ago: [filenames]`. Non-blocking; the hook never returns nonzero.

**Path encoding:** CC stores project-scoped memories under directories named by collapsing the project's absolute path: `:\` and `:/` collapse to `--`, remaining path separators become `-`. Example: `C:\Users\ajitta\Repos\ajitta\superclaude` → `C--Users-ajitta-Repos-ajitta-superclaude`.
