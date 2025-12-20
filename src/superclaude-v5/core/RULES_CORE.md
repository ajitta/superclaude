---
name: rules-core
type: core
priority: critical
---

<document type="core" name="rules-core">

# Core Rules (Opus 4.5)

## Critical (Never Compromise)

| Rule | Action | Reason |
|---|---|---|
| Git First | Check `status` and branch before changes | Safe version control |
| Read -> Edit | Never edit without reading | Context required |
| Feature Branch | Avoid direct work on main/master | Protect production |
| No Skip | Do not skip tests/validation | Quality assurance |
| Evidence | Claims must be verifiable | Prevent hallucination |

## Important (Strong Preference)

| Rule | Pattern | Reason |
|---|---|---|
| Todo | 3+ steps -> TodoWrite | Track complex tasks |
| Complete | Start = finish, no TODOs | Completeness |
| Scope | Build only what is asked | Avoid over-engineering |
| Clean | Remove temp files | Clean workspace |
| Professional | No marketing language | Clear communication |

## Recommended (When Practical)

| Rule | Tool | Reason |
|---|---|---|
| Parallel | Batch independent ops | Efficiency |
| MCP First | MCP > Native > Basic | Optimal tool selection |
| Naming | Follow existing conventions | Consistency |
| Structure | Respect project layout | Reduce friction |

## Safe Execution Template

<safe_execution>
<scope type="allowlist">
  <path>src/</path>
  <path>tests/</path>
  <path>docs/</path>
</scope>

<scope type="denylist">
  <path>node_modules/</path>
  <path>.git/</path>
  <path>dist/</path>
  <path>build/</path>
</scope>

Always ask for confirmation before destructive operations.

Task decomposition:
1. Execute first change
2. Review linter and test results
3. Request user confirmation
4. Execute next change
</safe_execution>

## Quick Decision Flow

```
Task request -> Complexity check -> 3+ steps? -> TodoWrite
File operation -> Read first -> Understand -> Edit
Tool selection -> MCP available? -> Use MCP -> Fallback to Native
```

</document>
