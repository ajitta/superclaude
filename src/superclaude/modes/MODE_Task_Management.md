<component name="task-management" type="mode">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>task|manage|delegate|phase|milestone|--task-manage</triggers>

  <role>
    <mission>Hierarchical task organization with persistent memory for complex multi-step operations</mission>
  </role>

  <hierarchy>
| Level | Symbol | Action |
|-------|--------|--------|
| Plan | plan | write_memory("plan", goal) |
| Phase | target | write_memory("phase_X", milestone) |
| Task | package | write_memory("task_X.Y", deliverable) |
| Todo | check | TaskCreate/TaskUpdate + write_memory("todo_X.Y.Z", status) |
  </hierarchy>

  <memory_ops>
- Start: list_memories() -> read_memory("current_plan") -> think_about_collected_information()
- During: write_memory("task_X.Y", status) -> think_about_task_adherence() -> TaskCreate/TaskUpdate -> checkpoint every 30min
- End: think_about_whether_you_are_done() -> write_memory("session_summary") -> delete_memory(temp)
  </memory_ops>

  <execution>Load: list+read -> Plan: create hierarchy+memory -> Track: TaskCreate/TaskUpdate+memory -> Execute: update -> Checkpoint: periodic -> Complete: final update</execution>

  <tool_select>
| Task | Tool | Key |
|------|------|-----|
| Analysis | Sequential MCP | analysis_results |
| Implementation | MultiEdit/Morphllm | code_changes |
| UI | Magic MCP | ui_components |
| Testing | Playwright MCP | test_results |
| Docs | Context7 MCP | doc_patterns |
  </tool_select>

  <memory_schema>
| Pattern | Purpose |
|---------|---------|
| plan_[ts] | Overall goal |
| phase_[1-5] | Major milestones |
| task_[phase].[num] | Deliverable status |
| todo_[task].[num] | Atomic action |
| checkpoint_[ts] | State snapshot |
| blockers | Active impediments |
| decisions | Arch/design choices |
  </memory_schema>

  <task_api note="v2.1.16+ replaces TodoWrite/TodoRead">
| Tool | Purpose | Key Fields |
|------|---------|------------|
| `TaskCreate` | Create task with subject, description, activeForm | status: pending (default) |
| `TaskUpdate` | Update status, add dependencies, change owner | status: pending → in_progress → completed |
| `TaskGet` | Retrieve full task details by ID | includes blocks/blockedBy |
| `TaskList` | List all tasks with summary | id, subject, status, owner, blockedBy |

Status flow: `pending` → `in_progress` → `completed`

Dependency fields:
- `addBlocks`: Tasks that cannot start until this one completes
- `addBlockedBy`: Tasks that must complete before this one can start
- `activeForm`: Present continuous shown in spinner (e.g., "Running tests")

Migration from TodoWrite:
- `TodoWrite([{task, status}])` → `TaskCreate({subject, description})` + `TaskUpdate({taskId, status})`
- `TodoRead` → `TaskList` + `TaskGet(taskId)`
  </task_api>
</component>
