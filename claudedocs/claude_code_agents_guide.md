# Claude Code Agents (Subagents) User Guide

This document summarizes Claude Code's Subagents documentation and organizes SuperClaude integration points.
Reference: https://code.claude.com/docs/en/sub-agents

## 1) Overview
Subagents are specialized workers with **separate context and tool permissions**.
Claude can automatically delegate to them, or users can invoke them explicitly.

## 2) Creation/Management: `/agents` (Recommended)
The `/agents` command provides GUI-like guidance for creation, modification, and tool permission settings.
- Create new agent
- Select tool permissions (including built-in tools + MCP tools)
- Immediately usable (no restart required)

## 3) Storage Locations and Priority
Subagents are stored as Markdown files with YAML frontmatter.
- Project: `.claude/agents/` (higher priority)
- User: `~/.claude/agents/` (shared across all projects)

When names conflict, project agents take priority.

## 4) File Format (Frontmatter)
```markdown
---
name: code-reviewer
description: Review code changes for quality and security.
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: default
skills: code-review, secure-coding
---

You are a senior code reviewer...
```

Key fields:
- `tools`: If not specified, **inherits all tools from the main thread**
- `skills`: Subagents **do not inherit** skills from the main thread
- `permissionMode`: `default`, `acceptEdits`, `bypassPermissions`, `plan`, `ignore`
- `model`: `sonnet/opus/haiku` or `inherit`

## 5) Invocation Methods
- Automatic: Claude delegates when deemed appropriate
- Explicit invocation example:
  - `Use the code-reviewer subagent to check my recent changes`

## 6) Plugin/CLI-Based Agents
- Plugin: Agents defined in `agents/` at plugin root appear in `/agents`
- CLI: `claude --agents '{...}'` can define session-limited agents

## 7) Location in SuperClaude
When SuperClaude is installed, files are copied to the following paths:
- Source: `src/superclaude/agents/`
- Target: `~/.claude/agents/` or `./.claude/agents/`

## 8) Operational Tips
- Don't overload a single agent with too many roles; separate responsibilities.
- Apply the principle of least tool permissions to improve safety.
- For long-running tasks, you can utilize the `resume` flow (see official documentation).
