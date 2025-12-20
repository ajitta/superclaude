---
name: context7
type: mcp
priority: high
triggers: [library, docs, framework]
---

<document type="mcp" name="context7">

# Context7 MCP

Official library documentation retrieval.

## Use When
- Need authoritative API references
- Library behavior is uncertain
- Version-specific guidance required

## Inputs
- Library name or ID
- Optional topic (hooks, routing, auth)

## Output Expectations
- Source-linked docs summary
- Version-aware guidance

## Best Practices
- Prefer official docs over blogs
- Cite docs for behavioral claims
- Resolve library ID before fetching

## Example

```xml
<draft>
step1: library -> next.js
step2: resolve -> /vercel/next.js
step3: fetch -> routing topic
result: summary + citations
</draft>
```

</document>
