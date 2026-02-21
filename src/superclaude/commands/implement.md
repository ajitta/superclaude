---
description: Feature and code implementation with intelligent persona activation and MCP integration
---
<component name="implement" type="command">

  <role>
    /sc:implement
    <mission>Feature and code implementation with intelligent persona activation and MCP integration</mission>
  </role>

  <syntax>/sc:implement [feature] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]</syntax>

  <triggers>feature development|code implementation|multi-domain dev|implementation with testing</triggers>

  <flow>
    1. Analyze: Requirements + tech context
    2. Plan: Approach + activate personas
    3. Checkpoint: If changes affect >3 files → present numbered plan → wait for user approval before editing
    4. Generate: Code + framework best practices
    5. Validate: Security + quality checks
    6. Integrate: Docs + testing recs
  </flow>

  <mcp servers="c7|seq|magic|play"/>
  <personas p="arch|fe|be|sec|qa"/>

  <defaults effort="medium">
| Type | Effort | Token Budget | Rationale |
|------|--------|--------------|-----------|
| component | low | 500 | Single-file, framework patterns |
| api | medium | 1000 | Multi-file, security considerations |
| service | medium | 1500 | Integration, error handling |
| feature | high | 2500 | Cross-cutting, multiple personas |
  </defaults>

  <tools>
    - Write/Edit: Code generation
    - Read/Grep/Glob: Project analysis
    - TaskCreate/TaskUpdate: Multi-file progress
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

  <token_note>Medium-high consumption — use --delegate for large features to distribute across subagents</token_note>

  <bounds will="intelligent impl|framework best practices|comprehensive testing" wont="arch decisions without consultation|conflict with security|override safety" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="execution">Implement code changes as requested | Follow framework-specific best practices | Validate security constraints before commit</boundaries>




  <handoff next="/sc:test /sc:git"/>
</component>
