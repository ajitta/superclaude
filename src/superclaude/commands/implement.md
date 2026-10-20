---
description: Feature and code implementation with sub-agent delegation and MCP integration. On request only — the user's /sc:implement or a workflow step that names it. Not for a routine function, bug fix or single-file edit — edit directly.
---
<component name="implement" type="command">

  <role command="/sc:implement">
    <mission>Feature and code implementation with agent delegation and MCP integration</mission>
  </role>

  <syntax>/sc:implement [feature] [--plan docs/plans/...] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]</syntax>

  <flow>
  1. Load: If --plan given, read plan doc + extract tasks; a split plan's index is read here and each phase file it links when that phase starts, so the Checkpoint step covers the index's phase list; otherwise analyze the requirements and technical context
  2. Plan: Approach + delegate to agents; verify simplest viable approach pre-build; with --plan, follow the plan's task order exactly
  3. Checkpoint: Without --plan, changes that hit more than 3 files → show a numbered plan and wait for user approval before editing. With --plan, invoking on that plan is the approval: proceed, and ask only before departing from the plan
  4. Execute: write the code following the framework's conventions; with --plan, work through the tasks in order and check each box as the Integrate step describes
  5. Phase Gate: After each phase/task group — build + run, then: "Does this already solve the next phase's problem?" If yes, skip with reason
  6. Validate: security and quality checks; run each task's verify command
  7. Integrate: docs and test recommendations; report any blockers hit. With --plan, record every departure from the plan under a "Deviations" heading in the plan doc, in the same commit as the code, and check a box only when the code backs it (a task dropped by decision becomes `- [x] ~~task~~` with its reason under Deviations) — `status: complete` with an open box is a defect. With a split plan, a phase's Deviations go in its phase file; a finished phase file gets `status: complete` and its box in the index (linked from the phase file's header) is checked; the index gets `status: complete` when its last box is checked. The first checked box sets the plan (index) to `status: implementing`; in a feature folder, set the README `phase:` to `implementing` then and to `complete` when the plan (index) reaches `status: complete`. Before the plan (index) gets `status: complete`, run the command in its `## Proof` footer and write under it `Result: <short sha of the code it ran on> — <actual output, one line>` in the same commit. A red or unrunnable Proof keeps `status: implementing` and is reported; it closes only on the user's acceptance, recorded as `Result: <short sha> — <what failed or why not run> (accepted by user)`. When the code changes after that sha (a review fix, say), re-run the Proof and update `Result:` before claiming done again
  </flow>

  <flags>
  - --plan <path>: implement from this plan doc in its task order; unrelated to the global --plan, whose 5-line-plan directive does not apply.
  - --type component|api|service|feature: selects the checks to lead with: component → accessibility, responsive layout and component boundaries; api and service → the API contract, data integrity and error handling; feature → split into independent streams per core/rules/RULES_DELEGATION.md `<sub_agent_decision>`.
  - --framework react|vue|express: follow this framework's conventions and look up its current docs (Context7) before writing framework-facing code.
  - --safe: build the feature without changing existing exported functions, config files or shared modules; a change the feature needs there is shown first and waits for approval; unrelated to the global --safe-mode.
  - --with-tests: write tests for the new behavior with the code and run them in the Validate step.
  </flags>

  <examples>
| Input | Output |
|---|---|
| `user profile --type component --framework react` | frontend agent + best practices |
| `auth API --type api --safe --with-tests` | backend + security agents |
| `payment system --type feature --with-tests` | Multi-agent coordination |
| `dashboard widget --framework vue` | C7 Vue patterns |
  <example name="scope-creep" type="error-path">
    - Input: /sc:implement 'add logout button' (agent also refactors auth module and adds session management)
    - Why wrong: the change goes past the requested scope. "Add logout button" does not authorize refactoring adjacent code.
    - Correct: Implement only the logout button. Suggest separate tasks for the auth refactor and session management.
  </example>

  </examples>

  <gotchas>
  - status-check: Run [R02 Status Check] pre-impl. Grep for existing func first
  - scope-discipline: Build only what asked. Zero unsolicited files, zero adjacent refactors
  - workflow-fanout: fan-out subagents RETURN code/results — subprocess writes discarded; main loop applies edits and runs the >3-file checkpoint (the Checkpoint step) (full rule: core/rules/RULES_DELEGATION.md)
  </gotchas>

  <bounds>
    <does>implements following framework best practices, with full testing.</does>
    <never>makes architecture decisions without consultation, conflicts with security, or overrides safety.</never>
  </bounds>

  <handoff next="/sc:review /sc:test /sc:build"/>
</component>