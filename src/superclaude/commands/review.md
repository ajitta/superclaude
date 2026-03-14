---
description: Review code changes for quality, security, and correctness with structured feedback
---

<component name="review" type="command">

  <role>
    /sc:review
    <mission>Review code changes for quality, security, and correctness with structured feedback</mission>
  </role>

  <syntax>/sc:review [target] [--scope pr|diff|file|branch]</syntax>

  <flow>
    1. Identify: Determine review scope — PR number, git diff, specific files, or branch comparison
    2. Gather: Read all changed files, understand context and intent of changes
    3. Analyze: Check for correctness, security issues, edge cases, test coverage, style consistency
    4. Categorize: Group findings as Critical (must fix), Important (should fix), Suggestion (nice to have)
    5. Report: Present structured review with evidence and specific line references
    6. Verify: Run tests and linting on changed code to confirm findings
  </flow>

  <outputs note="Per execution">
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
    - Agent: Dispatch specialized reviewers for security or performance
  </tools>

  <examples>
  | Input | Output |
  |-------|--------|
  | `/sc:review --scope diff` | Review unstaged changes |
  | `/sc:review --scope pr 42` | Review PR #42 |
  | `/sc:review src/auth/` | Review all files in auth directory |
  </examples>

  <bounds will="code review, quality analysis, security scanning, test verification" wont="auto-merge, auto-approve, modify code without explicit permission"/>

  <handoff next="/sc:implement /sc:test"/>
</component>
