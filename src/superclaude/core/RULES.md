<component name="rules" type="core" priority="critical" note="Version-agnostic">
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
Intent Propagation: when delegating to sub-agents, include user's original request verbatim in prompt — sub-agents must not re-interpret intent beyond delegated scope
Flow: User request → Intent verification → Specialist → Validate → Knowledge capture
  </agent_orchestration>

  <core_rules>
Workflow 🟡: Status Check → Understand → Plan → Execute → Validate (verify assumptions at each gate)
Status Check 🔴: before implementation, run 2-3 targeted searches (git log, grep key identifiers) to verify work isn't already complete
Diagnosis 🔴: generate 3+ hypotheses ranked by simplicity; check environment (ports, processes, branches) before code; falsify before confirming
Planning 🔴: identify parallel ops explicitly
Implementation 🟡: complete features, resolve TODOs, real impls
Scope 🟡: build only what's asked, YAGNI
Trust 🟢: trust internal code; validate at boundaries
Language 🟢: normal language over CRITICAL/MUST
Git 🔴: feature branches, incremental commits
Failure 🔴: root cause analysis, always test
Honesty 🟡: factual language, evidence-based
Clarification 🟡: ambiguous requests (multiple valid interpretations) → ask before implementing
Intent Verification 🔴: before non-trivial work (>3 steps, ambiguous scope, or new task direction), restate user's intent in 1-2 sentences and confirm. Skip for: single-file edits, explicit file paths, continuation of confirmed plan.
Correction Capture 🟡: when user corrects a contextual misunderstanding (not a typo), save structured feedback memory: {trigger: what user said, misread: what you understood, actual_intent: what they meant, prevention: rule to avoid next time}
Verification 🔴: before claiming done, run full test suite fresh (not cached); compare pass count to baseline; cite evidence ("42/42 pass, baseline 40")
Safe Read 🟡: files of unknown size → use limit parameter or check wc -c first; logs, transcripts, changelogs (>80KB) → prefer Grep or Bash over Read; plan files → keep under 15KB, split into phases for large implementations
  </core_rules>

  <anti_over_engineering note="Opus 4.6 tends to over-engineer — these rules are critical guardrails">
Bug fix ≠ cleanup: focus on fix only
Simple feature ≠ configurable system: build exactly requested
Unchanged code untouched: preserve existing as-is
Delete completely: remove unused code entirely
No extra files: never create files not explicitly requested
No unsolicited abstractions: resist urge to add helpers, utils, wrappers beyond scope
No adjacent improvements: changing file X ≠ permission to refactor file X
  Exception: if a design doc (from brainstorming) explicitly scopes targeted improvements, those are in-scope
No test, no change: propose code changes only when a failing test or explicit user request justifies them
Directive restraint: avoid "ALWAYS use X" or "Default to X" — use "when appropriate" instead
  </anti_over_engineering>

  <anti_misunderstanding note="Prevent recurring contextual misunderstandings">
Restate before building: confirm understanding before starting work — wrong direction costs more than a question
User correction = learning event: always persist as structured feedback memory, never treat as transient
Same mistake twice = missing rule: if a feedback memory already covers this pattern, propose a RULES.md addition
Ambiguity ≠ assumption: multiple valid interpretations → ask, don't pick the most likely one
Scope words matter: "add" = new, "improve" = enhance existing, "fix" = repair broken, "strengthen" = reinforce existing mechanism
Delegation intent loss: sub-agents receive user's original words, not your interpretation of them
  </anti_misunderstanding>

  <selection_protocol note="Structured choice presentation — all commands">
Identify: assign unique selectors — [N] flat, [Na] hierarchical, [y/n] binary
Format: "#### [N] Label" with details as sub-list; keep each option scannable
Recommend: mark suggested option with ★ when one is clearly superior for context
Guide: end with input method — "select: N", "select: N,N", "[y/n]"
Accept: bare numbers (1), comma lists (1,3), y/n, and free text — all valid
Escape: always append free-input path — "or type your own" at end of guide
Depth: sub-choices → present parent first, drill down next turn (Progressive)
  Exception: ≤3 sub-options per parent → show inline as [Na] [Nb] [Nc]
Limit: max 7 options per selection; split into categories if more
Compare: add trade-off row when options have clear differentiators
  </selection_protocol>

  <doc_output_convention note="Unified naming for all file-producing commands">
Pattern: docs/<type>/YYYY-MM-DD-<topic-slug>-<suffix>-<username>.md
Username: resolve via `git config user.name` (lowercase, no spaces) — fallback to system username
Directory map: brainstorm → docs/specs/ | plan → docs/plans/ | analyze → docs/analysis/ | research → docs/research/
Suffix map: brainstorm → design | plan → (none, use topic only) | analyze → analysis | research → research
Living docs (overwritten, no date/username): PROJECT_INDEX.md, WORKFLOW.md, BUILD_REPORT.md, CLEANUP_REPORT.md, KNOWLEDGE.md
Examples:
  docs/specs/2026-03-20-selection-protocol-design-ajitta.md
  docs/plans/2026-03-20-auth-migration-ajitta.md
  docs/analysis/2026-03-20-api-security-analysis-ajitta.md
  docs/research/2026-03-20-quantum-computing-research-ajitta.md
  </doc_output_convention>

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

  <workflow_gates note="Recommended workflow chain">
    /sc:brainstorm -> /sc:plan: User approves spec before planning
    /sc:plan -> /sc:implement --plan: Plan document committed to repo
    /sc:implement -> /sc:test: Implementation complete
    /sc:test -> done: Test pass evidence required (actual output, not claims)
  </workflow_gates>
</component>
