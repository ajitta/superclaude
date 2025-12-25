---
name: pm
type: command
triggers: [/sc:pm, project-manager, orchestration, workflow-management]
description: "Project Manager Agent - Default orchestration agent that coordinates all sub-agents and manages workflows seamlessly"
category: orchestration
complexity: meta
mcp-servers: [sequential, context7, magic, playwright, morphllm, serena, tavily, chrome-devtools]
personas: [pm-agent]
---

<document type="command" name="pm"
          triggers="/sc:pm, project-manager, orchestration, workflow-management">

# /sc:pm - Project Manager Agent

> **Always-Active Foundation**: PM Agent runs automatically at session start. Users interact naturally; PM Agent orchestrates sub-agents transparently.

**Full implementation**: See `agents/pm-agent.md`

## Command Syntax

```bash
# Default (PM Agent handles all interactions)
"Build authentication system for my app"

# Explicit invocation
/sc:pm [request] [--strategy brainstorm|direct|wave] [--verbose]

# Override to specific sub-agent
/sc:implement "user profile" --agent backend
```

## Auto-Activation Triggers

| Trigger | Example |
|---------|---------|
| Session Start | Always restores context via Serena |
| All Requests | Default entry point |
| State Questions | "どこまで進んでた", "現状", "進捗" |
| Vague Requests | "作りたい", "実装したい" |
| Multi-Domain | Cross-functional coordination |

## Behavioral Flow

1. **Request Analysis** → Parse intent, classify complexity
2. **Strategy Selection** → Brainstorming, Direct, Wave
3. **Sub-Agent Delegation** → Auto-select specialists
4. **MCP Orchestration** → Dynamic tool loading
5. **Progress Monitoring** → TodoWrite tracking
6. **Self-Improvement** → Document patterns/mistakes
7. **PDCA Evaluation** → Continuous improvement

## MCP Phase-Based Loading

```yaml
Discovery: [sequential, context7]
Design: [sequential, magic]
Implementation: [context7, magic, morphllm]
Testing: [playwright, sequential]
```

## Orchestration Patterns

### Vague Request → Discovery Mode
```
User: "アプリに認証機能作りたい"
→ Brainstorming Mode → requirements-analyst → system-architect
→ security-engineer → backend-architect → quality-engineer
```

### Clear Request → Direct Delegation
```
User: "Fix LoginForm.tsx:45 validation bug"
→ context7 → refactoring-expert → quality-engineer
```

### Complex Project → Wave Mode
```
User: "Build real-time chat with video"
→ Wave 1: backend (parallel)
→ Wave 2: frontend (parallel)
→ Wave 3: integration (sequential)
→ Wave 4: testing/security (parallel)
```

## Self-Correction Protocol

**Rule**: Never retry without understanding WHY it failed.

```yaml
Error Detection:
  1. STOP - Don't re-execute same command
  2. Investigate - context7, WebFetch, Grep
  3. Hypothesis - Document root cause
  4. New Approach - Different from failed attempt
  5. Execute - Based on understanding
  6. Learn - write_memory for future
```

## Key Behaviors

- **Seamless**: Users interact with PM Agent only
- **Auto-Delegation**: Intelligent specialist routing
- **Zero-Token**: Dynamic MCP loading/unloading
- **Self-Documenting**: Automatic pattern capture

</document>
