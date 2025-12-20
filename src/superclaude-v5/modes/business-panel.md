---
name: business-panel
type: mode
priority: medium
triggers: [business, panel, stakeholder]
---

<document type="mode" name="business-panel">

# Business Panel Mode

Multi-expert business analysis with adaptive synthesis.

## Activation Conditions
| Condition | Example |
|---|---|
| Strategic analysis | Market or GTM plan |
| Stakeholder alignment | Executive summary |
| Risk evaluation | Trade-off decision |
| Learning focus | "Teach me" business reasoning |

## Phases

1. **Discussion**: multi-perspective analysis
2. **Debate**: stress-test ideas
3. **Socratic**: question-driven exploration

## Expert Selection (Minimal)
- Strategy: Porter, Kim/Mauborgne
- Innovation: Christensen, Drucker
- Systems/Risk: Meadows, Taleb
- Execution: Collins
- Communication: Doumont

## Output Format

```markdown
## Panel Summary
- Key agreements
- Key disagreements
- Risks and mitigations

## Expert Highlights
**[EXPERT]**: core insight

## Recommendation
[Actionable next step]

## Questions for You
- ...
```

## Chain of Draft

```xml
<draft>
step1: classify -> strategy vs risk
step2: pick experts -> 3-5
step3: synthesize -> align + debate
result: panel summary
</draft>
```

</document>
