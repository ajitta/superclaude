---
name: plan
type: command
priority: medium
triggers: [plan, estimate, spec, roadmap]
---

<document type="command" name="plan">

# /sc:plan

## Purpose
Planning, estimation, and spec outlines.

## Syntax
```
/sc:plan [target] [--deep] [--estimate]
```

## Workflow
1. Clarify requirements
2. Break into steps
3. Estimate effort
4. Identify risks and dependencies

## Examples

<example>
  <input>/sc:plan migration to v5</input>
  <output>Step plan + risks</output>
</example>

<example>
  <input>/sc:plan feature X --estimate</input>
  <output>Effort estimate + scope</output>
</example>

<example>
  <input>/sc:plan --deep refactor module</input>
  <output>Detailed plan with dependencies</output>
</example>

</document>
