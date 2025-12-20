---
name: analyze
type: command
priority: critical
triggers: [analyze, troubleshoot, explain, debug]
---

<document type="command" name="analyze">

# /sc:analyze

## Purpose
Analyze issues, explain behavior, and troubleshoot problems.

## Syntax
```
/sc:analyze [target] [--log] [--scope]
```

## Workflow
1. Reproduce or restate the issue
2. Inspect evidence (logs, code, tests)
3. Isolate root cause
4. Propose fix + validation

## Chain of Draft

```xml
<draft>
step1: symptom -> 500 on login
step2: evidence -> logs + diff
step3: cause -> auth timeout
result: fix + test
</draft>
```

## Examples

<example>
  <input>/sc:analyze failing test suite</input>
  <output>Root cause + fix plan</output>
</example>

<example>
  <input>/sc:analyze memory spike</input>
  <output>Likely sources + profiling plan</output>
</example>

<example>
  <input>/sc:analyze slow API</input>
  <output>DB bottleneck + optimization</output>
</example>

## Quality Criteria
- Evidence-backed root cause
- Specific fix and validation steps

</document>
