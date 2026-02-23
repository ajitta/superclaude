# Claude Code 2.1.x Changes Summary

Last updated: 2026-01-18

## Key Features by Version

### v2.1.0 (Major Release)
- **Skills**: Hot-reload, `context: fork`, `agent` field, YAML `allowed-tools`
- **Hooks**: `once: true` config, hooks in agent/skill/command frontmatter
- **Permissions**: Wildcard patterns `Bash(npm *)`, `Task(AgentName)` disabling
- **MCP**: `list_changed` notifications for dynamic tool updates
- **Settings**: `language`, `respectGitignore`
- **Env**: `IS_DEMO`, `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS`

### v2.1.2
- Security: Command injection fix in bash processing
- `agent_type` in SessionStart hook input
- `FORCE_AUTOUPDATE_PLUGINS` env var

### v2.1.3
- **Breaking**: Merged slash commands and skills
- Tool hook timeout: 60s → 10 min
- Unreachable permission rule warnings

### v2.1.4-2.1.5
- `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` env var
- `CLAUDE_CODE_TMPDIR` env var

### v2.1.6
- Nested `.claude/skills/` directory discovery
- `context_window.used_percentage` status line field
- Permission bypass security fix (shell line continuation)

### v2.1.7
- **MCP auto-mode**: Default 10% threshold, `auto:N` syntax
- `showTurnDuration` setting
- Wildcard permission security fix (shell operators)

### v2.1.9
- `plansDirectory` setting
- `PreToolUse` hooks can return `additionalContext`
- `${CLAUDE_SESSION_ID}` skill substitution

### v2.1.10
- `Setup` hook event (`--init`, `--init-only`, `--maintenance` flags)

### v2.1.11
- MCP HTTP/SSE connection fix

## SuperClaude Updates Made

1. **hooks/README.md**: Added new hook events, `once` field, template variables, frontmatter hooks
2. **mcp/MCP_INDEX.md**: Added auto_mode and list_changed sections
3. **core/FLAGS.md**: Added environment_variables, settings, permission_patterns sections
4. **skills/README.md**: Created comprehensive skill frontmatter reference

## Security Fixes to Note

- v2.1.0: Sensitive data in debug logs
- v2.1.2: Command injection in bash
- v2.1.6: Shell line continuation bypass
- v2.1.7: Wildcard rules matching shell operators
