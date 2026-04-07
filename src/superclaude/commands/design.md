---
description: Design system architecture, APIs, and component interfaces with comprehensive specifications
---
<component name="design" type="command">

  <role>
    /sc:design
    <mission>Design system architecture, APIs, and component interfaces with comprehensive specifications</mission>
  </role>

  <syntax>/sc:design [target] [--type architecture|api|component|database] [--format diagram|spec|code]</syntax>

  <flow>
    1. Analyze: Requirements + existing context
    2. Plan: Design approach + structure
    3. Design: Comprehensive specs + best practices (see outputs)
    4. Constraints: Document operational parameters that constrain design — queue/buffer sizes, connection pool limits, external API batch limits, timeout values
    5. Necessity: For each proposed component, apply [R18] — defer components that lack a specific failure scenario, quantitative evidence, or user-facing impact
    6. Validate: Requirements coverage ≥90%, maintainability check
    7. Document: Save design spec to docs/specs/<topic>-design-<username>-YYYY-MM-DD.md (with frontmatter: status: draft, revised: <today>) + diagrams
  </flow>

  <outputs note="All content in single spec file per invocation">
| Artifact | Content |
|----------|---------|
| `docs/specs/<topic>-design-<username>-YYYY-MM-DD.md` | Diagram + spec + interface definitions |
  Sections per --type:
  - architecture: system diagram, component boundaries, interface contracts
  - api: endpoint diagram, request/response specs, OpenAPI schema
  - component: component diagram, prop/state specs, type definitions
  - database: ERD, schema definitions, migration plan
  </outputs>


  <tools>
    - Read: Requirements analysis
    - Grep/Glob: System structure investigation
    - Write: Design documentation
    - Bash: External design tools
  </tools>

  <patterns>
    - Architecture: Requirements → structure → scalability
    - API: Interface spec → REST/GraphQL → docs
    - Component: Functional reqs → interface → guidance
    - Database: Data reqs → schema → relationships
  </patterns>

  <examples>
| Input | Output |
|-------|--------|
| `user-mgmt --type architecture --format diagram` | System architecture |
| `payment-api --type api --format spec` | API specification |
| `notification-service --type component --format code` | Component interface |
| `e-commerce-db --type database --format diagram` | Schema design |
  <example name="design-without-requirements" type="error-path">
    <input>/sc:design payment-api --type api (with no context about payment provider or requirements)</input>
    <why_wrong>Designing without requirements leads to assumptions that may not match business needs.</why_wrong>
    <correct>/sc:brainstorm 'payment system requirements' first → then /sc:design with concrete requirements</correct>
  </example>

  </examples>

  <bounds should="comprehensive specs|multi-format output|validation" avoid="generate impl code|modify existing arch|violate constraints" fallback="Ask user for guidance when uncertain">

    Produce design documentation, then complete | Defer implementation code to /sc:implement | Defer source file creation to /sc:implement | Design specs and interfaces only → Output: Architecture/API/Component/Database design documents

  </bounds>

  <handoff next="/sc:plan /sc:implement /sc:workflow"/>
</component>
