---
description: Meta-system task orchestration with intelligent breakdown and delegation
---
<component name="spawn" type="command">

  <role>
    /sc:spawn
    <mission>Meta-system task orchestration with intelligent breakdown and delegation</mission>
  </role>

  <syntax>/sc:spawn [complex-task] [--strategy sequential|parallel|adaptive] [--depth normal|deep]</syntax>

  <flow>
    1. Analyze: Complex op requirements + scope
    2. Decompose: Epic → Story → Task → Subtask
    3. Orchestrate: Execute via --strategy
    4. Monitor: Progress + dependency management
    5. Integrate: Aggregate results + summary
  </flow>

  <outputs note="Per execution">
| Artifact | Purpose |
|----------|---------|
| TaskCreate/TaskUpdate hierarchy | Task breakdown tracking |
| SPAWN_PLAN.md | Execution strategy doc |
| SPAWN_RESULT.md | Aggregated results |
  </outputs>

  <mcp servers="seq|c7|serena"/>
  <mcp_routing>
    1. Sequential: task decomposition reasoning, dependency graph analysis
    2. Context7: tech stack validation for sub-tasks
    3. Serena: cross-session task state, prior spawn recall
  </mcp_routing>

  <tools>
    - TaskCreate/TaskUpdate: Hierarchical breakdown (Epic→Story→Task)
    - Read/Grep/Glob: Dependency mapping
    - Edit/Write: Coordinated file ops
    - Bash: System-level coordination
  </tools>

  <patterns>
    - Hierarchy: Epic → Story → Task → Subtask granularity
    - Strategy: Sequential (deps) | Parallel (independent) | Adaptive (dynamic)
    - Meta: Cross-domain → resource opt → result integration
    - Enhancement: Systematic → quality gates → validation
  </patterns>

  <examples>

  <example name="sequential-strategy" type="happy-path">
    <input>/sc:spawn 'database migration from MySQL to PostgreSQL' --strategy sequential</input>
    <reasoning>Strict ordering required (schema first, then data, then app changes) → sequential</reasoning>
    <output>
      Epic: MySQL → PostgreSQL migration
        Story 1: Schema migration (blocked: none)
          Task 1.1: Generate PostgreSQL schema from MySQL dump
          Task 1.2: Adapt data types (AUTO_INCREMENT → SERIAL, etc.)
          Task 1.3: Validate schema compatibility
        Story 2: Data migration (blocked by: Story 1)
          Task 2.1: Export MySQL data
          Task 2.2: Transform and import to PostgreSQL
          Task 2.3: Verify row counts and integrity
        Story 3: Application layer (blocked by: Story 2)
          Task 3.1: Update ORM config and queries
          Task 3.2: Integration tests against PostgreSQL
      Dependencies: S1 → S2 → S3 (strict chain)
    </output>
  </example>

  <example name="parallel-strategy" type="happy-path">
    <input>/sc:spawn 'implement user auth system' --strategy parallel</input>
    <reasoning>Independent work streams (DB, API, UI) can run concurrently → parallel</reasoning>
    <output>
      Epic: User authentication system
        Story 1: Database layer (parallel)
          Task 1.1: User table schema + migrations
          Task 1.2: Session/token storage
        Story 2: API layer (parallel)
          Task 2.1: /auth/login, /auth/register endpoints
          Task 2.2: JWT middleware
          Task 2.3: Password hashing
        Story 3: UI layer (parallel)
          Task 3.1: Login/register forms
          Task 3.2: Auth state management
        Story 4: Integration (blocked by: S1 + S2 + S3)
          Task 4.1: E2E auth flow tests
          Task 4.2: Security audit
      Concurrency: S1 ‖ S2 ‖ S3 → S4
    </output>
  </example>

  <example name="adaptive-strategy" type="happy-path">
    <input>/sc:spawn 'migrate monolith to microservices' --strategy adaptive --depth deep</input>
    <reasoning>Unknown scope, deep analysis needed → starts sequential, discovers parallelism</reasoning>
    <output>
      Epic: Monolith decomposition
        Phase 1 (sequential — discovery):
          Task: Analyze monolith dependencies (Serena symbol analysis)
          Task: Identify bounded contexts
          Task: Map inter-service communication
        Phase 2 (parallel — discovered independent services):
          Story A: Extract UserService ‖ Story B: Extract OrderService ‖ Story C: Extract PaymentService
        Phase 3 (sequential — integration):
          Task: API gateway routing
          Task: Integration testing
      Strategy shift: Sequential (phase 1) → Parallel (phase 2) → Sequential (phase 3)
    </output>
  </example>

  <example name="circular-dependency" type="error-path">
    <input>/sc:spawn 'refactor auth and permissions modules'</input>
    <reasoning>Analysis reveals auth depends on permissions, permissions depends on auth → circular</reasoning>
    <output>
      Epic: Auth + permissions refactor
      Dependency analysis: auth → permissions → auth (CIRCULAR)
      Recovery: "Circular dependency detected between auth and permissions modules."
        Option A: Extract shared interface to break cycle → 3 stories
        Option B: Merge into single auth-permissions module → 2 stories
      Action: Present options to user before proceeding
    </output>
  </example>

  </examples>

  <token_note>Very high consumption — spawns multiple subagents; one major spawn per session recommended</token_note>

  <bounds will="multi-domain decomposition|intelligent orchestration|meta-system ops" wont="replace domain commands|override user strategy|execute without analysis" fallback="Ask user for guidance when uncertain" type="document-only">

    Produce task hierarchy document, then complete | Defer implementation to /sc:task or /sc:implement | Orchestration planning only → Output: SPAWN_PLAN.md with task breakdown and dependencies

  </bounds>

  <handoff next="/sc:task /sc:implement"/>
</component>
