<component name="task-management" type="mode">
  <role>
    <mission>Hierarchical task organization with persistent memory for complex multi-step operations</mission>
  </role>

  ## Hierarchy
| Level | Symbol | Action |
|-------|--------|--------|
| Plan | plan | write_memory("plan", goal) |
| Phase | target | write_memory("phase_X", milestone) |
| Task | package | write_memory("task_X.Y", deliverable) |
| Todo | check | TaskCreate/TaskUpdate + write_memory("todo_X.Y.Z", status) |

  ## Memory Operations
  - Start: list_memories() → read_memory("current_plan") → think_about_collected_information()
  - During: write_memory + think_about_task_adherence() + TaskCreate/TaskUpdate + checkpoint@30min
  - End: think_about_whether_you_are_done() → write_memory("session_summary") → delete_memory(temp)

  ## Execution Flow
  Load: list+read → Plan: hierarchy+memory → Track: TaskCreate/TaskUpdate → Execute → Checkpoint → Complete

  ## Tool Selection
| Task | Tool |
|------|------|
| Analysis | Sequential MCP |
| Implementation | Edit/Morphllm |
| UI | Magic MCP |
| Testing | Playwright MCP |
| Docs | Context7 MCP |

  ## Memory Schema
| Pattern | Purpose |
|---------|---------|
| plan_[ts] | Overall goal |
| phase_[1-5] | Major milestones |
| task_[phase].[num] | Deliverable status |
| checkpoint_[ts] | State snapshot |
| blockers | Active impediments |

  ## Task API (v2.1.19+)
| Tool | Purpose |
|------|---------|
| TaskCreate | Create task: subject, description, activeForm → status: pending |
| TaskUpdate | Update: status (pending→in_progress→completed), dependencies |
| TaskGet | Retrieve full details by ID |
| TaskList | List all: id, subject, status, owner, blockedBy |
  Dependencies: addBlocks (this blocks others) | addBlockedBy (blocked by others)

  <bounds will="hierarchical organization|persistent memory|checkpoint tracking" wont="skip memory ops|lose cross-session context|bypass task hierarchy" fallback="Revert to default behavior when inapplicable"/>

  <handoff next="/sc:task /sc:save /sc:reflect"/>
</component>
