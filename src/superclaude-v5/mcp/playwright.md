---
name: playwright
type: mcp
priority: medium
triggers: [browser, e2e, visual-test]
---

<document type="mcp" name="playwright">

# Playwright MCP

Browser automation and E2E validation.

## Use When
- UI behavior verification
- Visual regression checks
- Cross-browser workflows

## Inputs
- Target URL
- Test steps or assertions

## Output Expectations
- Automated steps with results
- Artifacts (screenshots/logs) if needed

## Best Practices
- Use for user-critical paths
- Keep flows deterministic

## Example

```xml
<draft>
step1: url -> /login
step2: steps -> fill + submit
step3: assert -> redirect to /dashboard
result: test passes
</draft>
```

</document>
