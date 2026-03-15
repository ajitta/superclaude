---
name: verification-before-completion
description: |
  Evidence-first verification before any completion claims. Use before committing,
  creating PRs, or claiming work is done.
---

<component name="verification-before-completion" type="skill">

  <role>
    <mission>Evidence-first verification before any completion claims</mission>
  </role>

  <when>
  - Before claiming work is complete
  - Before running git commit or git push
  - Before creating or updating a pull request
  - Before moving to the next task in a sequence
  </when>

  <flow>
    1. Baseline: If a test suite exists and hasn't been captured this session, run it NOW and record pass/fail counts as pre-change baseline
    2. Identify: Determine the specific command that proves the claim (test suite, build, linter)
    3. Run: Execute the full command — no partial runs or cached results
    4. Read: Examine complete output — check exit code, count failures, warnings, errors
    5. Compare: Verify pass count >= baseline — any new failures = regression, fix before claiming done
    6. Confirm: Does the output actually support the claim? Match evidence to assertion
    7. Report: State the claim citing evidence (e.g., "42/42 tests pass, baseline was 40 — 2 new tests added, 0 regressions")
  </flow>

  <baseline_capture note="Test baseline pattern — advisory, not gate">
  Run the project's test suite BEFORE making any changes. Record:
  - Total tests, passed, failed, skipped
  - Timestamp of baseline run

  After implementation, compare:
  - Pass count must be >= baseline (no regressions)
  - New failures require investigation before completion
  - New tests should increase total count

  If no test suite exists, note "no baseline available" and skip comparison.
  </baseline_capture>

  <revert_verify note="For bug fixes with new tests">
  1. Write the test, confirm it passes with the fix applied
  2. Revert the fix, run the test — it should FAIL (proves test catches the bug)
  3. Restore the fix, run the test — it should PASS
  4. Run full suite — confirm no regressions against baseline
  </revert_verify>

  <constraints>
  - Never use "should pass" or "probably works" — cite actual output
  - Prior test runs do not count — run verification fresh after changes
  - If a subagent reports completion, verify independently before reporting upstream
  - Do not conflate tools (linter passing does not mean build succeeds)
  </constraints>

  <bounds will="evidence-based verification with baseline comparison" wont="skip verification or accept cached results"/>

  <handoff next="/sc:build /sc:test"/>
</component>
