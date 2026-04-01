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
    4. Validate: Requirements coverage ≥90%, maintainability check
    5. Document: Save design spec to docs/specs/<topic>-design-<username>-YYYY-MM-DD.md (with frontmatter: status: draft, revised: <today>) + diagrams
  </flow>

  <outputs note="Per --type and --format">
| Type | diagram | spec | code |
|------|---------|------|------|
| architecture | ARCH_DIAGRAM.md | ARCHITECTURE.md | interfaces/*.ts |
| api | API_DIAGRAM.md | API_SPEC.md | openapi.yaml |
| component | COMPONENT_DIAGRAM.md | COMPONENT_SPEC.md | types/*.ts |
| database | ERD.md | SCHEMA.md | migrations/*.sql |
  </outputs>

  <mcp servers="seq|c7"/>
  <personas p="arch|fe|be|anal"/>

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

  <token_note>Medium-high consumption — scales with --type complexity; use --format spec for lighter output</token_note>

  <bounds will="comprehensive specs|multi-format output|validation" wont="generate impl code|modify existing arch|violate constraints" fallback="Ask user for guidance when uncertain" type="document-only">

    Produce design documentation, then complete | Defer implementation code to /sc:implement | Defer source file creation to /sc:implement | Design specs and interfaces only → Output: Architecture/API/Component/Database design documents

  </bounds>

  <handoff next="/sc:implement /sc:workflow"/>
</component>
