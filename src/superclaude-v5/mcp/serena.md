---
name: serena
type: mcp
priority: medium
triggers: [symbol, navigate, codebase]
---

<document type="mcp" name="serena">

# Serena MCP

Symbol navigation and codebase exploration.

## Use When
- Finding references or definitions
- Understanding large codebases
- Dependency tracing

## Inputs
- Symbol name
- Optional scope

## Output Expectations
- Precise symbol locations
- Reference graph hints

## Best Practices
- Start with high-level entry points
- Combine with ripgrep for raw search

## Example

```xml
<draft>
step1: symbol -> AuthService
step2: find -> references
step3: trace -> call graph
result: 8 usages mapped
</draft>
```

</document>
