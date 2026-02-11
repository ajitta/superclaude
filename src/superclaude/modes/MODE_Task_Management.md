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
- Start: list_memories() → read_memory("current_plan") → think_about_collected_information()
- During: write_memory + think_about_task_adherence() + TaskCreate/TaskUpdate + checkpoint@30min
- End: think_about_whether_you_are_done() → write_memory("session_summary") → delete_memory(temp)
  </memory_ops>

  <execution>Load: list+read → Plan: hierarchy+memory → Track: TaskCreate/TaskUpdate → Execute → Checkpoint → Complete</execution>

  <tool_select>
| Task | Tool |
|------|------|
| Analysis | Sequential MCP |
| Implementation | Edit/Morphllm |
| UI | Magic MCP |
| Testing | Playwright MCP |
| Docs | Context7 MCP |
  </tool_select>

  <memory_schema>
| Pattern | Purpose |
|---------|---------|
| plan_[ts] | Overall goal |
| phase_[1-5] | Major milestones |
| task_[phase].[num] | Deliverable status |
| checkpoint_[ts] | State snapshot |
| blockers | Active impediments |
  </memory_schema>

  <task_api note="v2.1.19+">
| Tool | Purpose |
|------|---------|
| TaskCreate | Create task: subject, description, activeForm → status: pending |
| TaskUpdate | Update: status (pending→in_progress→completed), dependencies |
| TaskGet | Retrieve full details by ID |
| TaskList | List all: id, subject, status, owner, blockedBy |

Dependencies: addBlocks (this blocks others) | addBlockedBy (blocked by others)
activeForm: Present continuous for spinner (e.g., "Running tests")
  </task_api>

  <bounds will="hierarchical organization|persistent memory|checkpoint tracking" wont="skip memory ops|lose cross-session context|bypass task hierarchy" fallback="Revert to default behavior when inapplicable"/>
</component>
