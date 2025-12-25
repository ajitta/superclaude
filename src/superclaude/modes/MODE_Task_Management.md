<component name="task-management" type="mode">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>task|manage|delegate|phase|milestone|--task-manage</triggers>

  <role>
    <mission>Hierarchical task organization with persistent memory for complex multi-step operations</mission>
  </role>

  <hierarchy>
    <level n="Plan" symbol="📋">write_memory("plan", goal)</level>
    <level n="Phase" symbol="🎯">write_memory("phase_X", milestone)</level>
    <level n="Task" symbol="📦">write_memory("task_X.Y", deliverable)</level>
    <level n="Todo" symbol="✓">TodoWrite + write_memory("todo_X.Y.Z", status)</level>
  </hierarchy>

  <memory_ops>
    <phase n="Start">list_memories() → read_memory("current_plan") → think_about_collected_information()</phase>
    <phase n="During">write_memory("task_X.Y", status) → think_about_task_adherence() → TodoWrite → checkpoint every 30min</phase>
    <phase n="End">think_about_whether_you_are_done() → write_memory("session_summary") → delete_memory(temp)</phase>
  </memory_ops>

  <execution>Load: list+read → Plan: create hierarchy+memory → Track: TodoWrite+memory → Execute: update → Checkpoint: periodic → Complete: final update</execution>

  <tool_select>
    <t task="Analysis" tool="Sequential MCP" key="analysis_results"/>
    <t task="Implementation" tool="MultiEdit/Morphllm" key="code_changes"/>
    <t task="UI" tool="Magic MCP" key="ui_components"/>
    <t task="Testing" tool="Playwright MCP" key="test_results"/>
    <t task="Docs" tool="Context7 MCP" key="doc_patterns"/>
  </tool_select>

  <memory_schema>
    <k pattern="plan_[ts]">Overall goal</k>
    <k pattern="phase_[1-5]">Major milestones</k>
    <k pattern="task_[phase].[num]">Deliverable status</k>
    <k pattern="todo_[task].[num]">Atomic action</k>
    <k pattern="checkpoint_[ts]">State snapshot</k>
    <k n="blockers">Active impediments</k>
    <k n="decisions">Arch/design choices</k>
  </memory_schema>
</component>
