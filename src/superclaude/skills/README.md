# SuperClaude Skills

Skills are reusable, specialized capabilities with defined behaviors, tool access, and optional hooks.

## Skill Frontmatter Reference (v2.1.0+)

```yaml
---
name: skill-name
description: Brief description shown in slash command menu
triggers: /skill-name, keyword1, keyword2
user-invocable: true              # Visible in slash command menu (default: true for /skills/)
context: inline|fork              # inline = same context, fork = sub-agent (v2.1.0+)
agent: agent-name                 # Agent type for execution (v2.1.0+)
model: haiku|sonnet|opus          # Override model for this skill (v2.1.0+)
mcp: c7:docs|tavily:search        # MCP dependencies
allowed-tools:                    # YAML list format (v2.1.0+)
  - Read
  - Grep
  - Glob
  - WebSearch
  - mcp__server__tool             # Specific MCP tool
  - mcp__server__*                # All tools from server (wildcard)
disallowed-tools:                 # Explicit tool blocking (v2.1.0+)
  - Bash

hooks:                            # Inline hooks (v2.1.0+)
  PreToolUse:
    - matcher: "Bash|Edit"        # Outer level: matcher + hooks array
      hooks:
        - type: command
          command: "python validate.py"
          once: true              # Execute only once per session
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "python format.py"
  Stop:
    - hooks:
        - type: command
          command: "python cleanup.py"
---
```

## Frontmatter Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | required | Unique skill identifier |
| `description` | string | required | Shown in command menu |
| `triggers` | string | - | Comma-separated activation keywords |
| `user-invocable` | boolean | true | Show in slash command menu |
| `context` | string | inline | `inline` or `fork` (sub-agent) |
| `agent` | string | - | Agent type for specialized behavior |
| `model` | string | inherited | Override parent model (v2.1.0+) |
| `mcp` | string | - | MCP server dependencies |
| `allowed-tools` | list | all | Whitelist of permitted tools |
| `disallowed-tools` | list | none | Blacklist of blocked tools |
| `hooks` | object | - | Inline hook definitions |

## Context Modes

### `context: inline` (default)
- Executes in the current conversation context
- Shares memory and state with parent
- Lower overhead, faster execution

### `context: fork` (v2.1.0+)
- Executes in a forked sub-agent context
- Isolated memory and state
- Can use different model
- Progress visible in parent thread
- Note: `context: fork` + `agent:` via Skill tool may not be honored (GitHub #17283)

## Skill Discovery

Skills are discovered from:
1. `~/.claude/skills/` (user-level)
2. `.claude/skills/` (project-level)
3. Nested `.claude/skills/` directories (v2.1.6+)

### Hot Reload (v2.1.0+)
Skills created or modified are immediately available without restarting the session.

## Skill vs Slash Command (v2.1.3+)

As of v2.1.3, slash commands and skills are merged:
- Skills in `/skills/` directories are visible in slash command menu by default
- Opt-out with `user-invocable: false` in frontmatter
- Skill suggestions prioritize recently/frequently used skills

## Examples

### Minimal Skill
```yaml
---
name: quick-check
description: Fast validation
user-invocable: true
---
Perform a quick validation of the current context.
```

### Full-Featured Skill
```yaml
---
name: deep-analysis
description: Comprehensive code analysis
triggers: /analyze, deep-dive, thorough-check
context: fork
agent: quality-engineer
model: opus
mcp: c7:patterns|serena:symbols
allowed-tools:
  - Read
  - Grep
  - mcp__serena__*
hooks:
  Stop:
    - hooks:
        - type: command
          command: "python summarize.py"
---
<component name="deep-analysis">
  <!-- Skill implementation -->
</component>
```

## Skill Auto-Approval (v2.1.19+)

Skills that do not define hooks or require elevated permissions are auto-approved without user confirmation. This applies to skills that only use standard tools (Read, Grep, Glob, WebSearch) and do not modify files or run shell commands.

## Argument Syntax (v2.1.19+)

Skills can accept arguments passed after the skill name:

| Syntax | Description |
|--------|-------------|
| `$ARGUMENTS` | Full argument string |
| `$ARGUMENTS[0]` | First argument (bracket syntax) |
| `$ARGUMENTS[1]` | Second argument |
| `$0` | Shorthand for `$ARGUMENTS[0]` |
| `$1` | Shorthand for `$ARGUMENTS[1]` |

Example skill using arguments:
```yaml
---
name: deploy
description: Deploy to target environment
---
Deploy $ARGUMENTS[0] to the $ARGUMENTS[1] environment.
```

Invocation: `/deploy my-app staging` → `Deploy my-app to the staging environment.`

## Session ID Access (v2.1.9+)

Skills can access the current session ID:
```
${CLAUDE_SESSION_ID}
```

This enables session-aware behavior and tracking.
