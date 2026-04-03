---
description: Execute complex tasks with intelligent workflow management and delegation
---
<component name="task" type="command">

  <role>
    /sc:task
    <mission>Execute complex tasks with intelligent workflow management and delegation</mission>
  </role>

  <syntax>/sc:task [action] [target] [--strategy sequential|parallel|adaptive] [--delegate] [--cleanup]</syntax>

  <flow>
    1. Analyze: Parse requirements + dependency mapping
    2. Decompose: Break into Epic → Story → Task hierarchy
    3. Strategy: Select execution order (sequential for deps, parallel for independent, adaptive for mixed)
    4. Checkpoint: If changes affect >3 files → present numbered plan → wait for user approval
    5. Execute: Intelligent delegation + parallel where possible
    6. Validate: Quality gates + completion verification
    7. Cleanup: Auto-remove stale/completed tasks (--cleanup)
  </flow>

  <task_cleanup note="Claude Code 2.1.37+">
    <description>Automatic task cleanup via TaskUpdate delete feature</description>
    <cleanable_states>
      - completed: Successfully finished tasks
      - cancelled: User-cancelled tasks
      - stale: Pending > 24 hours without progress
      - blocked: Tasks blocked by unresolved dependencies
    </cleanable_states>
    <usage>
      - /sc:task cleanup: Run automatic task cleanup
      - /sc:task cleanup --dry-run: Preview without deletion
    </usage>
  </task_cleanup>

  <tools>
    - TaskCreate/TaskUpdate: Epic → Story → Task hierarchy
    - Agent: Sub-agent delegation for parallel work
    - Read/Write/Edit: Implementation + coordination
    - Grep/Glob: Dependency mapping
  </tools>

  <patterns>
    - Hierarchy: Epic → Story → Task → Subtask
    - Strategy: Sequential (strict deps) | Parallel (independent streams) | Adaptive (discover then parallelize)
    - Dependency: Analyze dependencies before execution — detect circular deps, present resolution options
    - Cleanup: Stale detection → auto-delete → report
  </patterns>

  <examples>

  <example name="sequential-strategy" type="happy-path">
    <input>/sc:task 'database migration from MySQL to PostgreSQL' --strategy sequential</input>
    <output>
      Epic: MySQL → PostgreSQL migration
        Story 1: Schema migration (blocked: none)
        Story 2: Data migration (blocked by: Story 1)
        Story 3: Application layer (blocked by: Story 2)
      Dependencies: S1 → S2 → S3 (strict chain)
    </output>
  </example>

  <example name="parallel-strategy" type="happy-path">
    <input>/sc:task 'implement user auth system' --strategy parallel</input>
    <output>
      Epic: User authentication system
        Story 1: Database layer (parallel)
        Story 2: API layer (parallel)
        Story 3: UI layer (parallel)
        Story 4: Integration (blocked by: S1 + S2 + S3)
      Concurrency: S1 ‖ S2 ‖ S3 → S4
    </output>
  </example>

  <example name="adaptive-strategy" type="happy-path">
    <input>/sc:task 'refactor monolith into services' --strategy adaptive</input>
    <output>
      Phase 1 (sequential — discovery): Analyze dependencies, identify bounded contexts
      Phase 2 (parallel — independent services): Extract UserService ‖ OrderService ‖ PaymentService
      Phase 3 (sequential — integration): API gateway + integration testing
      Strategy shift: Sequential → Parallel → Sequential
    </output>
  </example>

  <example name="circular-dependency" type="error-path">
    <input>/sc:task 'refactor auth and permissions modules'</input>
    <why_wrong>Circular dependency detected: auth → permissions → auth</why_wrong>
    <correct>Present options: A) Extract shared interface to break cycle, B) Merge into single module. User chooses before proceeding.</correct>
  </example>

| Input | Output |
|-------|--------|
| `cleanup` | Auto-remove stale/completed tasks |
| `cleanup --dry-run` | Preview cleanup without deletion |

  </examples>

  <token_note>High consumption with --delegate — spawns sub-agents; consider fresh session for large tasks</token_note>

  <bounds will="complex task coordination|hierarchical breakdown|dependency analysis|auto cleanup" wont="simple single-file tasks|compromise quality|operate without validation" fallback="Ask user for guidance when uncertain">

    Execute tasks via intelligent delegation | Quality gates enforced between phases | Progress reported via TaskCreate/TaskUpdate | Detect circular dependencies before execution

  </bounds>

  <handoff next="/sc:test /sc:implement"/>
</component>
