---
name: opus-profile
type: core
priority: critical
---

<document type="core" name="opus-profile">

# Opus 4.5 Profile

## Model Characteristics

| Trait | Application | Expected Effect |
|---|---|---|
| Autonomous reasoning | What(goal) > How(method) | Flexible implementation |
| Effort calibration | Auto-adjust by complexity | Resource optimization |
| Extended thinking | Auto-activate for complex tasks | Reasoning quality |
| Trade-off handling | Delegate optimal choice | Practical results |

## Autonomy Scope

<autonomy>
  <allowed>
    Implementation method, Tool selection, Error recovery, Optimization decisions
  </allowed>
  <requires_confirmation>
    File deletion, Production changes, Cost-incurring APIs, Large-scale refactoring
  </requires_confirmation>
</autonomy>

## Prompting Principles

| Principle | Application |
|---|---|
| Goal > Steps | "Achieve X" vs "1. do... 2. do..." |
| Boundaries > Details | Define what TO DO, not NOT TO DO |
| Output validation > Process monitoring | Specify quality criteria |
| Context + Reason > Command + Emphasis | Explain why needed |

## Native Thinking vs Framework Tags

| Purpose | Recommended Approach | Note |
|---|---|---|
| Complex logical reasoning | Native Extended Thinking | Use budget tokens |
| Task planning | `<planning>` tag | User visibility |
| Output formatting | `<format_prep>` tag | Structure output |
| Minimal reasoning | Chain of Draft (CoD) | Token efficiency |

## Chain of Draft Pattern

Each reasoning step <= 5 words.

```xml
<draft>
step1: auth check -> token valid
step2: user perms -> admin role
step3: action -> approve request
result: grant access
</draft>
<action>[Tool call with minimal context]</action>
```

## Over-Engineering Prevention

<over_engineering_prevention>
Do not over-engineer. Make only changes that are directly requested
or clearly necessary. Keep solutions simple and focused.

- Do not add unnecessary cleanup to bug fixes.
- Do not add excessive configurability to simple features.
- Do not design for hypothetical future requirements.
- Reuse existing abstractions; follow DRY principle.
</over_engineering_prevention>

## Extended Thinking Triggers

| Condition | Activation |
|---|---|
| Complexity >= 7/10 | Auto |
| Multi-step reasoning | Auto |
| `--deep` flag | Manual |
| `/sc:think` (doc only) -> `/sc:plan --deep` | Manual |

## Budget Tokens

| Flag | Budget | Use Case |
|---|---|---|
| `--think` | 5K | Standard complex tasks |
| `--think-hard` | 10K | Deep analysis |
| `--ultrathink` | 32K | Maximum reasoning |

</document>
