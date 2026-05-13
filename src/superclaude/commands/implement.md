---
description: Feature + code impl w/ smart agent delegate + MCP. Use ONLY when user explicit type `/sc:implement` — run multi-step impl flow w/ sub-agent delegate. NO auto-trigger on routine "add func", "fix bug", or single-file edit — handle direct w/o implement orchestrate.
---
<component name="implement" type="command">

  <role command="/sc:implement">
    <mission>Feature + code impl w/ smart agent delegate + MCP integration</mission>
  </role>

  <syntax>/sc:implement [feature] [--plan docs/plans/...] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]</syntax>

  <flow>
  1. Load: If --plan given, read plan doc + extract tasks; else analyze reqs + tech context
  2. Plan: Approach + delegate to agents; verify simplest viable approach pre-build; for plan mode, follow task order exact
  3. Checkpoint: If changes hit >3 files → show numbered plan → wait user approval pre-edit
  4. Execute: Code + framework best practices; for plan mode, mark tasks done as go
  5. Phase Gate: After each phase/task group — build + run, then: "Does this already solve the next phase's problem?" If yes, skip w/ reason
  6. Validate: Security + quality checks; run verify cmd per task
  7. Integrate: Docs + test recs; report any blockers hit
  </flow>

  <tools>
  - Write/Edit: Code gen
  - Read/Grep/Glob: Project analysis
  - TaskCreate/TaskUpdate: Multi-file progress
  - Agent: Large-scale delegate
  </tools>

  <patterns>
    - Context: Framework detect → agent + MCP activate
    - Flow: Reqs → code → validate → integrate
    - Multi-Agent: frontend + backend + security → full solutions
    - Quality: Impl → test → docs → validate
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
    - Why wrong: Impl past requested scope. "Add logout button" no authorize refactor adjacent code.
    - Correct: Impl only logout button. Suggest separate tasks for auth refactor + session mgmt.
  </example>

  </examples>


  <gotchas>
  - status-check: Run R02 status check pre-impl. Grep for existing func first
  - scope-discipline: Build only what asked. Zero unsolicited files, zero adjacent refactors
  </gotchas>

  <bounds>
    <does>smart impl, framework best practices, + full testing.</does>
    <never>arch decisions w/o consult, conflict w/ security, + override safety.</never>
    <fallback>Ask user guidance when unsure.</fallback>
  </bounds>

  <handoff next="/sc:test /sc:build"/>
</component>