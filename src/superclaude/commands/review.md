---
description: Review a work product (code, plan, design, spec) for quality, correctness and alignment, with structured feedback. Use when asked for a second opinion or an independent review. Not for a codebase-wide audit across domains — /sc:analyze; a casual "does this look right?" — answer briefly.
---

<component name="review" type="command">

  <role command="/sc:review">
    <mission>Review a work product (code, plan, design, spec) for quality, correctness and alignment, with structured feedback.</mission>
  </role>

  <syntax>/sc:review [target] [--scope pr|diff|file|branch|plan|design|spec] [--structured] [--audit-delegated]</syntax>

  <flow>
  1. Scope: pick review range — PR/diff/file/branch for code, or plan/design/spec doc path
  2. Gather: read target artifact + related context (spec/plan if reviewing code; parent spec if reviewing plan; requirements if reviewing design; `00-intent.md` from the feature folder when present). Find in docs/specs/ or docs/plans/ if present. A `status: draft` spec goes to the isolated reviewer (the Agent entry in the tools section) with the feature folder's `00-intent.md` verbatim among its acceptance criteria, so the reviewer checks the spec against the requester's own words and not only against the spec's own reading of them; a spec with no feature folder goes without it
  3. Review: Dim 1 (spec fidelity) — does the artifact match the intent (the spec, and the feature's `00-intent.md` when present)? Dim 2 (artifact quality) — correctness for code, planning rigor for plan, architectural soundness for design, requirement coverage for spec. Dim 3 (always-loaded docs) — did the change make CLAUDE.md, AGENTS.md, `.claude/rules/**` or any file the session-start import chain pulls in stale (a command, path, count or convention they state)? Report as a finding. With no spec, shift the weight to Dim 2
  4. Challenge: before categorizing, answer in plain words — Under what condition does the approach fail? What gap is easy to miss? What will be hardest to change 6 months from now?
  5. Categorize: group each finding as Critical (must fix) | Important (should fix) | Suggestion (nice to have)
  6. Verify: the evidence fits the artifact type — tests+lint for code, executability+completeness for plan, trade-off rationale for design, acceptance criteria for spec
  7. Process: classify each finding as a change request, a concern or a question; verify it against the source of truth (file:line, test output) and withdraw or downgrade any finding the evidence does not support. A fix to a Critical or Important finding that changes reviewed code or shipped content comes back for another round, with the earlier findings as acceptance criteria (RULES.md Intent Propagation). Rounds stop when one finds no Critical or Important finding, or when the user accepts the open findings or waives the re-review; leftover Suggestions are reported, not reviewed again. A `/sc:intent --through` run keeps its single fix round
  8. Delegated-decision audit (--audit-delegated): in addition to the Review step, when called on a spec with a "Resolved Decisions" table, re-evaluate only the rows whose `mode` is `delegated` (per the /sc:brainstorm Decision-mode tag step heuristic). The recorded choice was already read in the Gather step, so the re-evaluation goes to one isolated delegate (an independent stream, not a double-check) under the delegate packet rule in core/rules/RULES_DELEGATION.md: it gets each delegated question and its options as recorded (where the spec records none, the question alone; the delegate forms its own candidates and the report notes it), never the recorded choice or a ★/recommendation marker. Limit: a delegate that can read the repo can still find the recorded choice; its files inspected and commands run show whether it did, and the report says so. Surface for each: original Q, delegate's pick, recorded choice, agree/differ; a row whose recorded outcome defers the choice compares against the option the spec recommended, or reports the pick alone when none was recommended. Other rows get no re-evaluation: delegated decisions need this explicit audit, while user-confirmed choices already passed the user's own judgment.
  9. Spec gate: when the target is a `status: draft` spec (--scope spec, or a discovery spec path the Scope step picked), once the user has resolved the findings, append this round to the spec's "Self-Review Iteration Log" section (v1→vN delta); with no Critical finding open and the user's go-ahead, set `status: approved-for-plan`. Without that go-ahead the status stays draft.
  </flow>

  <flags>
  - --scope pr|diff|file|branch|plan|design|spec: command-local artifact-type selector, unrelated to the global --scope analysis-boundary enum (file|module|project|system).
  - --structured: isolated reviewer subagent dispatch, per the Agent entry in the tools section; a `status: draft` spec is always reviewed this way, flag or not.
  - --audit-delegated: delegated-decision audit, per the Delegated-decision audit step.
  </flags>

  <outputs>
  | Artifact | Purpose |
  |---|---|
  | Review summary | Categorized findings (critical/important/suggestion) |
  | Action items | Changes required before merge/approval |
  | Verification | Evidence that fits the artifact type (test output, plan executability, design rationale) |
  </outputs>


  <tools>
  - Agent: dispatch isolated reviewer subagent for big review (--structured), for every `status: draft` spec (the Gather step) and for the --audit-delegated re-eval (the Delegated-decision audit step); Read the delegate packet rule in core/rules/RULES_DELEGATION.md before dispatch, since it sets what the reviewer's prompt leaves out
  </tools>

  <review_lens>
  A domain angle (security, performance, quality, architecture) is a lens, not a separate agent: with --structured it goes into the isolated reviewer's prompt as the lens to apply, next to the artifact and its acceptance criteria. The reviewer is the `self-review` agent, whose `<finding_policy>` reports every finding with severity and confidence.
  </review_lens>

  <examples>
  | Input | Output |
  |---|---|
  | `/sc:review --scope diff` | Review unstaged code changes |
  | `/sc:review src/auth/` | Review all files in auth directory |
  | `/sc:review --scope plan docs/plans/foo.md` | Review plan doc: traceability + gaps + dependencies |
  | `/sc:review --scope design docs/specs/bar.md` | Review design: goal fit + trade-offs + architectural gaps |

  <example name="finding-self-check" type="info">
    Before reporting, the reviewer checks each finding against the source:
    - Keep: "This breaks test_X because [reason]. See [file:line]" — the evidence is cited.
    - Withdraw: the finding assumed pattern A, but module B uses [different pattern] at [file:line].
    - Downgrade to Suggestion: the proposed abstraction has no current consumer, so it is not a must-fix.
  </example>
  </examples>


  <gotchas>
  - scope-focus: with --scope diff|pr|branch, review the changed lines and the code they affect; a file, directory or doc target is reviewed whole
  - no-unsolicited-fixes: flag issues but do not fix them unless asked
  </gotchas>

  <bounds>
    <does>work-product review (code/plan/design/spec), quality analysis, security scan, spec+quality review plus a staleness check on always-loaded docs.</does>
    <never>auto-merge, auto-approve, or modify the artifact without explicit permission; the one exception is the user-approved log entry and status update in the Spec gate step.</never>
    <fallback>No spec: weight the review toward the artifact quality dimension.</fallback>
  </bounds>

  <handoff next="/sc:plan /sc:implement /sc:test /sc:troubleshoot"/>
</component>