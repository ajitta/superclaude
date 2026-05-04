---
description: Review work products (code, plans, designs, specs) for quality, correctness, and alignment with structured feedback
---

<component name="review" type="command">

  <role>
    /sc:review
    <mission>Review work products — code, plans, designs, specs — for quality, correctness, and alignment with structured feedback</mission>
  </role>

  <syntax>/sc:review [target] [--scope pr|diff|file|branch|plan|design|spec] [--structured] [--audit-delegated]</syntax>

  <flow>
  1. Scope: Determine review range — PR/diff/file/branch for code, or plan/design/spec doc path
  2. Gather: Read target artifact + related context (spec/plan if reviewing code; parent spec if reviewing plan; requirements if reviewing design). Locate in docs/specs/ or docs/plans/ if present
  3. Review-2D: Dimension 1 (spec fidelity) — does artifact match what was intended? Dimension 2 (artifact quality) — correctness for code, planning rigor for plans, architectural soundness for designs, requirement coverage for specs. When no spec exists, weight shifts to Dimension 2
  4. Challenge: Before categorizing, answer explicitly — What conditions could make this approach fail? What gaps are easiest to miss here? What will be hardest to change 6 months from now?
  5. Categorize: Group findings as Critical (must fix) | Important (should fix) | Suggestion (nice to have)
  6. Verify: Evidence appropriate to artifact type — tests+lint for code, executability+completeness for plans, trade-off rationale for designs, acceptance criteria for specs
  7. Process: For each finding — classify (change request vs concern vs question) → verify against source of truth → propose fix or push back with evidence
  8. Delegated-decision audit (--audit-delegated): when invoked on a spec with a "Resolved Decisions" table, scope review to ONLY the rows whose `mode` is `delegated` (per /sc:brainstorm step 5c heuristic). Surface for each: original Q, model recommendation, and an independent re-evaluation of the choice. Other rows are skipped. Source: 2026-04-25 §5.3 — delegated decisions historically need explicit audit; user-confirmed choices already passed direct user judgment.
  </flow>

  <outputs>
  | Artifact | Purpose |
  |---|---|
  | Review summary | Categorized findings (critical/important/suggestion) |
  | Action items | Required changes before merge/approval |
  | Verification | Evidence appropriate to artifact type (test output, plan executability, design rationale) |
  </outputs>


  <tools>
  - Grep: Search for patterns across changed files
  - Read: Examine file contents and context
  - Bash: Run tests and linting commands
  - Agent: Dispatch isolated reviewer subagent for large reviews (--structured)
  </tools>

  <focus_agent_mapping>
  When --p flag or domain context suggests specialist review, delegate to:
  security → @security-engineer | performance → @performance-engineer | quality → @quality-engineer | architecture → @system-architect
  </focus_agent_mapping>

  <examples>
  | Input | Output |
  |---|---|
  | `/sc:review --scope diff` | Review unstaged code changes |
  | `/sc:review --scope pr 42` | Review PR #42 |
  | `/sc:review src/auth/` | Review all files in auth directory |
  | `/sc:review --scope plan docs/plans/foo.md` | Review plan doc: traceability + gaps + dependencies |
  | `/sc:review --scope design docs/specs/bar.md` | Review design: goal fit + trade-offs + architectural gaps |
  | `/sc:review --scope branch --structured` | 2D review with subagent dispatch |

  <example name="pushback-protocol" type="info">
    When a review finding is incorrect, push back with evidence:
    - "This breaks test_X because [reason]. See [file:line]"
    - "Module B uses [different pattern]. Not applicable here."
    - "No current consumer for this abstraction. Deferring per YAGNI."
  </example>
  </examples>


  <gotchas>
  - scope-focus: Review only the changed code, not the entire file or module
  - no-unsolicited-fixes: Flag issues but do not fix them unless asked
  </gotchas>

  <bounds>
    <does>work-product review (code/plan/design/spec), quality analysis, security scanning, and 2D spec+quality review.</does>
    <never>auto-merge, auto-approve, and modify artifact without explicit permission.</never>
    <fallback>Without spec: weight review toward artifact quality dimension.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:test /sc:troubleshoot"/>
</component>
