---
name: using-superclaude
description: |
  Meta-skill for discovering and using SuperClaude features. Loaded at session
  start. Covers SC commands (/sc:*), agents, skills, and core configuration
  (FLAGS, PRINCIPLES, RULES).
---

## Purpose

Orient the user and model to SuperClaude's available features and how to invoke them.

## SuperClaude Features

**Commands** — Quick actions invoked as `/sc:<name>`. Use `/sc:help` for the full listing.

**Agents** — Specialized personas with defined models, permissions, and tool access. Defined in `~/.claude/agents/`.

**Skills** — Structured process workflows invoked via the Skill tool in Claude Code. Defined in `~/.claude/skills/`.

**Core config** — `FLAGS.md` (behavioral modes and MCP flags), `PRINCIPLES.md` (decision frameworks), `RULES.md` (behavioral rules and workflow gates). Located in `~/.claude/superclaude/core/`.

## Workflow

1. **Check for applicable skills** before responding. Match the current task against available skills by name and description.
2. **Invoke matching skills** using the Skill tool. If multiple skills apply, invoke process skills (brainstorming, debugging, TDD) before implementation skills (executing-plans, writing-plans), and implementation skills before quality skills (verification-before-completion).
3. **Use SC commands** for quick actions that do not require a full skill workflow.
4. **Follow core config** for behavioral modes (FLAGS), decision frameworks (PRINCIPLES), and workflow rules (RULES).

## Instruction Priority

When instructions conflict, follow this order:

1. **User's explicit instructions** (highest — always wins)
2. **Superpowers skills** (if loaded — process workflow authority)
3. **SuperClaude skills** (domain knowledge, /sc: commands)
4. **Default system prompt** (lowest — yields to the above)

## Superpowers Coexistence

When the Superpowers plugin is also installed, SP skills take precedence for overlapping skill names. This is handled automatically at install time.

## SC-Exclusive Skills

| Skill | Purpose |
|-------|---------|
| using-superclaude | This skill — feature discovery and skill invocation |
| confidence-check | Pre-execution confidence assessment before risky actions |
| ship | Packaging and shipping deliverables |
| simplicity-coach | Reducing complexity, removing unnecessary abstractions |

## Platform Adaptation

In non-Claude Code environments, skills cannot be invoked via the Skill tool. In those cases, treat skill content as reference documentation and follow the workflows manually.

## Completion

The appropriate skills and commands have been identified and invoked for the current task.

## Next

Use `/sc:help` for the command listing. Use the Skill tool to invoke any skill by name.
