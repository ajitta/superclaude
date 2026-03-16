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
    4. Categorize: Group findings as Critical (must fix) | Important (should fix) | Suggestion (nice to have)
    5. Verify: Run tests and linting on changed code to confirm findings
    6. Process: For each finding — classify (change request vs concern vs question) → verify against codebase → implement fix or push back with evidence
  </flow>

  <outputs note="Per execution">
  | Artifact | Purpose |
  |----------|---------|
  | Review summary | Categorized findings (critical/important/suggestion) |
  | Action items | Required changes before merge |
  | Test results | Verification evidence |
  </outputs>

  <mcp servers="seq|serena"/>
  <personas p="qa|sec"/>

  <tools>
    - Grep: Search for patterns across changed files
    - Read: Examine file contents and context
    - Bash: Run tests and linting commands
    - Agent: Dispatch isolated reviewer subagent for large reviews (--structured)
  </tools>

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

  <token_note>Medium-high consumption — --structured dispatches subagent for isolated context</token_note>

  <bounds will="code review|quality analysis|security scanning|2D spec+quality review" wont="auto-merge|auto-approve|modify code without explicit permission" fallback="Ask user for guidance when uncertain"/>

  <handoff next="/sc:implement /sc:test /sc:troubleshoot"/>
</component>
