<component name="rules" type="core" priority="critical">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>rules|behavior|compliance|standards|guidelines</triggers>

  <role>
    <mission>Claude Code behavioral rules for framework operation</mission>
    <note>Full rules in ~/.claude/RULES.md. This file provides project-specific additions.</note>
  </role>

  <priority_system>
- 🔴 Security, data safety — Always protect
- 🟡 Quality, maintainability — Strong preference
- 🟢 Optimization, style — Apply when practical
  </priority_system>

  <conflict_resolution>
- Safety First: Security/data rules take precedence
- Scope > Features: Build only what's asked
- Quality > Speed: Except genuine emergencies
  </conflict_resolution>

  <agent_orchestration>
- Task Layer: Auto-selection by keywords, file types, complexity
- PM Agent Layer: Post-impl docs, mistake detection, monthly maintenance
- Flow: User request → Specialist → PM Agent documents → Knowledge capture
  </agent_orchestration>

  <core_rules>
| Rule | Pri | Description |
|------|-----|-------------|
| Workflow | 🟡 | Understand → Plan → TaskCreate → Execute → Validate |
| Planning | 🔴 | Identify parallel ops explicitly |
| Implementation | 🟡 | Complete features, resolve TODOs, real impls |
| Scope | 🟡 | Build only what's asked, YAGNI |
| Trust | 🟢 | Trust internal code; validate at boundaries |
| Language | 🟢 | Normal language over CRITICAL/MUST |
| Git | 🔴 | Feature branches, incremental commits |
| Failure | 🔴 | Root cause analysis, always test |
| Honesty | 🟡 | Factual language, evidence-based |
  </core_rules>

  <anti_over_engineering>
- Bug fix ≠ cleanup: Focus on fix only
- Simple feature ≠ configurable system: Build exactly requested
- Unchanged code untouched: Preserve existing as-is
- Delete completely: Remove unused code entirely
  </anti_over_engineering>

  <decision_trees>
- File op → Read first → Check patterns → Edit/Create
- New feature → Scope clear? → TaskCreate(3+ steps) → Execute
- Tool selection → MCP > Native > Basic → Parallel when possible
  </decision_trees>

  <priority_actions>
- 🔴 git status, read before edit, feature branches, root cause
- 🟡 TaskCreate for complex, complete impls, MVP first
- 🟢 Parallel ops, MCP tools, batch operations
  </priority_actions>

  <dynamic_context>
- Hook injects `<context-load file="path"/>` on UserPromptSubmit
- Dedup via temp file cache; skip if content visible
- Benefit: ~70% token savings vs static @-references
  </dynamic_context>
</component>
