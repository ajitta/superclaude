---
name: morphllm
type: mcp
priority: high
triggers: [bulk-edit, pattern-edit]
---

<document type="mcp" name="morphllm">

# Morphllm MCP

Pattern-based bulk edits across files.

## Use When
- Repetitive edits across many files
- Structural or naming refactors
- Consistent text transformations

## Inputs
- Pattern or rule
- Scope (files/dirs)

## Output Expectations
- Batch changes with preview
- Minimal manual follow-up

## Best Practices
- Constrain scope first
- Verify with tests after batch edits

## Example

```xml
<draft>
step1: pattern -> rename oldFunc to newFunc
step2: scope -> src/**/*.ts
step3: execute -> batch apply
result: 12 files updated
</draft>
```

</document>
