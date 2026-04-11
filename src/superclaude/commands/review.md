---
description: Review code changes for quality, security, and correctness with structured feedback
---

<component name="review" type="command">

  <role>
    /sc:review
    <mission>Review code changes for quality, security, and correctness with structured feedback</mission>
  </role>

  <syntax>/sc:review [target] [--scope pr|diff|file|branch] [--structured]</syntax>

  <flow>
    1. Scope: Determine review range — PR number, git diff, specific files, or branch comparison
    2. Gather: Read all changed files; locate spec/plan if exists (docs/specs/ or docs/plans/)
    3. Review-2D: Dimension 1 (spec fidelity) — does code match what was planned? Dimension 2 (code quality) — correctness, security, edge cases, test coverage. When no spec exists, weight shifts to Dimension 2
    4. Challenge: Before categorizing, answer these explicitly — What conditions could make this approach fail? What edge cases are easiest to miss here? What will be hardest to modify 6 months from now?
    5. Categorize: Group findings as Critical (must fix) | Important (should fix) | Suggestion (nice to have)
    6. Verify: Run tests and linting on changed code to confirm findings
    7. Process: For each finding — classify (change request vs concern vs question) → verify against codebase → implement fix or push back with evidence
  </flow>

  <outputs>
  | Artifact | Purpose |
  |----------|---------|
  | Review summary | Categorized findings (critical/important/suggestion) |
  | Action items | Required changes before merge |
  | Test results | Verification evidence |
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
  |-------|--------|
  | `/sc:review --scope diff` | Review unstaged changes |
  | `/sc:review --scope pr 42` | Review PR #42 |
  | `/sc:review src/auth/` | Review all files in auth directory |
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

  <bounds should="code review|quality analysis|security scanning|2D spec+quality review" avoid="auto-merge|auto-approve|modify code without explicit permission" fallback="Without spec: weight review toward code quality dimension"/>

  <handoff next="/sc:implement /sc:test /sc:troubleshoot"/>
</component>
