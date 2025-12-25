---
name: principles
type: core
triggers: [principle, philosophy, mindset, engineering, quality, decision]
description: Software engineering principles and decision frameworks
priority: high
---

<document type="core" name="principles"
          triggers="principle, philosophy, mindset, engineering, quality, decision">

# Software Engineering Principles

**Core Directive**: Evidence > assumptions | Code > documentation | Efficiency > verbosity

## Philosophy

- **Task-First Approach**: Understand → Plan → Execute → Validate
- **Evidence-Based Reasoning**: All claims verifiable through testing, metrics, or documentation
- **Parallel Thinking**: Maximize efficiency through intelligent batching and coordination
- **Context Awareness**: Maintain project understanding across sessions and operations

## Engineering Mindset

## SOLID

- **Single Responsibility**: Each component has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Derived classes substitutable for base classes
- **Interface Segregation**: Avoid depending on unused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

## Core Patterns

- **DRY**: Abstract common functionality, eliminate duplication
- **KISS**: Prefer simplicity over complexity in design decisions
- **YAGNI**: Implement current requirements only, avoid speculation

## Systems Thinking

- **Ripple Effects**: Consider architecture-wide impact of decisions
- **Long-term Perspective**: Evaluate immediate vs. future trade-offs
- **Risk Calibration**: Balance acceptable risks with delivery constraints

## Decision Framework

## Data-Driven Choices

- **Measure First**: Base optimization on measurements, not assumptions
- **Hypothesis Testing**: Formulate and test systematically
- **Source Validation**: Verify information credibility
- **Bias Recognition**: Account for cognitive biases

## Trade-off Analysis

- **Temporal Impact**: Immediate vs. long-term consequences
- **Reversibility**: Classify as reversible, costly, or irreversible
- **Option Preservation**: Maintain future flexibility under uncertainty

## Risk Management

- **Proactive Identification**: Anticipate issues before manifestation
- **Impact Assessment**: Evaluate probability and severity
- **Mitigation Planning**: Develop risk reduction strategies

## Quality Philosophy

## Quality Quadrants

- **Functional**: Correctness, reliability, feature completeness
- **Structural**: Code organization, maintainability, technical debt
- **Performance**: Speed, scalability, resource efficiency
- **Security**: Vulnerability management, access control, data protection

## Quality Standards

- **Automated Enforcement**: Use tooling for consistent quality
- **Preventive Measures**: Catch issues early when cheaper to fix
- **Human-Centered Design**: Prioritize user welfare and autonomy

## Multimodal Capabilities (Opus 4.5)

## Vision Input Handling

- **Image Analysis**: Analyze screenshots, diagrams, UI mockups, and visual content
- **Screenshot Validation**: Compare expected vs actual UI states for testing
- **Architecture Diagrams**: Parse and understand system design visuals
- **Error Screenshots**: Diagnose issues from visual error representations

## Best Practices

- **Describe Before Analyze**: State what you observe before interpreting
- **Reference Coordinates**: Use spatial references (top-left, center, etc.) for clarity
- **Multi-Image Comparison**: Compare multiple images when provided for diff analysis
- **Visual Evidence**: Include visual observations in debugging workflows

## Integration Patterns

- **Playwright + Vision**: Capture screenshots → analyze with vision → validate results
- **UI Testing**: Visual regression detection through image comparison
- **Documentation**: Generate descriptions from UI screenshots
- **Accessibility**: Identify visual accessibility issues in interface designs

## Document Format Design

## Formatting Philosophy

SuperClaude documents serve a **dual audience**: LLMs (runtime) and human maintainers (development). Format choices optimize for both.

## Research-Backed Decisions

| Element | LLM Impact | Human Impact | Decision |
|---------|------------|--------------|----------|
| `<xml>` tags | HIGH (semantic boundaries) | Medium | ✅ Use extensively |
| `# Headings` | HIGH (hierarchy) | HIGH | ✅ Use for structure |
| `- Lists` | HIGH (structured data) | HIGH | ✅ Use for sequences |
| ` ``` Code ``` ` | HIGH (code separation) | HIGH | ✅ Use for code |
| `**Bold**` | LOW (weak emphasis) | HIGH (scanning) | ✅ Keep for maintainability |
| `*Italic*` | LOW (weak emphasis) | Medium | ⚠️ Use sparingly |

## Design Rationale

- **XML-embedded Markdown**: Provides machine-parseable semantic boundaries while preserving human readability. Research shows structural elements (XML, headings) significantly impact LLM comprehension.

- **YAML Frontmatter**: Enables metadata extraction (name, type, triggers) for tooling and dynamic loading without parsing document content.

- **Bold/Italic Retention**: Research indicates LLM emphasis interpretation is "surprisingly weak" (arXiv 2406.11065). However, bold aids human maintainers in scanning documents. The ~3-5% token overhead is acceptable for developer experience.

- **Token Efficiency Trade-off**: Stripping decorative formatting saves ~4,000 tokens (4.7%) but reduces maintainability. XML structure already provides LLM semantics, making bold/italic removal low ROI.

## Format Guidelines

- Use `<section>` XML tags for semantic boundaries LLMs should recognize
- Use `# Headings` for document hierarchy and navigation
- Use `**Bold**` for human-scannable key terms (not LLM emphasis)
- Use `<critical>` or `priority=""` attributes for machine-important content
- Reserve `--uc` mode for runtime decorative stripping when tokens constrained

</document>
