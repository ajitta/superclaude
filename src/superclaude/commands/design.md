---
description: Design system architecture, APIs, and component interfaces with comprehensive specifications
---
<component name="design" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:design
    <mission>Design system architecture, APIs, and component interfaces with comprehensive specifications</mission>
  </role>

  <syntax>/sc:design [target] [--type architecture|api|component|database] [--format diagram|spec|code]</syntax>

  <triggers>
    - Architecture planning
    - API specification
    - Component design
    - Database schema design
  </triggers>

  <flow>
    1. Analyze: Requirements + existing context
    2. Plan: Design approach + structure
    3. Design: Comprehensive specs + best practices (see outputs)
    4. Validate: Requirements coverage ≥90%, maintainability check
    5. Document: Diagrams + specifications
  </flow>

  <outputs note="Per --type and --format">
| Type | diagram | spec | code |
|------|---------|------|------|
| architecture | ARCH_DIAGRAM.md | ARCHITECTURE.md | interfaces/*.ts |
| api | API_DIAGRAM.md | API_SPEC.md | openapi.yaml |
| component | COMPONENT_DIAGRAM.md | COMPONENT_SPEC.md | types/*.ts |
| database | ERD.md | SCHEMA.md | migrations/*.sql |
  </outputs>

  <checklist note="MUST complete all">
    - [ ] Design document generated per --type
    - [ ] Format matches --format flag
    - [ ] Requirements coverage validated
    - [ ] Maintainability considerations documented
  </checklist>

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
  </examples>

  <bounds will="comprehensive specs|multi-format output|validation" wont="generate impl code|modify existing arch|violate constraints"/>
</component>
