# Serena MCP Installation Troubleshooting

> Canonical install reference: https://oraios.github.io/serena/02-usage/010_installation.html

## Install (canonical)

Install the `serena-agent` PyPI package via `uv tool install`:

```bash
uv tool install -p 3.13 serena-agent@latest --prerelease=allow
serena init                # default LSP backend
# or: serena init -b JetBrains  # JetBrains plugin backend
```

This places the `serena` binary on PATH so Claude Code can invoke it directly.

## Register with Claude Code

Quick setup (registers at user scope):

```bash
serena setup claude-code
```

Equivalent manual command (user scope, recommended):

```bash
claude mcp add --scope user serena -- serena start-mcp-server \
  --context claude-code --project-from-cwd
```

Per-project alternative (current directory only):

```bash
claude mcp add serena -- serena start-mcp-server \
  --context claude-code --project "$(pwd)"
```

Verify:

```bash
claude mcp list
```

## Common Issues

### "Failed to spawn: serena"

The `serena` binary is missing from PATH. Re-run the install command above. If `uv tool install` succeeded but the binary is missing, ensure `~/.local/bin` (or `uv tool dir --bin`) is on PATH.

### Migrating from old uvx-based install

Older guides used `uvx --from git+https://github.com/oraios/serena ...`. Replace with the new install:

```bash
claude mcp remove serena
uv tool install -p 3.13 serena-agent@latest --prerelease=allow
serena setup claude-code
```

### uv not found

Install `uv` first: https://docs.astral.sh/uv/getting-started/installation/

### Tool adherence drops mid-session

Recent Opus models can drop Serena's manual mid-session. Two upstream-recommended mitigations:

1. Inject the system prompt override at session start:
   ```bash
   claude --system-prompt="$(serena prompts print-cc-system-prompt-override)"
   ```
2. Install the Serena hooks (see "Optional: Serena hooks" below) for SessionStart/PreToolUse reminders.

## Optional: Serena hooks

Add to `.claude/settings.json` (project) or `~/.claude/settings.json` (user) — counteracts manual drift and auto-approves Serena tool calls:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "serena-hooks remind --client=claude-code" }] },
      { "matcher": "mcp__serena__*", "hooks": [{ "type": "command", "command": "serena-hooks auto-approve --client=claude-code" }] }
    ],
    "SessionStart": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "serena-hooks activate --client=claude-code" }] }
    ],
    "Stop": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "serena-hooks cleanup --client=claude-code" }] }
    ]
  }
}
```

The `serena-hooks` binary ships with the `serena-agent` install. Caveat: the `mcp__serena__*` PreToolUse hook auto-approves all Serena tool calls — drop that entry if you rely on permission prompts as a guardrail.

Source: https://oraios.github.io/serena/02-usage/030_clients.html

## Manual MCP config

If `claude mcp add` is unavailable, edit `~/.claude.json` directly:

```json
{
  "mcpServers": {
    "serena": {
      "command": "serena",
      "args": ["start-mcp-server", "--context", "claude-code", "--project-from-cwd"]
    }
  }
}
```

## Getting Help

1. Check upstream docs: https://oraios.github.io/serena/
2. Verify binary: `serena --version`
3. Verify uv: `uv --version`
4. Report issues: https://github.com/SuperClaude-Org/SuperClaude_Framework/issues
