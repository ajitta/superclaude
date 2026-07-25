---
description: Design system architecture, APIs, component interfaces w/ comprehensive specs. Use when user type `/sc:design`, ask "design the system/API/interface for X", or want committed design spec under docs/specs/. NOT auto-trigger on "how should I structure this function", small sketches, single-component examples — those get inline answer.
---
<component name="design" type="command">

  <role command="/sc:design">
    <mission>Design system architecture, APIs, component interfaces w/ comprehensive specs</mission>
  </role>

  <syntax>/sc:design [target] [--type architecture|api|component|database] [--format diagram|spec|code]</syntax>

  <flow>
  1. Analyze: Requirements + existing context
  2. Plan: Design approach + structure
  3. Design: Comprehensive specs + best practices (see outputs)
  4. Constraints: Document operational params that constrain design — queue/buffer sizes, connection pool limits, external API batch limits, timeout values
  5. Necessity: For each proposed component, apply [R18 Necessity Test] — defer components lacking specific failure scenario, quantitative evidence, or user-facing impact
  6. Validate: Requirements coverage ≥90%, maintainability check
  7. Document: feature path `docs/features/<slug>/04-design.md`, standalone `docs/specs/<topic>-design-<username>-YYYY-MM-DD.md` — slug resolution (zero-match default `[f]`), frontmatter, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`. Plus diagrams.
  </flow>

  <outputs note="All content in single spec file per invocation">
| Artifact | Content |
|---|---|
| Feature path: `docs/features/<slug>/04-design.md` | Phase doc when slug resolves to existing/new feature folder |
| Standalone path: `docs/specs/<topic>-design-<username>-YYYY-MM-DD.md` | One-off design, no related work expected |
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

  <examples>
| Input | Output |
|---|---|
| `user-mgmt --type architecture --format diagram` | System architecture |
| `payment-api --type api --format spec` | API specification |
| `notification-service --type component --format code` | Component interface |
| `e-commerce-db --type database --format diagram` | Schema design |
  <example name="design-without-requirements" type="error-path">
    - Input: /sc:design payment-api --type api (no context about payment provider or requirements)
    - Why wrong: Design w/o requirements lead to assumptions that may not match business needs.
    - Correct: /sc:brainstorm 'payment system requirements' first → then /sc:design w/ concrete requirements
  </example>

  </examples>


  <gotchas>
  - over-architect: Apply R18 necessity test to each proposed component. Only design what needed now
  - existing-check: Check if design doc already exist for this topic before creating new one
  - workflow-fanout: fan-out subagents RETURN design markdown — subprocess writes discarded; main loop performs the Write per outputs routing (full rule: core/rules/RULES_DELEGATION.md)
  </gotchas>

  <bounds>
    <does>comprehensive specs, multi-format output, validation.</does>
    <never>generate impl code, modify existing arch, violate constraints.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:plan /sc:implement /sc:roadmap"/>
</component>