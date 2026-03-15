---
name: systematic-debugging
description: |
  Root cause investigation before proposing any fix. Use when encountering
  bugs, test failures, or unexpected behavior.
---
<component name="systematic-debugging" type="skill">

  <role>
    <mission>Find the root cause before attempting a fix. Investigation first, implementation second</mission>
  </role>

  <when>
  - Test failures (unit, integration, e2e)
  - Runtime bugs and exceptions
  - Unexpected behavior or wrong output
  - Performance degradation
  - Build/compilation failures
  - Flaky or intermittent failures
  </when>

  <flow>
    1. Reproduce — Confirm the failure. Read the full error output including inner exceptions. Identify exact steps to trigger it and note what varies
    2. Investigate — Check `git log` and `git diff` for recent changes. Trace data flow from symptom back to origin. Find working examples of similar functionality and compare differences
    3. Hypothesize — Form a single specific hypothesis — "X causes Y because Z." It should explain all observed symptoms. Test it by changing one variable at a time
    4. Confirm or iterate — If the hypothesis holds, proceed to fix. If refuted, form a new hypothesis from updated evidence. Do not reuse the same approach with slight variations
    5. Write a failing test — Create a test that reproduces the exact failure. Confirm it fails before implementing the fix
    6. Fix — Make one change that addresses the root cause. No "while I'm here" secondary fixes
    7. Verify — The failing test passes. All existing tests still pass. Manual verification in the original reproduction scenario confirms the fix
  </flow>

  <constraints>
  - Do not propose a fix before you can explain the root cause
  - After 3+ failed fix attempts, stop and reconsider your approach. You may be looking at the wrong component entirely — discuss with the user
  - Change one variable at a time when testing hypotheses
  - Do not suppress errors with try/catch as a "fix"
  - Do not revert to a working version without understanding why the current version fails
  </constraints>

  <bounds will="root cause investigation|hypothesis testing|evidence-based diagnosis|regression testing" wont="propose fixes before root cause|suppress errors|make secondary fixes"/>

  <handoff next="test-driven-development /sc:troubleshoot"/>
</component>
