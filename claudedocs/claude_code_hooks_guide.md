# Claude Code Hooks User Guide (SuperClaude Summary)

This document is a practical guide that combines the official documentation (Claude Code Hooks Guide/Reference) with repository implementation.
Reference: https://code.claude.com/docs/en/hooks-guide, https://code.claude.com/docs/en/hooks

## 1) Hooks Overview
Hooks are a feature that executes user-defined commands at Claude Code lifecycle events.
They are useful for **always executing** formatting, validation, prompt/permission blocking, and context injection.
Since hooks run with current user permissions, always review scripts before registration.

## 2) Configuration Location and Method
The official configuration location is the `hooks` section in `settings.json`.
- `~/.claude/settings.json` (user global)
- `.claude/settings.json` (project shared)
- `.claude/settings.local.json` (personal)

Settings can also be edited via the `/hooks` slash command.

Plugin hooks are registered through `hooks/hooks.json` in the plugin directory,
and hooks from activated plugins are **merged** with user/project hooks.

## 3) Event Types and Matcher Rules
Official event list:
`PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`,
`Notification`, `Stop`, `SubagentStop`, `PreCompact`, `SessionStart`, `SessionEnd`

Matcher application:
- **Applied**: `PreToolUse`, `PermissionRequest`, `PostToolUse`
- **Not applied**: Other events should omit `matcher`

Matchers are **case-sensitive** and support regex/wildcards (`*`).
Examples: `Edit|Write`, `Notebook.*`, `*`, `""`

## 4) Hooks Structure (Official Format)
```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "your-command-here",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

## 5) Output/Blocking Rules (Key Points)
Official Exit Code Rules:
- `0`: Success. `stdout` is visible in **verbose mode**,
  and for `UserPromptSubmit` and `SessionStart`, `stdout` is **injected into context**.
- `2`: **Block**. `stderr` message is delivered to user/Claude.
- Other: Non-blocking error. Execution continues.

Exit code 2 behavior summary:
- `PreToolUse`: Blocks tool call
- `PermissionRequest`: Denies permission request
- `UserPromptSubmit`: Stops prompt processing (prompt is cleared)
- `Stop`/`SubagentStop`: Blocks termination
- `PostToolUse`: Shows warning after already-executed tool

## 6) Prompt-Based Hooks
You can configure hooks where the LLM makes decisions using `type: "prompt"`.
According to official documentation, this works for all events and is especially useful for `Stop`/`SubagentStop`.
Input JSON is passed via `$ARGUMENTS`.

## 7) SuperClaude Default Hook Configuration
SuperClaude copies `src/superclaude/hooks/hooks.json` during installation.
During installation, `{{SCRIPTS_PATH}}` is replaced with the actual path.

Installation flow (summary):
- Script copy: `src/superclaude/scripts/` → `.claude/superclaude/scripts/`
- Hook copy: `src/superclaude/hooks/hooks.json` → `.claude/hooks/hooks.json`
- Path substitution:
  - `--scope project`: `.claude/superclaude/scripts` (relative path)
  - `--scope user`: absolute path

Default hook contents:
- `SessionStart` → `session_init.py` (session initialization)
- `UserPromptSubmit` → `skill_activator.py` (skill recommendation hints)
- `PostToolUse` (matcher: `Edit|Write`) → `prettier_hook.py` (JS/TS formatting)

Reinstall/Update:
- `superclaude install --force`
- `superclaude install --scope project --force`

## 8) Environment Variables (Representative)
- `CLAUDE_PROJECT_DIR`: Project root
- `CLAUDE_PLUGIN_ROOT`: Plugin root (used in plugin hooks)
- `CLAUDE_FILE_PATHS`: Related file paths (space-separated)
- `CLAUDE_TOOL_NAME`: Tool name
- `CLAUDE_TOOL_INPUT`: Tool input (JSON)
- `CLAUDE_TOOL_OUTPUT`: Tool output (PostToolUse only)

## 9) Operational Tips
- Check settings with `/hooks` and verify they are saved in `~/.claude/settings.json`.
- Keep timeout short to reduce delays.
- Document hook locations/rules as team standards to maintain consistency.
