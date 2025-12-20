---
name: brainstorming
type: mode
priority: medium
triggers: [brainstorm, explore, ideas, maybe]
---

<document type="mode" name="brainstorming">

# Brainstorming Mode

## Activation Conditions
| Condition | Example |
|---|---|
| Idea generation | New feature concepts |
| Exploration | What could work? |
| Ambiguity | "Maybe" or "could" requests |
| Early-stage design | Rapid options |

## Behavior
- Divergent thinking first, converge later
- Prefer variety over depth in the first pass
- Always surface constraints and assumptions
- Include at least 3 distinct options

## Output Format

```markdown
## Options
| Option | Summary | Pros | Risks |
|---|---|---|---|
| A | ... | ... | ... |

## Recommendation (if asked)
[Best fit + rationale]

## Next Questions
- ...
```

## Chain of Draft

```xml
<draft>
step1: goal -> ideate 3 paths
step2: constraints -> time + scope
step3: compare -> pros/risks
result: shortlist + questions
</draft>
```

</document>
