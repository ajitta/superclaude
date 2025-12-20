---
name: research
type: command
priority: critical
triggers: [research, investigate, evaluate, compare]
---

<document type="command" name="research">

# /sc:research

## Purpose
Deep research with evidence, sources, and confidence scores.

## Syntax
```
/sc:research [topic] [--scope] [--sources=N]
```

## Workflow
1. Define the question and success criteria
2. Gather sources (MCP first)
3. Analyze and cross-validate
4. Score confidence
5. Synthesize findings

## Chain of Draft

```xml
<draft>
step1: topic -> caching strategy
step2: sources -> docs + benchmarks
step3: compare -> latency + cost
result: ranked options
</draft>
```

## Examples

<example>
  <input>/sc:research Postgres vs MySQL</input>
  <output>Comparison with pros/cons and confidence</output>
</example>

<example>
  <input>/sc:research latest changes in Next.js</input>
  <output>Release summary with citations</output>
</example>

<example>
  <input>/sc:research auth libraries --sources=5</input>
  <output>Shortlist with evaluation criteria</output>
</example>

## Success Criteria
- All claims have cited sources
- Confidence scores on key findings
- Uncertainties explicitly labeled

## Boundaries

| Will | Won't |
|---|---|
| Gather and synthesize evidence | Make business decisions |
| Score confidence | Guarantee accuracy |
| Cross-validate sources | Access paywalled content |

</document>
