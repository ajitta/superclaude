---
description: Reflect on and validate a multi-step task — surface assumptions, list residuals, name gaps. Use when asked whether a task is truly done. Not for the routine end-of-turn summary.
---
<component name="reflect" type="command">

  <role command="/sc:reflect">
    <mission>Reflect on and validate a task using analysis capabilities</mission>
    <note>/sc:reflect judges done-ness from evidence already gathered; to produce new test evidence, run /sc:test.</note>
  </role>

  <syntax>/sc:reflect [--type task|session|completion] [--analyze] [--validate]</syntax>

  <flow>
  1. Analyze: judge completeness of info gathered
  2. Validate: check goal align + drift; when the feature folder holds `00-intent.md`, compare its Proposed outcome, and its `Done when:` line when present, with what was delivered and record the gap
    2.5. Misunderstanding-Audit: spot moments user intent misread this session. Each: what trigger misread, what actual intent, what rule stop it. List the ones not yet stored as proposed feedback memories for the Persist step.
  3. Reflect: weigh done-criteria
    3.5. Gotchas-Gardening: if `.claude/rules/gotchas/` exist, check: (a) files with `# Last reviewed:` older 90 days → warn, (b) `paths:` glob match zero files in project → warn stale pattern, (c) gotcha entries cite identifiers not in codebase → warn maybe stale.
    3.6. Plan-Close: when the work ran from a plan document (a feature folder's `05-plan.md` or a `docs/plans/` plan), check its plan (index) from the plan file, the review findings and `git log`, without re-running the Proof: (1) every task box is checked; (2) the `## Proof` footer's `Result:` line is green or marked accepted by the user, and no commit after its sha changes code; (3) every Critical or Important review finding is fixed or accepted by the user, and no fix to one waits for another /sc:review round. The plan is `implementing` and all three hold → propose one docs-only commit that sets the plan `status: complete` and, in a feature folder, the README `phase: complete`, and write it only when the user says yes. A condition fails → name it and the step that clears it: an open box, a missing `Result:` line or a code commit after its sha to /sc:implement --plan, which finishes the box or re-runs the Proof and rewrites `Result:`; a fix waiting for review to /sc:review; an open finding or a red `Result:` to the user, who accepts it or has it fixed. A `complete` plan whose `Result:` is red or whose condition (3) fails is proposed back to `implementing`, the README `phase:` unchanged; a code commit after its sha only needs the Proof re-run
  4. Persist: propose learnings and feedback memories for /sc:save; write them only when the user agrees
  </flow>

  <flags>
  - --type task|session|completion: task: the current task's goal alignment; session: all work this session; completion: done-ready judgment.
  - --analyze: goal alignment: compare the work done against the task's stated goal, item by item.
  - --validate: quality check of the delivered work: verification actually run, claims backed by evidence, gaps named; unrelated to the global --validate.
  </flags>


  <examples>
  | Input | Output |
  |---|---|
  | `--type task --analyze` | Goal align validate |
  | `--type session --validate` | Session work quality check |
  | `--type completion` | Done-ready judge |
  </examples>


  <gotchas>
  - evidence-required: cite real test output + file state, not predict result
  - baseline-compare: compare now-state vs baseline metric (test count, pass rate)
  </gotchas>

  <bounds>
    <does>full reflection, cross-session learning, qualitative rule-effectiveness analysis (misread audit and improvement narrative).</does>
    <never>sets a plan `complete` without the user's yes or with a Plan-Close condition unmet, bypasses integrity checks, or produces quantitative rule statistics (delegate those to /sc:analyze --focus rules).</never>
  </bounds>

  <handoff next="/sc:improve /sc:troubleshoot"/>
</component>