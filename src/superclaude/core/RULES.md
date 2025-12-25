---
name: rules
type: core
triggers: [rules, behavior, compliance, standards, guidelines]
description: Claude Code behavioral rules for framework operation
category: core
priority: critical
---

<document type="core" name="rules"
          triggers="rules, behavior, compliance, standards, guidelines"
          priority="critical">

# Claude Code Behavioral Rules

> **Note**: Full rules are defined in `~/.claude/RULES.md`. This file provides project-specific additions.

## Priority System

| Priority | Scope | Examples |
|----------|-------|----------|
| 🔴 | Security, data safety | Never compromise |
| 🟡 | Quality, maintainability | Strong preference |
| 🟢 | Optimization, style | Apply when practical |

## Conflict Resolution
1. Safety First: Security/data rules take precedence
2. Scope > Features: Build only what's asked
3. Quality > Speed: Except in genuine emergencies

## Agent Orchestration

**Task Execution**: Auto-selection of specialist agents by keywords, file types, complexity
**PM Agent Meta-Layer**: Post-implementation documentation, mistake detection, monthly maintenance

```
User request → Specialist executes → PM Agent documents → Knowledge capture
```

## Core Rules Summary

| Rule | Priority | Key Behavior |
|------|----------|--------------|
| Workflow | 🟡 | Understand → Plan → TodoWrite → Execute → Validate |
| Planning | 🔴 | Identify parallel operations explicitly |
| Implementation | 🟡 | No partial features, no TODOs, no mocks |
| Scope | 🟡 | Build only what's asked, YAGNI |
| Git | 🔴 | Feature branches, incremental commits |
| Failure | 🔴 | Root cause analysis, never skip tests |
| Honesty | 🟡 | No marketing language, evidence-based |

## Quick Decision Trees

```
File operation → Read first → Check patterns → Edit/Create
New feature → Scope clear? → TodoWrite(3+ steps) → Execute
Tool selection → MCP > Native > Basic → Parallel when possible
```

## Priority Actions

**🔴 Safety**: git status, read before edit, feature branches, root cause analysis
**🟡 Quality**: TodoWrite for complex tasks, complete implementations, MVP first
**🟢 Efficiency**: Parallel operations, MCP tools, batch operations

</document>
