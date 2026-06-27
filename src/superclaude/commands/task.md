---
description: Execute complex tasks with intelligent workflow management and delegation. Use when user types `/sc:task` or hands over complex multi-step task needing explicit tracking and sub-agent delegation. Do NOT auto-trigger on single-step actions, small TODOs, or "do X" — those execute directly.
---
<component name="task" type="command">

  <role command="/sc:task">
    <mission>Execute complex tasks with intelligent workflow management and delegation</mission>
  </role>

  <syntax>/sc:task [action] [target] [--strategy sequential|parallel|adaptive] [--delegate] [--cleanup]</syntax>

  <flow>
  1. Analyze: Parse requirements + dependency mapping
  2. Decompose: Break into Epic → Story → Task hierarchy
  3. Strategy: Pick execution order (sequential for deps, parallel for independent, adaptive for mixed)
  4. Checkpoint: Changes affect >3 files → present numbered plan → wait for user approval
  5. Execute: Intelligent delegation + parallel where possible
  6. Validate: Quality gates + completion verification
  7. Cleanup: Auto-remove stale/completed tasks (--cleanup)
  </flow>

  <task_cleanup note="Claude Code 2.1.37+">
    <description>Auto task cleanup via TaskUpdate delete feature</description>
    <cleanable_states>
      - completed: Finished tasks
      - cancelled: User-cancelled tasks
      - stale: Pending > 24 hours, no progress
      - blocked: Tasks blocked by unresolved deps
    </cleanable_states>
    <usage>
      - /sc:task cleanup: Run auto task cleanup
      - /sc:task cleanup --dry-run: Preview, no deletion
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
    - Dependency: Analyze deps before execution — detect circular deps, present resolution options
    - Cleanup: Stale detection → auto-delete → report
  </patterns>

  <examples>

  <example name="adaptive-strategy" type="happy-path">
    - Input: /sc:task 'refactor monolith into services' --strategy adaptive
  </example>

  <example name="circular-dependency" type="error-path">
    - Input: /sc:task 'refactor auth and permissions modules'
    - Why wrong: Circular dep detected: auth → permissions → auth
    - Correct: Present options: A) Extract shared interface to break cycle, B) Merge into single module. User chooses before proceeding.
  </example>

| Input | Output |
|---|---|
| `cleanup` | Auto-remove stale/completed tasks |
| `cleanup --dry-run` | Preview cleanup, no deletion |

  </examples>


  <gotchas>
  - task-count: No excessive sub-tasks. Break into 3-7 tasks max per feature
  - already-done: Check git log and existing code before creating implementation tasks
  - workflow-task-state: Under ultracode Workflow fan-out, harness task-state may not survive the subagent boundary — the main loop owns TaskCreate/TaskUpdate and the >3-file approval checkpoint (flow step 4); subagents return task results and cannot pause for input
  </gotchas>

  <bounds>
    <does>complex task coordination, hierarchical breakdown, dependency analysis, auto cleanup.</does>
    <never>simple single-file tasks, compromise quality, operate without validation.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:test /sc:implement"/>
</component>