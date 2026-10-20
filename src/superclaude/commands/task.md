---
description: Execute complex tasks as a tracked Epic → Story → Task hierarchy with sub-agent delegation. On request only — the user's /sc:task or a workflow step that names it. Not for single-step actions or small TODOs — do them directly; parallel streams — /sc:pm; one task from scope to review — /sc:agent.
---
<component name="task" type="command">

  <role command="/sc:task">
    <mission>Execute complex tasks with intelligent workflow management and delegation</mission>
  </role>

  <syntax>/sc:task [action] [target] [--strategy sequential|parallel|adaptive] [--delegate] [--cleanup] [--dry-run]</syntax>

  <flow>
  1. Analyze: Parse requirements + dependency mapping
  2. Decompose: Break into Epic → Story → Task hierarchy; each task starts open with an empty evidence note in its TaskCreate description
  3. Strategy: Pick execution order (sequential for deps, parallel for independent, adaptive for mixed)
  4. Checkpoint: Changes affect >3 files → present numbered plan → wait for user approval
  5. Execute: run independent tasks in parallel, each as one `general-purpose` delegate with its domain checks in the prompt, per core/rules/RULES_DELEGATION.md `<sub_agent_decision>`
  6. Validate: Quality gates + completion verification — a task is marked completed in TaskUpdate only when its evidence note cites the check that passed (exit code, test output, observed outcome); a sub-agent's result is a claim to check, not evidence
  7. Cleanup: With --cleanup, delete completed and cancelled tasks and list stale and blocked ones, per the task cleanup section
  </flow>

  <flags>
  - --strategy sequential|parallel|adaptive: force the execution order the Strategy step otherwise picks.
  - --cleanup: task cleanup, per the task cleanup section.
  - --dry-run: with cleanup or --cleanup, list what would be deleted and delete nothing.
  </flags>

  <task_cleanup>
    <description>Task cleanup via TaskUpdate delete</description>
    <cleanable_states>
      - completed: finished tasks; deleted.
      - cancelled: user-cancelled tasks; deleted.
      - stale: pending with no progress since an earlier session; listed, and deleted only after the user confirms.
      - blocked: listed with the unresolved dependency; never deleted automatically.
    </cleanable_states>
    <usage>
      - /sc:task cleanup: Run task cleanup
      - /sc:task cleanup --dry-run: Preview, no deletion
    </usage>
  </task_cleanup>

  <patterns>
    - Hierarchy: Epic → Story → Task → Subtask
    - Strategy: Sequential (strict deps) | Parallel (independent streams) | Adaptive (discover then parallelize)
    - Dependency: Analyze deps before execution — detect circular deps, present resolution options
    - Cleanup: Delete completed/cancelled → list stale and blocked → delete stale only on user confirm → report
  </patterns>

  <examples>

  <example name="circular-dependency" type="error-path">
    - Input: /sc:task 'refactor auth and permissions modules'
    - Why wrong: Circular dep detected: auth → permissions → auth
    - Correct: Present options: A) Extract shared interface to break cycle, B) Merge into single module. User chooses before proceeding.
  </example>

| Input | Output |
|---|---|
| `cleanup` | Delete completed/cancelled tasks; list stale and blocked ones |
| `cleanup --dry-run` | Preview cleanup, no deletion |

  </examples>

  <gotchas>
  - task-count: avoid excessive sub-tasks; break each feature into at most 3-7 tasks
  - already-done: Check git log and existing code before creating implementation tasks
  - workflow-task-state: Under a Workflow-tool fan-out, harness task-state may not survive the subagent boundary — the main loop owns TaskCreate/TaskUpdate and the >3-file approval checkpoint (the Checkpoint step); subagents return task results and cannot pause for input
  </gotchas>

  <bounds>
    <does>complex task coordination, hierarchical breakdown, dependency analysis, task cleanup.</does>
    <never>takes on simple single-file tasks, compromises quality, or operates without validation.</never>
  </bounds>

  <handoff next="/sc:test /sc:implement"/>
</component>