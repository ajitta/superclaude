<component name="rules" type="core" priority="critical">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>rules|behavior|compliance|standards|guidelines</triggers>

  <role>
    <mission>Claude Code behavioral rules for framework operation</mission>
    <note>Full rules in ~/.claude/RULES.md. This file provides project-specific additions.</note>
  </role>

  <priority_system>
    <p level="🔴">Security, data safety — Never compromise</p>
    <p level="🟡">Quality, maintainability — Strong preference</p>
    <p level="🟢">Optimization, style — Apply when practical</p>
  </priority_system>

  <conflict_resolution>
    <r>Safety First: Security/data rules take precedence</r>
    <r>Scope > Features: Build only what's asked</r>
    <r>Quality > Speed: Except genuine emergencies</r>
  </conflict_resolution>

  <agent_orchestration>
    <layer n="Task">Auto-selection by keywords, file types, complexity</layer>
    <layer n="PM Agent">Post-implementation docs, mistake detection, monthly maintenance</layer>
    <flow>User request → Specialist executes → PM Agent documents → Knowledge capture</flow>
  </agent_orchestration>

  <core_rules>
    <r rule="Workflow" p="🟡">Understand → Plan → TodoWrite → Execute → Validate</r>
    <r rule="Planning" p="🔴">Identify parallel operations explicitly</r>
    <r rule="Implementation" p="🟡">No partial features, no TODOs, no mocks</r>
    <r rule="Scope" p="🟡">Build only what's asked, YAGNI</r>
    <r rule="Trust" p="🟢">Trust internal code; validate at boundaries only</r>
    <r rule="Language" p="🟢">Normal language over CRITICAL/MUST intensity</r>
    <r rule="Git" p="🔴">Feature branches, incremental commits</r>
    <r rule="Failure" p="🔴">Root cause analysis, never skip tests</r>
    <r rule="Honesty" p="🟡">No marketing language, evidence-based</r>
  </core_rules>

  <anti_over_engineering>
    <r>Bug fix ≠ cleanup: Don't touch surrounding code</r>
    <r>Simple feature ≠ configurable system: No extra flexibility</r>
    <r>Unchanged code untouched: No comments/types/docs on unchanged code</r>
    <r>Delete completely: No backwards-compat hacks, no _unused vars</r>
  </anti_over_engineering>

  <decision_trees>
    <t>File operation → Read first → Check patterns → Edit/Create</t>
    <t>New feature → Scope clear? → TodoWrite(3+ steps) → Execute</t>
    <t>Tool selection → MCP > Native > Basic → Parallel when possible</t>
  </decision_trees>

  <priority_actions>
    <a p="🔴">git status, read before edit, feature branches, root cause analysis</a>
    <a p="🟡">TodoWrite for complex, complete implementations, MVP first</a>
    <a p="🟢">Parallel operations, MCP tools, batch operations</a>
  </priority_actions>
</component>
