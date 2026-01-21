# Claude Code Rules & Configuration: Comprehensive Research Report

**Research Date:** 2025-01-21
**Depth Level:** Exhaustive (--ultrathink)
**Confidence Score:** 92%

---

## Executive Summary

Claude Code's rules and configuration system provides a hierarchical, flexible framework for customizing Claude's behavior across personal, project, and enterprise contexts. The system comprises two primary components:

1. **Memory Files (CLAUDE.md)**: Markdown-based instructions and context loaded at startup
2. **Settings Files (settings.json)**: JSON-based configuration for permissions, hooks, and tool behavior

Key insights from this research:
- Memory files cascade from enterprise → user → project → local scope
- Permission rules use Allow/Ask/Deny precedence with wildcard pattern support
- The hooks system provides complete lifecycle control with 6 event types
- Modular rules in `.claude/rules/` enable path-specific configurations
- Token efficiency is critical - keep CLAUDE.md under 100 lines

---

## 1. CLAUDE.md File System

### 1.1 File Locations and Hierarchy

Claude Code reads memory files from multiple locations in a specific precedence order:

| Memory Type | Location | Purpose | Shared With |
|-------------|----------|---------|-------------|
| **Enterprise Policy** | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`<br>Linux: `/etc/claude-code/CLAUDE.md`<br>Windows: `C:\ProgramData\ClaudeCode\CLAUDE.md` | Organization-wide instructions managed by IT/DevOps | All users in organization |
| **User Memory** | `~/.claude/CLAUDE.md` | Personal preferences for all projects | Just you (all projects) |
| **Project Memory** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared instructions for the project | Team members via source control |
| **Local Memory** | `./CLAUDE.local.md` | Personal overrides for specific project | Just you (this project only) |

**Precedence Rule:** More specific scopes override more general ones. Local > Project > User > Enterprise.

### 1.2 File Discovery Behavior

Claude Code reads memories recursively:
- Starting from the current working directory (cwd)
- Recurses upward toward the filesystem root
- Reads any CLAUDE.md or CLAUDE.local.md files found along the path

**Example:** If you run Claude Code in `foo/bar/`, it will read:
- `foo/bar/CLAUDE.md`
- `foo/CLAUDE.md`
- `CLAUDE.md` (at project root)

**Known Issue:** Documentation inconsistencies exist regarding exact boundary points and whether `/CLAUDE.md` at the filesystem root is read. See [GitHub Issue #722](https://github.com/anthropics/claude-code/issues/722).

### 1.3 CLAUDE.md Imports

CLAUDE.md files support importing other markdown files:

```markdown
# CLAUDE.md
@core/FLAGS.md
@core/PRINCIPLES.md
@modes/MODE_INDEX.md
```

When you use `@` file references in conversations:
- The `CLAUDE.md` from the referenced file's directory is added to context
- Parent directory `CLAUDE.md` files are also included

---

## 2. Settings Configuration

### 2.1 Settings File Locations

| Scope | Location | Purpose |
|-------|----------|---------|
| **Managed** | OS-specific system directories | Enterprise policies (highest priority) |
| **User** | `~/.claude/settings.json` | Personal preferences across all projects |
| **Project** | `.claude/settings.json` | Team-shared project settings |
| **Local** | `.claude/settings.local.json` | Personal project overrides |

### 2.2 Settings Structure

```json
{
  "$schema": "https://...",
  "model": "claude-sonnet-4-5-20250929",
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(npm run:*)",
      "Bash(git:*)",
      "Edit(src/**)",
      "mcp__github"
    ],
    "deny": [
      "Read(.env*)",
      "Read(secrets/)",
      "Bash(rm -rf:*)",
      "Bash(sudo:*)",
      "Edit(.git/)"
    ],
    "ask": [
      "WebFetch",
      "Bash(curl:*)",
      "Bash(docker:*)"
    ],
    "additionalDirectories": [
      "../shared-lib",
      "../docs"
    ],
    "defaultMode": "acceptEdits"
  },
  "env": {
    "NODE_ENV": "development"
  },
  "hooks": { },
  "sandbox": {
    "enabled": false,
    "autoAllowBashIfSandboxed": true
  }
}
```

### 2.3 Permission Rules

**Rule Format:** `Tool` or `Tool(optional-specifier)`

**Precedence:** Deny > Ask > Allow

| Rule Type | Behavior |
|-----------|----------|
| **Allow** | Claude can use the tool without manual approval |
| **Ask** | Requires user confirmation each time |
| **Deny** | Prevents Claude from using the tool |

**Wildcard Patterns (v2.1.0+):**

| Pattern | Example | Matches |
|---------|---------|---------|
| Prefix wildcard | `Bash(npm *)` | `npm install`, `npm run build` |
| Suffix wildcard | `Bash(* install)` | `npm install`, `yarn install` |
| Middle wildcard | `Bash(git * main)` | `git push origin main` |
| Help commands | `Bash(*-h)` | `node -h`, `npm --help` |

**Path Pattern Types (gitignore-style):**

| Pattern | Meaning | Example |
|---------|---------|---------|
| `//path` | Absolute from filesystem root | `Read(//Users/alice/secrets/)` |
| `~/path` | From home directory | `Read(~/Documents/*.pdf)` |
| `/path` | Relative to settings file | `Edit(/src/**/*.ts)` |
| `path` or `./path` | Relative to current directory | `Read(.env*)` |

### 2.4 Permission Modes

| Mode | Behavior |
|------|----------|
| `default` | Ask for each action |
| `acceptEdits` | Auto-accept file edits, ask for others |
| `trustMode` | Trust most operations (use cautiously) |

---

## 3. Modular Rules System

### 3.1 The .claude/rules/ Directory

All `.md` files in `.claude/rules/` are automatically loaded as project memory with the same priority as `.claude/CLAUDE.md`.

**Benefits:**
- Organize rules by domain (api, frontend, testing)
- Path-specific rules for different parts of the codebase
- Easier maintenance and review

### 3.2 Path-Specific Rules

Rules can be scoped to specific files using YAML frontmatter:

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/services/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
- Include OpenAPI documentation comments
```

**Glob Pattern Support:**
- `*` matches any characters except `/`
- `**` matches any characters including `/`
- `{a,b,c}` matches any of a, b, or c

### 3.3 Subdirectory Structure

```
.claude/
├── CLAUDE.md              # Main project memory
├── settings.json          # Project settings
├── settings.local.json    # Personal overrides (gitignored)
├── rules/
│   ├── api-rules.md       # API development rules
│   ├── frontend-rules.md  # Frontend patterns
│   └── testing-rules.md   # Testing standards
├── commands/              # Custom slash commands
│   └── deploy.md
└── skills/                # Skill definitions
    └── review/
        └── SKILL.md
```

---

## 4. Hooks System

### 4.1 Lifecycle Events

| Event | Trigger | Use Case |
|-------|---------|----------|
| `SessionStart` | Claude Code starts or resumes | Environment setup, warnings |
| `UserPromptSubmit` | User submits a prompt | Context injection, validation |
| `PreToolUse` | Before tool invocation | Blocking, approval, logging |
| `PostToolUse` | After tool invocation | Notifications, formatting |
| `PreCompact` | Before context compression | Backup important context |
| `Stop` | Agent stops | Cleanup, notifications |

### 4.2 Hook Configuration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$FILE_PATH\""
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/validate-bash.sh"
          }
        ]
      }
    ]
  }
}
```

### 4.3 Hook Options

| Option | Description |
|--------|-------------|
| `matcher` | Regex pattern for tools (e.g., `"Edit\|Write"`, `"Bash"`) |
| `type` | Hook type (`"command"` for shell commands) |
| `command` | Shell command to execute |
| `once` | If `true`, fires only once per session (v2.1.0+) |

### 4.4 Hook Return Values

**Exit Codes:**

| Exit Code | Behavior |
|-----------|----------|
| 0 (Success) | stdout shown to user, added to context |
| 2 (Blocking) | stderr fed back to Claude, blocks the action |
| Other | stderr shown to user, execution continues |

**JSON Output (PreToolUse):**

```json
{
  "permissionDecision": "allow" | "deny" | "ask",
  "additionalContext": "Additional information for Claude"
}
```

### 4.5 Hooks in Frontmatter (v2.1.0+)

Agents, skills, and slash commands can define their own hooks:

```yaml
---
hooks:
  PreToolUse:
    - matcher: "Bash(git commit*)"
      command: ".claude/hooks/pre-commit-check.sh"
  PostToolUse:
    - matcher: "Write"
      command: "echo 'File written'"
---
```

---

## 5. Best Practices

### 5.1 Token Efficiency

**Critical:** CLAUDE.md files are included in every interaction.

| Practice | Example |
|----------|---------|
| **Be concise** | "Functional components only" NOT "Always ensure that components use React hooks rather than class-based components" |
| **Line limit** | Keep under 100 lines |
| **Remove verbosity** | Review monthly, prune unused rules |
| **Don't @-file large docs** | Instead: "For FooBarError troubleshooting, see `path/to/docs.md`" |

### 5.2 Writing Effective Rules

**DO:**
- Start with 5-10 essential rules
- Test that rules work: "Create a component following our patterns"
- Provide alternatives, not just prohibitions
- Use specific, actionable language

**DON'T:**
- Use negative-only constraints ("Never use X" without alternative)
- Embed entire documentation files
- Add rules for behaviors Claude already follows

**Example - Good vs Bad:**

```markdown
# Bad
Never use the --foo-bar flag when running npm commands.

# Good
Use `npm run build` without flags. If you encounter build errors,
check `docs/build-troubleshooting.md` for alternatives.
```

### 5.3 Security Best Practices

| Practice | Implementation |
|----------|----------------|
| **Sandbox untrusted content** | Use `/sandbox` command |
| **Block sensitive files** | `deny: ["Read(.env*)", "Read(secrets/)"]` |
| **Block risky commands** | `deny: ["Bash(rm -rf:*)", "Bash(sudo:*)"]` |
| **Explicit MCP servers** | `"enabledMcpjsonServers": ["github", "memory"]` |
| **Regular audits** | Monthly `/permissions` review |
| **Containerize** | Run in Docker/VM for high-security |

---

## 6. Enterprise Deployment

### 6.1 Organization-Wide Configuration

Deploy CLAUDE.md files at multiple levels:

1. **System directories** for company-wide standards:
   - macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`
   - Linux: `/etc/claude-code/CLAUDE.md`
   - Windows: `C:\ProgramData\ClaudeCode\CLAUDE.md`

2. **Repository-level** for project architecture and guidelines

3. **Managed settings** for enforcing security policies:
   - Windows: `C:\Program Files\ClaudeCode\managed-settings.json` (new path)

### 6.2 Cloud Integration

| Provider | Features |
|----------|----------|
| **AWS Bedrock** | IAM authentication, Cost Explorer integration, VPC isolation |
| **Google Vertex AI** | IAM roles, Cloud Audit Logs, PSC endpoints |

### 6.3 Security Patterns

```json
{
  "permissions": {
    "deny": [
      "Bash(curl:*)",
      "Bash(wget:*)",
      "Read(.env*)",
      "Read(**/secrets/**)"
    ]
  },
  "enabledMcpjsonServers": ["github", "memory"],
  "disabledMcpjsonServers": ["filesystem"],
  "allowManagedHooksOnly": true
}
```

---

## 7. Recent Changes (v2.1.x)

### 7.1 Key Updates

| Version | Feature |
|---------|---------|
| 2.1.0 | Wildcard permission syntax (`Bash(npm *)`) |
| 2.1.0 | Hooks in agent/skill/command frontmatter |
| 2.1.0 | `once: true` for single-fire hooks |
| 2.1.0 | `Task(AgentName)` syntax to disable specific agents |
| 2.1.0 | MCP `list_changed` notifications |
| 2.1.0 | `respectGitignore` setting for @-mention picker |
| 2.1.7 | `auto:N` syntax for MCP tool search threshold |
| 2.1.9 | `plansDirectory` setting |
| 2.1.9 | `additionalContext` return from PreToolUse hooks |

### 7.2 Deprecated Features

| Deprecated | Replacement |
|------------|-------------|
| `includeCoAuthoredBy` | `attribution` setting |
| `/allowed-tools` | `/permissions` |
| `claude config` commands | Edit settings.json directly |
| Windows `C:\ProgramData\ClaudeCode\managed-settings.json` | `C:\Program Files\ClaudeCode\managed-settings.json` |
| `ANTHROPIC_SMALL_FAST_MODEL` | `ANTHROPIC_DEFAULT_HAIKU_MODEL` |

---

## 8. Known Issues and Documentation Gaps

### 8.1 Documented Issues

| Issue | Status | Reference |
|-------|--------|-----------|
| CLAUDE.md discovery behavior inconsistent with docs | Open | [#722](https://github.com/anthropics/claude-code/issues/722), [#2274](https://github.com/anthropics/claude-code/issues/2274) |
| CLAUDE.md persistence through context compression unclear | Open | [#11629](https://github.com/anthropics/claude-code/issues/11629) |
| `/etc/claude-code` not mentioned in all docs | Acknowledged | [#2274](https://github.com/anthropics/claude-code/issues/2274) |

### 8.2 Uncertainty Areas

| Area | Confidence | Notes |
|------|------------|-------|
| File hierarchy and locations | 95% | Official docs + multiple confirmations |
| Permission syntax | 95% | Official docs + CHANGELOG |
| Hooks lifecycle | 90% | Official docs + community verification |
| Context compression behavior | 60% | Documented as unclear in GitHub issues |
| Symlink handling in rules/ | 70% | Limited documentation |

---

## 9. Quick Reference

### 9.1 Essential Commands

| Command | Purpose |
|---------|---------|
| `/init` | Bootstrap CLAUDE.md for project |
| `/memory` | Edit CLAUDE.md files |
| `/permissions` | View/modify permission rules |
| `/hooks` | Manage hook configurations |
| `/config` | View/modify configuration |
| `/doctor` | Health check installation |

### 9.2 File Checklist for New Projects

```
[ ] ./CLAUDE.md - Project rules and context
[ ] ./.claude/settings.json - Team permissions
[ ] ./.claude/settings.local.json - Personal overrides (gitignored)
[ ] ./.claude/rules/*.md - Domain-specific rules (optional)
[ ] ./.claude/commands/*.md - Custom slash commands (optional)
```

### 9.3 Minimal CLAUDE.md Template

```markdown
# Project: [Name]

## Tech Stack
- [Framework], [Language], [Database]

## Rules
- [Essential rule 1]
- [Essential rule 2]
- [Essential rule 3]

## Commands
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`
```

---

## Sources

### Official Documentation
- [Claude Code Settings](https://code.claude.com/docs/en/settings) - code.claude.com
- [Memory Management](https://code.claude.com/docs/en/memory) - code.claude.com
- [Identity and Access Management](https://code.claude.com/docs/en/iam) - code.claude.com
- [Security](https://code.claude.com/docs/en/security) - code.claude.com
- [Enterprise Deployment](https://code.claude.com/docs/en/third-party-integrations) - code.claude.com
- [CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) - GitHub

### GitHub Issues
- [#722 - CLAUDE.md discovery documentation](https://github.com/anthropics/claude-code/issues/722)
- [#2274 - CLAUDE.md locations documentation](https://github.com/anthropics/claude-code/issues/2274)
- [#11629 - CLAUDE.md persistence through compression](https://github.com/anthropics/claude-code/issues/11629)

### Community Resources
- [Claude Code Part 2 - CLAUDE.md Configuration](https://www.letanure.dev/blog/2025-07-31--claude-code-part-2-claude-md-configuration) - Luiz Tanure
- [Complete Guide to Global Instructions](https://naqeebali-shamsi.medium.com/the-complete-guide-to-setting-global-instructions-for-claude-code-cli-cec8407c99a0) - Medium
- [Claude Code Hooks: A Practical Guide](https://www.datacamp.com/tutorial/claude-code-hooks) - DataCamp
- [How I Use Every Claude Code Feature](https://blog.sshh.io/p/how-i-use-every-claude-code-feature) - Shrivu Shankar
- [Claude Code CLI: The Definitive Technical Reference](https://blakecrosley.com/guide/claude-code) - Blake Crosley

### Enterprise & Security
- [Claude Code Security Best Practices](https://www.backslash.security/blog/claude-code-security-best-practices) - Backslash Security
- [Claude Code Deployment with Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/claude-code-deployment-patterns-and-best-practices-with-amazon-bedrock/) - AWS

---

*Report generated by SuperClaude Deep Research Agent*
*Research methodology: Multi-hop web search with source credibility weighting*
