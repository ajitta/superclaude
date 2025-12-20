---
name: agent
type: command
priority: critical
triggers: [agent, expert, persona]
---

<document type="command" name="agent">

# /sc:agent

## Purpose
Invoke a specialized agent.

## Syntax
```
/sc:agent [name] [context]
```

## Example Agents
- architecture-expert
- quality-expert
- research-agent
- product-expert
- learning-expert
- frontend-expert
- security-expert
- devops-expert
- python-expert
- refactoring-expert
- technical-writer
- self-review

## Examples

<example>
  <input>/sc:agent architecture-expert design an event system</input>
  <output>Architecture options + recommendation</output>
</example>

<example>
  <input>/sc:agent security-expert review auth flow</input>
  <output>Threats + mitigations</output>
</example>

<example>
  <input>/sc:agent technical-writer write API docs</input>
  <output>Structured documentation</output>
</example>

</document>
