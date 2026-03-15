---
name: requesting-code-review
description: |
  Dispatch a subagent reviewer with the context needed to review completed work.
  Use when completing tasks, implementing features, or before merging.
context: fork
---

<component name="requesting-code-review" type="skill">

  <role>
    <mission>Dispatch a structured code review covering spec fidelity and code quality</mission>
  </role>

  <when>
  - After completing a discrete task or feature
  - Before merging any branch into integration or master
  - After resolving a complex bug touching multiple files
  - When stuck on a design decision or working in unfamiliar code
  </when>

  <flow>
    1. Diff range: Identify BASE_SHA..HEAD_SHA covering your work — confirm with git log --oneline
    2. Gather context: Changed files, purpose, original requirements/plan, current test results
    3. Locate plan: If a plan document exists (from writing-plans), include it as review reference
    4. Dispatch reviewer: Send self-review subagent or /sc:review with implementation summary, plan/requirements, commit range, review dimensions
    5. Keep context clean: Reviewer receives final result and requirements — not false starts
    6. Triage feedback by severity: Critical (fix now) | Important (fix before next task) | Minor (batch later) | Style (apply if agreed)
    7. Re-request if needed: After addressing Critical/Important items with substantial changes
  </flow>

  <review_dimensions note="Two-dimensional review in single pass — spec fidelity + code quality">
  The reviewer evaluates BOTH dimensions in a single review pass:

  **Dimension 1 — Spec Fidelity** (does implementation match intent?):
  - Does the code implement what was planned/requested?
  - Are all requirements from the plan addressed?
  - Are there unplanned additions (scope creep)?
  - Do edge cases from the spec have handling?

  **Dimension 2 — Code Quality** (is the code well-crafted?):
  - Correctness, error handling, edge cases
  - Security (input validation, injection risks)
  - Performance (unnecessary allocations, N+1 queries)
  - Maintainability (naming, structure, complexity)
  - Test coverage (are new paths tested?)

  When no plan document exists, weight shifts to Dimension 2 (quality-only review).
  </review_dimensions>

  <constraints>
  - Do not skip review because "it's a small change" — small changes in critical paths cause outages
  - Do not request review before work compiles and tests pass
  - Do not ignore Critical feedback — disagree with evidence, not silence
  </constraints>

  <bounds will="structured two-dimensional review dispatch" wont="skip review or accept without triage"/>

  <handoff next="/sc:review receiving-code-review"/>
</component>
