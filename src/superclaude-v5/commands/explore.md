---
name: explore
type: command
priority: medium
triggers: [brainstorm, design, explore, ideate]
---

<document type="command" name="explore">

# /sc:explore

## Purpose
Creative exploration and early-stage design.

## Syntax
```
/sc:explore [topic] [--constraints]
```

## Workflow
1. Clarify goals
2. Generate 3+ options
3. Compare pros/cons
4. Ask next questions

## Chain of Draft

```xml
<draft>
step1: topic -> onboarding flow
step2: options -> 3 variants
step3: compare -> effort vs impact
result: shortlist
</draft>
```

## Examples

<example>
  <input>/sc:explore redesign settings UX</input>
  <output>3 approaches with trade-offs</output>
</example>

<example>
  <input>/sc:explore data model for tags</input>
  <output>Options + recommended next step</output>
</example>

<example>
  <input>/sc:explore marketing automation ideas</input>
  <output>Idea list + risks</output>
</example>

## Success Criteria
- 3+ distinct options presented
- Pros/cons for each option
- Clear next questions or steps

## Boundaries

| Will | Won't |
|---|---|
| Generate diverse options | Make final decisions |
| Surface trade-offs | Implement without approval |
| Ask clarifying questions | Over-commit to one path early |

</document>
