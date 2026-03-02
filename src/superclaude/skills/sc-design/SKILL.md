---
name: sc-design
description: >-
  This skill should be used when the user asks to
  "design the system architecture",
  "create an API specification",
  "design component interfaces",
  "database schema design",
  "design the data model",
  "create architecture diagram",
  "design the API",
  "component interface design".
version: 1.0.0
metadata:
  context: inline
  agent: system-architect
  mcp: seq
  allowed-tools:
    - Read
    - Grep
    - Glob
    - Write
    - Bash
---
<component name="sc-design" type="skill">

  <role>
    <mission>Design system architecture, APIs, and component interfaces with comprehensive specifications</mission>
  </role>

  <syntax>/sc:design [target] [--type architecture|api|component|database] [--format diagram|spec|code]</syntax>

  <flow>
    1. Gather: Read requirements, scan existing codebase for patterns and constraints
    2. Analyze: Identify design drivers (scalability, performance, maintainability, security)
    3. Design: Create comprehensive specification per --type with best practices applied
    4. Validate: Check requirements coverage ≥90%, verify consistency with existing architecture
    5. Document: Output in requested --format with diagrams, specs, or interface code
  </flow>

  <design_outputs note="Per --type and --format">
| Type | diagram | spec | code |
|------|---------|------|------|
| architecture | ARCH_DIAGRAM.md | ARCHITECTURE.md | interfaces/*.ts |
| api | API_DIAGRAM.md | API_SPEC.md | openapi.yaml |
| component | COMPONENT_DIAGRAM.md | COMPONENT_SPEC.md | types/*.ts |
| database | ERD.md | SCHEMA.md | migrations/*.sql |
  </design_outputs>

  <validation_checklist>
    - Requirements coverage: ≥90% of stated requirements addressed
    - Consistency: No conflicts with existing architecture decisions
    - Scalability: Design handles 10x current load without restructuring
    - Security: OWASP considerations addressed where applicable
    - Maintainability: Clear separation of concerns, documented interfaces
  </validation_checklist>

  <patterns>
    - Architecture: Requirements → component decomposition → interaction patterns → scalability plan
    - API: Resource identification → endpoint design → request/response schemas → error handling
    - Component: Functional requirements → interface contracts → dependency management → testing strategy
    - Database: Data requirements → entity relationships → normalization → indexing strategy
  </patterns>

  <examples>
| Input | Output |
|-------|--------|
| `user-mgmt --type architecture --format diagram` | System architecture diagram in Mermaid |
| `payment-api --type api --format spec` | OpenAPI specification with examples |
| `notification-service --type component --format code` | TypeScript interface definitions |
| `e-commerce-db --type database --format diagram` | ERD with relationship annotations |
| (auto-trigger) "design the system architecture" | Skill activates, gathers requirements, designs |
| (auto-trigger) "create an API spec" | Skill activates, runs API design pattern |

  <example name="design-without-requirements" type="error-path">
    <input>/sc:design payment-api --type api (with no context about payment provider or requirements)</input>
    <why_wrong>Designing without requirements leads to assumptions that may not match business needs.</why_wrong>
    <correct>/sc:brainstorm 'payment system requirements' first → then /sc:design with concrete requirements</correct>
  </example>
  </examples>

  <bounds will="comprehensive specs|multi-format output|validation checklist|architecture diagrams" wont="generate implementation code|modify existing architecture without approval|violate stated constraints" fallback="Ask user for requirements clarification when design scope is ambiguous"/>

  <handoff next="/sc:implement /sc:workflow"/>
</component>
