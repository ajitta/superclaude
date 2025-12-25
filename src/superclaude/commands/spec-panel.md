---
name: spec-panel
type: command
triggers: [/sc:spec-panel, specification-review, expert-panel, requirements-analysis]
description: "Multi-expert specification review and improvement using renowned specification and software engineering experts"
category: analysis
complexity: enhanced
mcp-servers: [sequential, context7]
personas: [technical-writer, system-architect, quality-engineer]
---

<document type="command" name="spec-panel"
          triggers="/sc:spec-panel, specification-review, expert-panel">

# /sc:spec-panel - Expert Specification Review Panel

## Usage
```
/sc:spec-panel [spec|@file] [--mode discussion|critique|socratic] [--experts "name1,name2"] [--focus requirements|architecture|testing|compliance] [--iterations N]
```

## Behavioral Flow
Analyze spec → Assemble experts → Multi-expert review → Collaborate → Synthesize → Improve

## Expert Panel

| Expert | Domain | Key Question |
|--------|--------|--------------|
| **Karl Wiegers** | Requirements quality, SMART criteria | "How would you validate this in production?" |
| **Gojko Adzic** | BDD, Given/When/Then | "Can you provide concrete examples?" |
| **Alistair Cockburn** | Use cases, goals | "Who is the primary stakeholder?" |
| **Martin Fowler** | API design, patterns | "Consider separating concerns here." |
| **Michael Nygard** | Production reliability | "What happens when this fails?" |
| **Sam Newman** | Microservices | "How does this handle service evolution?" |
| **Lisa Crispin** | Testing strategies | "How would testing validate this?" |
| **Kelsey Hightower** | Cloud native, K8s | "How does this handle cloud deployment?" |

## Analysis Modes

| Mode | Purpose | Pattern |
|------|---------|---------|
| `discussion` | Collaborative improvement | Sequential expert dialogue building on insights |
| `critique` | Systematic review | Issue identification → Severity → Recommendation → Priority |
| `socratic` | Learning-focused | Deep questioning to surface assumptions |

## Focus Areas

| Focus | Lead Experts | Analysis |
|-------|-------------|----------|
| `requirements` | Wiegers, Adzic, Cockburn | Clarity, testability, acceptance criteria |
| `architecture` | Fowler, Newman, Nygard | Interface design, boundaries, patterns |
| `testing` | Crispin, Adzic | Test strategy, edge cases, validation |
| `compliance` | Wiegers, Nygard | Security, regulatory, audit trails |

## MCP Integration
- **Sequential**: Expert panel coordination
- **Context7**: Specification patterns and best practices

## Output Format

```yaml
quality_assessment:
  overall_score: 7.2/10
  requirements_quality: 8.1/10
  testability_score: 7.5/10

critical_issues:
  - severity: high
    expert: wiegers
    issue: "Timeout not specified"
    recommendation: "Define session timeout"

improvement_roadmap:
  immediate: ["Define timeouts", "Add error scenarios"]
  short_term: ["Monitoring requirements"]
```

## Examples

```bash
/sc:spec-panel @auth_api.yml --mode critique --focus requirements,architecture
/sc:spec-panel "user story" --mode discussion --experts "wiegers,adzic"
/sc:spec-panel @system.yml --mode socratic --iterations 3
```

## Boundaries

**Will**: Expert-level review, actionable recommendations, multi-mode analysis
**Will Not**: Replace human judgment, modify without consent, provide legal guarantees

</document>
