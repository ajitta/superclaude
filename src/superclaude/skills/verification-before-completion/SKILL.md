---
name: verification-before-completion
description: |
  Evidence-first verification before any completion claims. Use before committing,
  creating PRs, or claiming work is done. Requires running verification commands and
  confirming output before making success claims. No shortcuts for verification.
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency. The difference between a reliable agent and a reckless one is a single step: confirming the result before announcing it. Core principle: evidence before claims, always.

## The Iron Law

**NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.**

If you have not executed the verification command in this message turn, you cannot claim it passes. Prior runs do not count. Assumptions do not count. Only fresh output counts.

## The Gate Function

Every completion claim must pass through these five gates in order:

1. **IDENTIFY** -- What specific command proves this claim? Name it explicitly.
2. **RUN** -- Execute the full command. No partial runs, no skipped steps, no cached results.
3. **READ** -- Examine the complete output. Check the exit code. Count failures, warnings, errors.
4. **VERIFY** -- Does the output actually confirm the claim? Match evidence to assertion.
5. **ONLY THEN** -- State the claim, citing the evidence.

Skipping any gate invalidates the claim.

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Fresh test output showing 0 failures | Previous run, "should pass" |
| Linter clean | Linter output showing 0 errors/warnings | Partial file check |
| Build succeeds | Build command exit code 0 | Linter passing (different tool) |
| Bug fixed | Reproduce original symptom, confirm gone | "Code changed, assumed fixed" |
| Requirements met | Line-by-line checklist against spec | Tests passing (tests may be incomplete) |

## Red Flags

Stop immediately when you detect any of these:

- Words like **"should"**, **"probably"**, **"seems to"** in a completion statement
- Premature satisfaction language ("Great!", "Done!", "All good!") before running verification
- About to commit or create a PR without running the test suite
- Trusting another agent's success report without independent confirmation
- **Any phrasing that implies success without citing command output from this turn**

## Rationalization Prevention

| Rationalization | Response |
|----------------|----------|
| "Should work now" | Run the verification. "Should" is not evidence. |
| "I'm confident this is correct" | Confidence is not evidence. Execute the command. |
| "Just this once we can skip it" | No exceptions. The one you skip is the one that fails. |
| "The agent reported success" | Verify independently. Trust but verify is insufficient -- verify then trust. |
| "I already checked earlier" | Earlier is not now. Code changed since then. Run it again. |

## Key Patterns

### Test Verification

**Correct:**
```
1. Run full test suite
2. Read output: "42 passed, 0 failed"
3. Report: "All 42 tests pass (verified)"
```

**Wrong:**
```
1. Fix the code
2. Report: "This should fix the failing tests"
```

### Regression TDD

**Correct:**
```
1. Write failing test that reproduces the bug
2. Confirm test fails (run it, see failure)
3. Implement fix
4. Run test again, confirm it passes
5. Run full suite, confirm no regressions
```

**Wrong:**
```
1. Read the bug report
2. Fix the code
3. Report: "Bug fixed"
```

### Build Verification

**Correct:**
```
1. Run build command
2. Check exit code: 0
3. Check output for warnings
4. Report: "Build succeeds with 0 errors, 2 warnings (both cosmetic)"
```

**Wrong:**
```
1. Run linter (passes)
2. Report: "Build is clean" (linter is not build)
```

### Requirements Checklist

**Correct:**
```
1. List each requirement from the spec
2. For each: identify verification method, execute it, record result
3. Report with per-requirement evidence
```

**Wrong:**
```
1. Implement features
2. Run tests
3. Report: "All requirements met" (tests may not cover all requirements)
```

### Agent Delegation

**Correct:**
```
1. Delegate task to subagent
2. When subagent reports completion, run verification yourself
3. Report based on your own verification output
```

**Wrong:**
```
1. Delegate task to subagent
2. Subagent says "done"
3. Report: "Task complete" (you verified nothing)
```

## When To Apply

Apply this skill **every time** before:

- Making any claim that work is complete or correct
- Running `git commit` or `git push`
- Creating or updating a pull request
- Moving on to the next task in a sequence
- Reporting results to the user

There are no exceptions. Verification cost is always lower than the cost of a false completion claim.

## SuperClaude Integration

- Use the `self-review` agent for structured post-implementation validation
- Use `/sc:analyze` for comprehensive multi-dimensional verification
- Pair with `/sc:build` to confirm compilation before claiming build success
- Pair with `/sc:test` to confirm test results before claiming tests pass
