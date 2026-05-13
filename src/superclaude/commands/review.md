---
description: Review work product (code, plan, design, spec) for quality, correctness, alignment with structured feedback. Use when user type `/sc:review`, ask "second opinion" / "independent review" of deliverable, or want structured feedback on PR/spec/plan. NOT auto-trigger on casual "does this look right?" or "is this OK?" — those get brief inline answer.
---

<component name="review" type="command">

  <role command="/sc:review">
    <mission>Review work product — code, plan, design, spec — for quality, correctness, alignment. Structured feedback.</mission>
  </role>

  <syntax>/sc:review [target] [--scope pr|diff|file|branch|plan|design|spec] [--structured] [--audit-delegated]</syntax>

  <flow>
  1. Scope: pick review range — PR/diff/file/branch for code, or plan/design/spec doc path
  2. Gather: read target artifact + related context (spec/plan if reviewing code; parent spec if reviewing plan; requirements if reviewing design). Find in docs/specs/ or docs/plans/ if present
  3. Review-2D: Dim 1 (spec fidelity) — artifact match intent? Dim 2 (artifact quality) — correctness for code, planning rigor for plan, architectural soundness for design, requirement coverage for spec. No spec → weight shift to Dim 2
  4. Challenge: before categorize, answer plain — What condition make approach fail? What gap easy to miss? What hardest to change 6 months from now?
  5. Categorize: group finding as Critical (must fix) | Important (should fix) | Suggestion (nice to have)
  6. Verify: evidence fit artifact type — tests+lint for code, executability+completeness for plan, trade-off rationale for design, acceptance criteria for spec
  7. Process: each finding — classify (change request vs concern vs question) → verify against source of truth → propose fix or push back with evidence
  8. Delegated-decision audit (--audit-delegated): when called on spec with "Resolved Decisions" table, scope review to ONLY row where `mode` is `delegated` (per /sc:brainstorm step 7 heuristic). Surface for each: original Q, model recommendation, independent re-eval of choice. Other row skipped. Delegated decision historically need explicit audit; user-confirmed choice already pass direct user judgment.
  </flow>

  <outputs>
  | Artifact | Purpose |
  |---|---|
  | Review summary | Categorized finding (critical/important/suggestion) |
  | Action items | Required change before merge/approval |
  | Verification | Evidence fit artifact type (test output, plan executability, design rationale) |
  </outputs>


  <tools>
  - Grep: search pattern across changed file
  - Read: examine file content + context
  - Bash: run test + lint command
  - Agent: dispatch isolated reviewer subagent for big review (--structured)
  </tools>

  <focus_agent_mapping>
  When --p flag or domain context suggest specialist review, delegate to:
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
    When review finding wrong, push back with evidence:
    - "This breaks test_X because [reason]. See [file:line]"
    - "Module B uses [different pattern]. Not applicable here."
    - "No current consumer for this abstraction. Deferring per YAGNI."
  </example>
  </examples>


  <gotchas>
  - scope-focus: review only changed code, not whole file or module
  - no-unsolicited-fixes: flag issue but no fix unless asked
  </gotchas>

  <bounds>
    <does>work-product review (code/plan/design/spec), quality analysis, security scan, 2D spec+quality review.</does>
    <never>auto-merge, auto-approve, modify artifact without explicit permission.</never>
    <fallback>No spec: weight review toward artifact quality dim.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:test /sc:troubleshoot"/>
</component>