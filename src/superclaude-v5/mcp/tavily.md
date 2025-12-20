---
name: tavily
type: mcp
priority: high
triggers: [web, search, current]
---

<document type="mcp" name="tavily">

# Tavily MCP

Web search for current information.

## Use When
- Up-to-date facts required
- News, prices, policies, releases
- External validation needed

## Inputs
- Query
- Recency / domain filters

## Output Expectations
- Source-backed summaries
- Multiple viewpoints when relevant

## Best Practices
- Prefer authoritative domains
- Cite sources for claims

## Example

```xml
<draft>
step1: query -> "Next.js 15 release notes"
step2: filter -> last 30 days
step3: summarize -> key changes
result: sources + summary
</draft>
```

</document>
