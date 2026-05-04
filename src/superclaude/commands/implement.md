---
description: Feature and code implementation with intelligent agent delegation and MCP integration
---
<component name="implement" type="command">

  <role command="/sc:implement">
    <mission>Feature and code implementation with intelligent agent delegation and MCP integration</mission>
  </role>

  <syntax>/sc:implement [feature] [--plan docs/plans/...] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]</syntax>

  <flow>
  1. Load: If --plan provided, read plan document and extract tasks; otherwise analyze requirements + tech context
  2. Plan: Approach + delegate to agents; verify simplest viable approach before building; for plan mode, follow task order exactly
  3. Checkpoint: If changes affect >3 files → present numbered plan → wait for user approval before editing
  4. Execute: Code + framework best practices; for plan mode, mark tasks complete as you go
  5. Phase Gate: After each phase/task group — build + run, then: "Does this already solve the next phase's problem?" If yes, skip with reason
  6. Validate: Security + quality checks; run verification command per task
  7. Integrate: Docs + testing recs; report any blockers encountered
  </flow>

  <tools>
  - Write/Edit: Code generation
  - Read/Grep/Glob: Project analysis
  - TaskCreate/TaskUpdate: Multi-file progress
  - Agent: Large-scale delegation
  </tools>

  <patterns>
    - Context: Framework detect → agent + MCP activation
    - Flow: Requirements → code → validation → integration
    - Multi-Agent: frontend + backend + security → comprehensive solutions
    - Quality: Impl → testing → docs → validation
  </patterns>

  <examples>
| Input | Output |
|---|---|
| `user profile --type component --framework react` | frontend agent + best practices |
| `auth API --type api --safe --with-tests` | backend + security agents |
| `payment system --type feature --with-tests` | Multi-agent coordination |
| `dashboard widget --framework vue` | C7 Vue patterns |
  <example name="scope-creep" type="error-path">
    - Input: /sc:implement 'add logout button' (agent also refactors auth module and adds session management)
    - Why wrong: Implementation exceeded requested scope. "Add logout button" does not authorize refactoring adjacent code.
    - Correct: Implement only the logout button. Suggest separate tasks for auth refactor and session management.
  </example>

  </examples>


  <gotchas>
  - status-check: Run R02 status check before implementing. Grep for existing functionality first
  - scope-discipline: Build only what was asked. Zero unsolicited files, zero adjacent refactors
  </gotchas>

  <bounds>
    <does>intelligent impl, framework best practices, and comprehensive testing.</does>
    <never>arch decisions without consultation, conflict with security, and override safety.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:test /sc:build"/>
</component>
