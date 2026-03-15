---
name: verification-before-completion
description: |
  Evidence-first verification before any completion claims. Use before committing,
  creating PRs, or claiming work is done.
---

## Purpose

Run the verification command, read the output, confirm the result — then make the claim. Evidence before claims.

## When to Use

- Before claiming work is complete
- Before running `git commit` or `git push`
- Before creating or updating a pull request
- Before moving to the next task in a sequence

## Workflow

1. **Identify**: Determine the specific command that proves the claim (test suite, build, linter).
2. **Run**: Execute the full command. No partial runs or cached results.
3. **Read**: Examine the complete output. Check exit code. Count failures, warnings, errors.
4. **Confirm**: Does the output actually support the claim? Match evidence to assertion.
5. **Report**: State the claim, citing the evidence (e.g., "All 42 tests pass — verified").

## Revert-Verify for Regression

When fixing a bug with a new test:

1. Write the test and confirm it passes with the fix applied.
2. Revert the fix, run the test again — it should fail (proves the test catches the bug).
3. Restore the fix, run the test again — it should pass.
4. Run the full suite to confirm no regressions.

## Constraints

- Do not use "should pass" or "probably works" in completion statements. Cite actual output.
- Prior test runs do not count — run verification fresh after your changes.
- If a subagent reports completion, verify independently before reporting upstream.
- Do not conflate different tools (linter passing does not mean build succeeds).

## Completion

Every claim is backed by fresh command output from the current turn.

## Next

Use `/sc:build` and `/sc:test` to run verification. Use the `self-review` agent for structured post-implementation validation.
