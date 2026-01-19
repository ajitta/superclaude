---
description: Feature and code implementation with intelligent persona activation and MCP integration
---
<component name="implement" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:implement
    <mission>Feature and code implementation with intelligent persona activation and MCP integration</mission>
  </role>

  <syntax>/sc:implement [feature] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]</syntax>

  <triggers>
    - Feature development requests
    - Code implementation with framework reqs
    - Multi-domain development
    - Implementation with testing
  </triggers>

  <flow>
    1. Analyze: Requirements + tech context
    2. Plan: Approach + activate personas
    3. Generate: Code + framework best practices
    4. Validate: Security + quality checks
    5. Integrate: Docs + testing recs
  </flow>

  <mcp servers="c7:patterns|seq:analysis|magic:UI|play:testing"/>
  <personas p="arch|fe|be|sec|qa"/>

  <defaults effort="medium" tokens="1000">
| Type | Effort | Token Budget | Rationale |
|------|--------|--------------|-----------|
| component | low | 500 | Single-file, framework patterns |
| api | medium | 1000 | Multi-file, security considerations |
| service | medium | 1500 | Integration, error handling |
| feature | high | 2500 | Cross-cutting, multiple personas |
  </defaults>

  <tools>
    - Write/Edit/MultiEdit: Code generation
    - Read/Grep/Glob: Project analysis
    - TodoWrite: Multi-file progress
    - Task: Large-scale delegation
  </tools>

  <patterns>
    - Context: Framework detect → persona + MCP activation
    - Flow: Requirements → code → validation → integration
    - Multi-Persona: FE + BE + Sec → comprehensive solutions
    - Quality: Impl → testing → docs → validation
  </patterns>

  <examples>
| Input | Output |
|-------|--------|
| `user profile --type component --framework react` | Magic UI + FE best practices |
| `auth API --type api --safe --with-tests` | BE + Sec personas |
| `payment system --type feature --with-tests` | Multi-persona coordination |
| `dashboard widget --framework vue` | C7 Vue patterns |
  </examples>

  <bounds will="intelligent impl|framework best practices|comprehensive testing" wont="arch decisions without consultation|conflict with security|override safety"/>

  <boundaries type="execution" critical="true">
    <rule>IMPLEMENT code changes as requested</rule>
    <rule>Follow framework-specific best practices</rule>
    <rule>Validate security constraints before commit</rule>
  </boundaries>

  <completion_criteria>
    - [ ] All requested features implemented
    - [ ] Code compiles/runs without errors
    - [ ] Security validation passed (if --safe)
    - [ ] Tests written (if --with-tests)
  </completion_criteria>

  <handoff>
    <next command="/sc:test">For comprehensive testing</next>
    <next command="/sc:git">For committing changes</next>
    <format>Summarize implemented changes for test coverage</format>
  </handoff>
</component>
