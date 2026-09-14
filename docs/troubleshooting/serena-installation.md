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

Do not add `--mode=no-memories`: it removes Serena's memory tools (`list_memories`, `read_memory`, `write_memory`, …) and `onboarding`, which `/sc:load` and `/sc:save` use as their primary store.

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
2. Consider the Serena hooks (see "Optional: Serena hooks" below); read each entry's caveat before adding it.

## Optional: Serena hooks

Upstream's full set for Claude Code, to add to `.claude/settings.json` (project) or `~/.claude/settings.json` (user). Pick entries individually — see what each one does below:

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
    "SessionEnd": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "serena-hooks cleanup --client=claude-code" }] }
    ]
  }
}
```

The `serena-hooks` binary ships with the `serena-agent` install.

- `remind` denies the Grep or Read call that reaches its threshold since the last Serena symbolic tool call (serena-agent 1.7.0: the 3rd Grep, the 3rd code-file Read, or the 4th of the two combined; other tools neither count nor reset; at most one deny per 2 minutes). Grep counts whatever the file type, so in markdown-heavy repositories — SuperClaude itself included — it blocks searches no symbolic tool can replace and the agent falls back to shell `grep`. Leave it out for such repositories.
- `activate` tells the agent at session start to call `activate_project`. The `claude-code` context disables that tool once a project is given, so with `--project-from-cwd` the instruction cannot be followed; leave it out for that registration.
- `auto-approve` approves Serena's symbolic tools (find, insert, replace, rename and delete symbol, and similar) while Claude Code runs in `acceptEdits` or `auto` permission mode — leave it out if you rely on permission prompts as a guardrail. Memory, onboarding, diagnostics and other non-symbolic tools keep the normal approval flow, so `/sc:save` still prompts on `write_memory` unless a `mcp__serena__write_memory` allow rule covers it.
- `cleanup` deletes the per-session counters `remind` writes under `~/.serena/hook_data/`, so it is only needed alongside `remind`. It belongs on `SessionEnd`: `Stop` fires after every turn.

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
