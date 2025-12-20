---
name: sequential
type: mcp
priority: medium
triggers: [complex, reasoning, sequential]
---

<document type="mcp" name="sequential">

# Sequential MCP

Structured multi-step reasoning.

## Use When
- Complex analysis required
- Multi-step plans with dependencies
- High ambiguity or risk

## Inputs
- Problem statement
- Constraints and success criteria

## Output Expectations
- Stepwise reasoning summary
- Clear decisions and rationale

## Best Practices
- Keep steps explicit
- Verify assumptions

## Example

```xml
<draft>
step1: problem -> auth failing
step2: analyze -> token + session
step3: hypothesis -> expired refresh
result: root cause identified
</draft>
```

</document>
