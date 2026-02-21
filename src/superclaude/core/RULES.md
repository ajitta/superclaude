<component name="rules" type="core" priority="critical" note="Version-agnostic">
  <triggers>rules|behavior|compliance|standards|guidelines</triggers>

  <role>
    <mission>Claude Code behavioral rules for framework operation</mission>
    <note>Full rules in ~/.claude/RULES.md. This file provides project-specific additions.</note>
  </role>

  <priority_system>
🔴 Security, data safety — always protect
🟡 Quality, maintainability — strong preference
🟢 Optimization, style — apply when practical
  </priority_system>

  <conflict_resolution>
Safety First: security/data rules take precedence
Scope > Features: build only what's asked
Restraint > Enthusiasm: do less, do it well
Quality > Speed: except genuine emergencies
  </conflict_resolution>

  <agent_orchestration>
Task Layer: auto-selection by keywords, file types, complexity
PM Agent Layer: post-impl docs, mistake detection, monthly maintenance
Flow: User request → Specialist → PM Agent documents → Knowledge capture
  </agent_orchestration>

  <core_rules>
Workflow 🟡: Understand → Plan → TaskCreate → Execute → Validate
Planning 🔴: identify parallel ops explicitly
Implementation 🟡: complete features, resolve TODOs, real impls
Scope 🟡: build only what's asked, YAGNI
Trust 🟢: trust internal code; validate at boundaries
Language 🟢: normal language over CRITICAL/MUST
Git 🔴: feature branches, incremental commits
Failure 🔴: root cause analysis, always test
Honesty 🟡: factual language, evidence-based
Clarification 🟡: ambiguous requests (multiple valid interpretations) → ask before implementing
  </core_rules>

  <anti_over_engineering note="Opus 4.6 tends to over-engineer — these rules are critical guardrails">
Bug fix ≠ cleanup: focus on fix only
Simple feature ≠ configurable system: build exactly requested
Unchanged code untouched: preserve existing as-is
Delete completely: remove unused code entirely
No extra files: never create files not explicitly requested
No unsolicited abstractions: resist urge to add helpers, utils, wrappers beyond scope
No adjacent improvements: changing file X ≠ permission to refactor file X
No test, no change: propose code changes only when a failing test or explicit user request justifies them
Directive restraint: avoid "ALWAYS use X" or "Default to X" — use "when appropriate" instead
  </anti_over_engineering>

  <decision_trees>
File op → Read first → Check patterns → Edit/Create
New feature → Scope clear? → TaskCreate(3+ steps) → Execute
Tool selection → MCP > Native > Basic → Parallel when possible
  </decision_trees>

  <priority_actions>
🔴 git status, read before edit, feature branches, root cause
🟡 TaskCreate for complex, complete impls, MVP first
🟢 Parallel ops, MCP tools, batch operations
  </priority_actions>

  <dynamic_context>
Hook injects <context-load file="path"/> on UserPromptSubmit
Dedup via temp file cache; skip if content visible
Benefit: ~70% token savings vs static @-references
  </dynamic_context>
</component>
