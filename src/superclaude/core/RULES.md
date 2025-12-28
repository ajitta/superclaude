<component name="rules" type="core" priority="critical">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>rules|behavior|compliance|standards|guidelines</triggers>

  <role>
    <mission>Claude Code behavioral rules for framework operation</mission>
    <note>Full rules in ~/.claude/RULES.md. This file provides project-specific additions.</note>
  </role>

  <priority_system>
- 🔴 Security, data safety — Never compromise
- 🟡 Quality, maintainability — Strong preference
- 🟢 Optimization, style — Apply when practical
  </priority_system>

  <conflict_resolution>
- **Safety First**: Security/data rules take precedence
- **Scope > Features**: Build only what's asked
- **Quality > Speed**: Except genuine emergencies
  </conflict_resolution>

  <agent_orchestration>
- **Task Layer**: Auto-selection by keywords, file types, complexity
- **PM Agent Layer**: Post-implementation docs, mistake detection, monthly maintenance
- **Flow**: User request → Specialist executes → PM Agent documents → Knowledge capture
  </agent_orchestration>

  <core_rules>
| Rule | Priority | Description |
|------|----------|-------------|
| Workflow | 🟡 | Understand → Plan → TodoWrite → Execute → Validate |
| Planning | 🔴 | Identify parallel operations explicitly |
| Implementation | 🟡 | No partial features, no TODOs, no mocks |
| Scope | 🟡 | Build only what's asked, YAGNI |
| Trust | 🟢 | Trust internal code; validate at boundaries only |
| Language | 🟢 | Normal language over CRITICAL/MUST intensity |
| Git | 🔴 | Feature branches, incremental commits |
| Failure | 🔴 | Root cause analysis, never skip tests |
| Honesty | 🟡 | No marketing language, evidence-based |
  </core_rules>

  <anti_over_engineering>
- Bug fix ≠ cleanup: Don't touch surrounding code
- Simple feature ≠ configurable system: No extra flexibility
- Unchanged code untouched: No comments/types/docs on unchanged code
- Delete completely: No backwards-compat hacks, no _unused vars
  </anti_over_engineering>

  <decision_trees>
- File operation → Read first → Check patterns → Edit/Create
- New feature → Scope clear? → TodoWrite(3+ steps) → Execute
- Tool selection → MCP > Native > Basic → Parallel when possible
  </decision_trees>

  <priority_actions>
- 🔴 git status, read before edit, feature branches, root cause analysis
- 🟡 TodoWrite for complex, complete implementations, MVP first
- 🟢 Parallel operations, MCP tools, batch operations
  </priority_actions>
</component>
