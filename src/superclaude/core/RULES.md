<component name="rules" type="core" priority="critical">
  <config style="Telegraphic|Imperative|XML"/>

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
- PM Agent Layer: Post-implementation docs, mistake detection, monthly maintenance
- Flow: User request → Specialist executes → PM Agent documents → Knowledge capture
  </agent_orchestration>

  <core_rules>
| Rule | Priority | Description |
|------|----------|-------------|
| Workflow | 🟡 | Understand → Plan → TodoWrite → Execute → Validate |
| Planning | 🔴 | Identify parallel operations explicitly |
| Implementation | 🟡 | Complete features, resolve TODOs, use real implementations |
| Scope | 🟡 | Build only what's asked, YAGNI |
| Trust | 🟢 | Trust internal code; validate at boundaries only |
| Language | 🟢 | Normal language over CRITICAL/MUST intensity |
| Git | 🔴 | Feature branches, incremental commits |
| Failure | 🔴 | Root cause analysis, always run tests |
| Honesty | 🟡 | Use factual language, evidence-based claims |
  </core_rules>

  <anti_over_engineering>
- Bug fix ≠ cleanup: Focus on the fix only
- Simple feature ≠ configurable system: Build exactly what's requested
- Unchanged code untouched: Preserve existing code as-is
- Delete completely: Remove unused code entirely
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

  <dynamic_context note="Hook-triggered loading">
- Directive: `<context-load file="path"/>` injected by UserPromptSubmit hook
- Action: Use Read tool to load file content
- Dedup: Hook tracks loaded files per session (temp file cache)
- Skip: If content already visible in conversation, skip Read
- Benefit: ~70% token savings vs static @-references
  </dynamic_context>
</component>
