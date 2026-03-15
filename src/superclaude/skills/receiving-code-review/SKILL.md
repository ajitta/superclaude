---
name: receiving-code-review
description: |
  Process code review feedback with technical rigor. Verify suggestions before
  implementing, push back on incorrect feedback with evidence.
---

<component name="receiving-code-review" type="skill">

  <role>
    <mission>Evaluate each review comment on its technical merit — verify before implementing, push back when feedback is wrong</mission>
  </role>

  <flow>
    1. Read all comments first: Read every comment before implementing anything — later comments may contradict or supersede earlier ones
    2. Classify each comment: Distinguish between concrete change requests, design concerns, questions seeking clarification, and tentative suggestions — each requires a different response
    3. Verify against the codebase: Before accepting or rejecting, check: Does the referenced function exist? Does the suggested pattern match codebase conventions? Is the edge case actually reachable? Use grep and tests, not assumptions
    4. Evaluate technically: Is the suggestion correct and beneficial? Correct but not worth the churn? Incorrect due to missing context? Incorrect on its merits?
    5. Batch clarifications: If any comments are ambiguous, collect all unclear items into one clarification request before implementing anything
    6. Implement in order: Blocking fixes first (dependency ordering, cascading type changes), then simple one-line fixes, then complex multi-file changes
    7. Test after each change: Run relevant tests after each fix, not only at the end
  </flow>

  <pushback>
  Push back with evidence when a suggestion:
  - Breaks existing functionality: "This causes test_X to fail because [reason]. The current implementation handles [edge case]."
  - Lacks codebase context: "Module B uses [different pattern] for [reason]. See [file:line]."
  - Violates YAGNI: "No current code path uses this abstraction. Deferring until a concrete consumer exists."
  - Is technically incorrect: "The proposed fix introduces [issue]. Reproduction: [steps]."
  Always include what you verified and what you found.
  </pushback>

  <constraints>
  - Do not implement suggestions without verifying them against the codebase first
  - Do not agree with everything — verify each suggestion independently
  - Do not build abstractions for hypothetical future needs — grep for actual consumers first
  - When feedback conflicts with the human partner's prior decisions, check with the human partner before proceeding
  </constraints>

  <bounds will="address all review comments: fixes applied and tested, disagreements responded to with evidence, clarifications resolved" wont="auto-accept suggestions without verification, build speculative abstractions"/>

  <handoff next="verification-before-completion /sc:review"/>
</component>
