---
name: systematic-debugging
description: |
  Root cause investigation before proposing any fix. Use when encountering
  bugs, test failures, or unexpected behavior.
---

## Purpose

Find the root cause before attempting a fix. Investigation first, implementation second.

## When to Use

- Test failures (unit, integration, e2e)
- Runtime bugs and exceptions
- Unexpected behavior or wrong output
- Performance degradation
- Build/compilation failures
- Flaky or intermittent failures

## Workflow

1. **Reproduce**: Confirm the failure. Read the full error output including inner exceptions. Identify exact steps to trigger it and note what varies.
2. **Investigate**: Check `git log` and `git diff` for recent changes. Trace data flow from symptom back to origin. Find working examples of similar functionality and compare differences.
3. **Hypothesize**: Form a single specific hypothesis — "X causes Y because Z." It should explain all observed symptoms. Test it by changing one variable at a time.
4. **Confirm or iterate**: If the hypothesis holds, proceed to fix. If refuted, form a new hypothesis from updated evidence. Do not reuse the same approach with slight variations.
5. **Write a failing test**: Create a test that reproduces the exact failure. Confirm it fails before implementing the fix.
6. **Fix**: Make one change that addresses the root cause. No "while I'm here" secondary fixes.
7. **Verify**: The failing test passes. All existing tests still pass. Manual verification in the original reproduction scenario confirms the fix.

## Constraints

- Do not propose a fix before you can explain the root cause.
- After 3+ failed fix attempts, stop and reconsider your approach. You may be looking at the wrong component entirely — discuss with the user.
- Change one variable at a time when testing hypotheses.
- Do not suppress errors with try/catch as a "fix."
- Do not revert to a working version without understanding why the current version fails.

## Completion

Root cause is identified with evidence. A failing test locks the fix. All tests pass with no regressions.

## Next

Hand off to `test-driven-development` for implementation. Use `/sc:troubleshoot` to initiate structured debugging sessions.
