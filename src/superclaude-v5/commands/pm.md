---
name: pm
type: command
priority: low
triggers: [pm, product manager, roadmap]
---

<document type="command" name="pm">

# /sc:pm

## Purpose
Product management support (requirements, prioritization, roadmap).

## Syntax
```
/sc:pm [topic]
```

## Examples

<example>
  <input>/sc:pm prioritize backlog</input>
  <output>RICE table + top picks</output>
</example>

<example>
  <input>/sc:pm define MVP for feature X</input>
  <output>MVP scope + acceptance criteria</output>
</example>

<example>
  <input>/sc:pm roadmap for Q1</input>
  <output>Milestones + dependencies</output>
</example>

</document>
