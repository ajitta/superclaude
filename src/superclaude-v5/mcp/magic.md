---
name: magic
type: mcp
priority: high
triggers: [ui, component, design]
---

<document type="mcp" name="magic">

# Magic MCP

UI component generation and layout assistance.

## Use When
- Building UI components
- Rapid layout prototyping
- Consistent design patterns needed

## Inputs
- Component description
- Design constraints (framework, style)

## Output Expectations
- Component code (framework-aligned)
- Styling and structure included

## Best Practices
- Provide constraints (breakpoints, theme)
- Validate a11y basics
- Avoid over-customization unless requested

## Example

```xml
<draft>
step1: component -> login form
step2: framework -> React + Tailwind
step3: constraints -> mobile-first
result: accessible component
</draft>
```

</document>
