---
name: deep-research-workflows
type: example
triggers: [research-example, deep-research-workflow, research-patterns]
description: "Deep research workflow patterns with strategy examples"
category: examples
complexity: reference
mcp-servers: [tavily, playwright, context7]
---

<document type="example" name="deep-research-workflows"
          triggers="research-example, deep-research-workflow, research-patterns">

# Deep Research Workflows

## Strategy Selection

| Strategy | When to Use | Workflow |
|----------|-------------|----------|
| `planning-only` | Clear query | Direct execution, no clarification |
| `intent-planning` | Ambiguous query | Clarify → Plan → Execute |
| `unified` | Complex research | Present plan → User feedback → Adjust |

## Example 1: Planning-Only (Clear Query)

```bash
/sc:research "TensorFlow 3.0 features" --strategy planning-only --depth standard
```

```yaml
Workflow:
  1. Decompose: docs, changelog, tutorials (no user input)
  2. Execute: Hop 1 (docs) → Hop 2 (tutorials) → Confidence 0.85
  3. Synthesize: Features, migration guide, performance data
```

## Example 2: Intent-Planning (Ambiguous Query)

```bash
/sc:research "AI safety" --strategy intent-planning --depth deep
```

```yaml
Workflow:
  1. Clarify: "Technical alignment, policy, or current events?"
  2. User: "Technical alignment for LLMs"
  3. Plan: Alignment papers → Key researchers → Techniques
  4. Execute: 4 hops, confidence 0.82
```

## Example 3: Unified with Replanning (Complex)

```bash
/sc:research "AI startup competitive analysis" --strategy unified --hops 5
```

```yaml
Workflow:
  1. Present plan: Landscape → Funding → Tech → Positioning
  2. User adjusts: "Focus on code generation, include pricing"
  3. Execute: 5 hops with mid-research replanning
  4. Low confidence (0.55) → Add Playwright for demos
  5. Final: Competitive matrix, confidence 0.85
```

## Core Patterns

### Iterative Deepening
```
Round 1: Broad landscape → Round 2: Deep dive → Round 3: Fill gaps → Round 4: Validate
```

### Source Triangulation
```
Primary (official docs) ↔ Secondary (industry) ↔ Tertiary (community) → Cross-validate
```

### Temporal Analysis
```
Historical → Current state → Future projections → Trajectory synthesis
```

## Tool Routing

| Content Type | Tool | Example |
|-------------|------|---------|
| Static content | Tavily | Blog posts, docs |
| JS-heavy sites | Playwright | Interactive demos |
| Live data | Playwright + screenshots | Pricing calculators |
| PDFs | Download + process | Academic papers |

## Quality Checklist

- [ ] Objectives defined, strategy selected
- [ ] All searches completed, extraction appropriate
- [ ] Findings integrated, contradictions resolved
- [ ] Citations complete, confidence transparent

</document>
