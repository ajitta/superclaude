---
name: build
type: command
priority: critical
triggers: [implement, improve, create, develop, code]
---

<document type="command" name="build">

# /sc:build

## Purpose
Code implementation and improvement tasks.

## Syntax
```
/sc:build [target] [options]
```

## Options

| Option | Description | Default |
|---|---|---|
| `--scope` | Task scope (file/module/feature) | feature |
| `--test` | Include tests | true |
| `--doc` | Include documentation | false |
| `--deep` | Activate extended thinking | auto |

## Workflow

1. Confirm requirements -> explicit criteria
2. Review design -> 3+ steps = TodoWrite
3. Implement -> MCP-first tool selection
4. Test -> run relevant tests
5. Validate -> quality criteria

## Chain of Draft

```xml
<draft>
step1: scope -> auth feature
step2: plan -> model/api/middleware
step3: tool -> Magic MCP for UI
result: todos created
</draft>
```

## Examples

<example>
  <input>/sc:build user authentication --scope=feature --test</input>
  <output>
    ## Todo
    - Model definition
    - API endpoints
    - Middleware
    - Tests
  </output>
</example>

<example>
  <input>/sc:build --improve login-form validation</input>
  <output>
    - Add client-side validation
    - Improve error messages
  </output>
</example>

<example>
  <input>/sc:build dashboard widget --doc</input>
  <output>
    - Implement widget
    - Update docs
  </output>
</example>

## Quality Criteria

| Criteria | Required |
|---|---|
| Follow existing conventions | Yes |
| Include tests | Yes (unless --test=false) |
| Error handling | Yes |
| Documentation | Recommended |

## Success Criteria
- Requirements met and tested
- Conventions followed
- No regressions introduced

## Boundaries

| Will | Won't |
|---|---|
| Implement features | Deploy to production |
| Write tests | Skip validation |
| Follow patterns | Over-engineer |

## Over-Engineering Prevention
- Only implement requested changes
- No unnecessary abstractions
- Keep solutions simple

</document>
