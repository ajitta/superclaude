# Claude Code Skills User Guide

This document summarizes the key points from official documentation and organizes connections with SuperClaude configuration.
Reference: https://code.claude.com/docs/en/skills

## 1) Skills Overview
Skills are knowledge/procedure bundles that the **model automatically activates**. Even without explicit user invocation, Claude selects and applies skills when the request matches the `description`.

## 2) Storage Locations and Priority
Official locations and priorities are as follows:
- Enterprise: Managed policies (organization-wide)
- Personal: `~/.claude/skills/`
- Project: `.claude/skills/`
- Plugin: `skills/` within plugin bundle

When skills with the same name conflict, **higher priority wins**.

## 3) SKILL.md Structure (Required)
`SKILL.md` consists of YAML frontmatter + body instructions.

```markdown
---
name: explaining-code
description: Explains code with diagrams and analogies. Use when user asks how code works.
allowed-tools: Read, Grep
model: claude-sonnet-4-20250514
---

## Instructions
- Start with an analogy
- Provide an ASCII diagram
```

Required fields:
- `name`: Only lowercase letters/numbers/hyphens allowed, recommend matching directory name
- `description`: Clearly describe when it should be used (model activation criteria)

Optional fields:
- `allowed-tools`: Tools allowed while skill is active
- `model`: Skill-specific model designation

## 4) Activation Flow
1) When request meaning matches `description`, Claude suggests/applies skill usage
2) Loads or executes connected files/scripts as needed
3) Changes are reflected **after Claude Code restart**

## 5) Separate Large Knowledge
To reduce context overload, **Progressive Disclosure** approach is recommended:
- Core content in `SKILL.md`
- Detailed documentation separated into `reference.md`, `examples.md`
- Scripts placed in `scripts/` and executed explicitly

## 6) Location in SuperClaude
When SuperClaude is installed, files are copied to the following paths:
- Source: `src/superclaude/skills/`
- Target: `~/.claude/skills/` or `./.claude/skills/`

## 7) Practical Tips
- If trigger doesn't work, include keywords from `description` in your prompt
- YAML errors cause loading failures, so check `---` and indentation
- Use `claude --debug` to check loading errors
