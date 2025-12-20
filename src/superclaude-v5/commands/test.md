---
name: test
type: command
priority: critical
triggers: [test, verify, check]
---

<document type="command" name="test">

# /sc:test

## Purpose
Run tests and report results.

## Syntax
```
/sc:test [target] [--scope unit|integration|e2e]
```

## Workflow
1. Identify relevant tests
2. Run tests
3. Summarize failures
4. Suggest next fixes

## Examples

<example>
  <input>/sc:test</input>
  <output>Runs default suite and summarizes</output>
</example>

<example>
  <input>/sc:test api --scope=integration</input>
  <output>Runs integration tests for API</output>
</example>

<example>
  <input>/sc:test --scope=unit</input>
  <output>Runs unit tests only</output>
</example>

## Success Criteria
- Tests executed with output
- Failures summarized
- Next steps proposed

## Boundaries

| Will | Won't |
|---|---|
| Run test suites | Modify tests without request |
| Summarize results | Skip failing tests |
| Suggest fixes | Auto-fix without approval |

</document>
