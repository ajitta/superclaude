---
name: systematic-debugging
description: |
  Four-phase root cause investigation before proposing any fix. Use when encountering
  bugs, test failures, or unexpected behavior. Requires hypothesis generation, evidence
  gathering, and verification before implementing fixes.
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Every "quick patch" that skips root cause analysis adds tech debt, masks the real problem, and erodes trust in the codebase. The cost of a proper investigation is always less than the cost of three wrong guesses stacked on top of each other.

**Core Principle**: ALWAYS find root cause before attempting fixes.

## The Iron Law

> NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.

This is non-negotiable. Even under time pressure — especially under time pressure — skipping investigation leads to longer resolution times. A 10-minute investigation that identifies root cause beats an hour of trial-and-error patching every single time.

## When to Use

Apply this skill to ANY technical issue:

- Test failures (unit, integration, e2e)
- Runtime bugs and exceptions
- Unexpected behavior or wrong output
- Performance degradation
- Build and compilation failures
- Deployment and infrastructure errors
- Flaky or intermittent failures

**ESPECIALLY under time pressure.** The temptation to skip investigation grows with urgency, but that is exactly when discipline matters most.

## The Four Phases

Complete each phase fully before proceeding to the next. Do not skip ahead.

### Phase 1: Root Cause Investigation

Goal: Understand what is actually happening vs what should happen.

**Read error messages carefully.**
- Read the entire stack trace, not just the first line.
- Note the originating file, line number, and function.
- Read inner/wrapped exceptions — the root cause is often buried.
- Check for multiple errors — the first one may cause the rest.

**Reproduce consistently.**
- Write down exact steps to trigger the issue.
- Can you reproduce every time? If not, identify what varies.
- Isolate the minimal reproduction case.
- Note environment specifics: OS, versions, config.

**Check recent changes.**
- `git diff` and `git log` — what changed since it last worked?
- New dependencies added or upgraded?
- Configuration or environment variable changes?
- Infrastructure or deployment changes?

**Gather evidence in multi-component systems.**
- Log at each boundary (API calls, database queries, message queues).
- Verify inputs and outputs at every layer.
- Check network calls, timeouts, and response codes.
- Confirm which component owns the failure.

**Trace data flow.**
- Where does the bad value first appear?
- Trace upstream from the symptom to the origin.
- Check type conversions, serialization, and encoding boundaries.
- Verify assumptions about data shape at each step.

### Phase 2: Pattern Analysis

Goal: Understand why this specific case fails when similar cases succeed.

**Find working examples in the same codebase.**
- Locate similar functionality that works correctly.
- Find passing tests that exercise related code paths.
- Check if the same operation works with different inputs.

**Compare working vs broken.**
- List every difference between the working and broken case.
- Differences in input data, configuration, timing, or environment.
- Differences in code path, dependencies, or state.
- Narrow the list — which differences could cause the symptom?

**Understand dependencies and assumptions.**
- What does the broken code assume about its inputs?
- What does it assume about external state (DB, filesystem, network)?
- Are there ordering or timing assumptions?
- Are there version or compatibility assumptions?

### Phase 3: Hypothesis and Testing

Goal: Form a single testable theory and validate it.

**Form a single specific hypothesis.**
- State it clearly: "X is the root cause because Y."
- It must explain all observed symptoms.
- It must explain why working cases work and broken cases break.
- If you cannot form a specific hypothesis, return to Phase 1 — you need more evidence.

**Test minimally.**
- Change one variable at a time.
- Make the smallest possible change to validate or invalidate.
- Use logging, assertions, or debugger breakpoints — not code changes.
- Record the result clearly: confirmed or refuted.

**Evaluate and iterate.**
- Hypothesis confirmed: proceed to Phase 4.
- Hypothesis refuted: form a new hypothesis from updated evidence. Do NOT reuse the same fix with slight variations.
- If three hypotheses fail, step back. Re-examine Phase 1 evidence. You may be looking at the wrong component entirely.

### Phase 4: Implementation

Goal: Fix the root cause with a single, verified change.

**Create a failing test case.**
- Write a test that reproduces the exact failure.
- Confirm the test fails before implementing the fix.
- Use the test-driven-development skill for guidance.

**Implement a single fix.**
- ONE change that addresses the root cause.
- No "while I'm here" secondary fixes — they confuse the commit history and risk regressions.
- The fix should be proportional to the problem.

**Verify the fix.**
- The failing test now passes.
- All existing tests still pass (no regressions).
- Manual verification in the original reproduction scenario.
- If the fix does not work, return to Phase 3 with new evidence.

**Escalation rule.**
- If 3+ fix attempts have failed, STOP.
- Question your architectural assumptions.
- Discuss with the user — you may be solving the wrong problem.
- Consider whether the issue is a symptom of a deeper design flaw.

## Red Flags

Stop immediately if you catch yourself doing any of these:

1. **"Quick fix for now"** — there is no such thing; temporary fixes become permanent.
2. **"Just try changing X"** — random mutation is not debugging.
3. **Proposing solutions before reading the error message** — the answer is often in the output you skipped.
4. **Changing multiple things at once** — you will not know which change worked.
5. **Copying a fix from a different bug** — similar symptoms do not mean same cause.
6. **Ignoring test failures after your fix** — regressions are new bugs you just created.
7. **"It works on my machine"** — environment differences are root causes, not excuses.
8. **Adding try/catch to suppress errors** — hiding symptoms makes the next failure harder to debug.
9. **Reverting to a working version without understanding why** — the bug is still there, waiting.
10. **Skipping reproduction** — if you cannot reproduce it, you cannot verify you fixed it.

## Common Rationalizations

| Rationalization | Why It Is Wrong | What to Do Instead |
|---|---|---|
| "This is a simple bug" | Simple bugs do not resist the first fix attempt | If it were simple, you would already know the root cause |
| "I have seen this before" | Pattern matching without evidence leads to wrong fixes | Verify the pattern matches this specific case |
| "We do not have time to investigate" | You do not have time to NOT investigate — failed fixes cost more | A 10-minute investigation saves an hour of guessing |
| "Let me just try this one thing" | One thing becomes five things becomes a rewrite | Form a hypothesis first, then test it |
| "The error message is misleading" | Sometimes true, but check before assuming | Read it literally first, then consider misdirection |
| "It must be a library bug" | Possible but unlikely — your code is the usual suspect | Prove it with a minimal reproduction outside your code |
| "I will clean it up later" | Later never comes; the hack stays forever | Fix it correctly now or document the tech debt explicitly |
| "The tests are wrong" | Sometimes true, but prove it before changing them | Understand what the test expects and why before modifying |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|---|---|---|
| 1. Root Cause Investigation | Read errors, reproduce, check changes, trace data flow | Can explain what happens and where it diverges from expected |
| 2. Pattern Analysis | Find working examples, compare differences, check assumptions | Can explain why this case fails and similar cases succeed |
| 3. Hypothesis and Testing | Form specific hypothesis, test one variable, evaluate result | Have a confirmed root cause with evidence |
| 4. Implementation | Write failing test, single fix, verify no regressions | Test passes, no regressions, root cause eliminated |

## SuperClaude Integration

This skill connects to the broader SuperClaude workflow:

- **Trigger command**: Use `/sc:troubleshoot` to initiate structured debugging sessions.
- **Specialist agent**: The `root-cause-analyst` agent is purpose-built for deep investigation and can be delegated to for complex multi-component issues.
- **Handoff to fix**: Once root cause is confirmed, hand off to the `test-driven-development` skill to implement the fix with proper test coverage.

The sequence is: `/sc:troubleshoot` (investigate) -> `systematic-debugging` (this skill, root cause) -> `test-driven-development` (implement fix).
