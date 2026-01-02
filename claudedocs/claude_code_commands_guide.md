# Claude Code Slash Commands User Guide

This document summarizes the official Slash Commands documentation and organizes SuperClaude command structure.
Reference: https://code.claude.com/docs/en/slash-commands

## 1) Overview
Slash commands are reusable prompts **explicitly executed** in `/command` format.
Built-in commands and user-defined commands coexist.

## 2) Basic Usage
- Syntax: `/<command-name> [arguments]`
- Built-in command list can be viewed with `/help`
- Argument hints can be displayed in command autocomplete

## 3) User-Defined Command Locations
- Project commands: `.claude/commands/` (team shared)
- Personal commands: `~/.claude/commands/` (shared across all projects)

When names conflict, **project commands take priority**.

## 4) Command File Format
Commands are Markdown files with optional frontmatter.

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: [message]
description: Create a git commit
model: claude-3-5-haiku-20241022
---

Create a git commit with message: $ARGUMENTS
```

Frontmatter key fields:
- `allowed-tools`: Restrict tools this command can use
- `argument-hint`: Argument hint displayed in autocomplete
- `description`: Command description
- `model`: Command-specific model
- `disable-model-invocation`: Block `SlashCommand` tool invocation

## 5) Argument Passing Methods
- `$ARGUMENTS`: Full argument string
- `$1`, `$2`: Positional arguments

Example:
```text
/review-pr 456 high alice
```

## 6) Namespacing
Subdirectories can represent namespaces.
Example: `.claude/commands/frontend/test.md` → `/test (project:frontend)`

## 7) Plugin Commands
Plugin commands are located in `commands/` at the plugin root and appear in `/help`.
To prevent conflicts, `/plugin-name:command-name` format is recommended.

## 8) SlashCommand Tool and Permissions
To allow Claude to **automatically invoke custom commands**,
it's recommended to explicitly include the command name in prompts or `CLAUDE.md`.

Permission rule examples:
- `SlashCommand:/commit` (exact match)
- `SlashCommand:/review-pr:*` (with arguments)

## 9) MCP Slash Commands
Commands provided by MCP servers follow this format:
- `/mcp__<server-name>__<prompt-name> [arguments]`

## 10) Location in SuperClaude
When SuperClaude is installed, files are copied to the following paths:
- Source: `src/superclaude/commands/`
- Target: `~/.claude/commands/sc/` or `./.claude/commands/sc/`
- Usage examples: `/sc:implement`, `/sc:review`
