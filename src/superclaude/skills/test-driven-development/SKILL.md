---
name: test-driven-development
description: |
  Enforce RED-GREEN-REFACTOR cycle for all feature and bugfix implementation.
  Use before writing any implementation code. Write failing test first, then
  minimal code to pass. No production code without a failing test.
---

# Test-Driven Development

## Overview

Write the test first. Watch it fail. Write the minimum code to make it pass.

This is not optional discipline — it is the only reliable way to know your test actually verifies the behavior you think it does. If you never watched a test fail, you have no evidence it tests the right thing. A test that has never been red is decoration.

## When to Use

**Always** for:
- New features
- Bug fixes
- Refactoring that changes behavior
- Adding edge case handling
- Any code that could break silently

**Exceptions** require explicit user permission. There are no implicit exceptions.

## The Iron Law

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.**

If you wrote implementation code before writing a test, delete it. Start over. The cycle only works when the test comes first. Writing code first and then testing it is verification, not TDD — and it misses the entire point.

## Red-Green-Refactor Cycle

### 1. RED: Write One Minimal Failing Test

Write exactly one test for exactly one behavior. Do not write multiple tests at once.

**Good — tests one specific behavior:**
```python
def test_user_email_rejects_missing_at_sign():
    with pytest.raises(ValidationError):
        User(email="invalid-email")
```

**Bad — tests too many things at once:**
```python
def test_user_validation():
    with pytest.raises(ValidationError):
        User(email="invalid-email")
    with pytest.raises(ValidationError):
        User(email="")
    assert User(email="a@b.com").email == "a@b.com"
    assert User(email="a@b.com").is_active is True
```

### 2. Verify RED (MANDATORY)

Run the test. Confirm it fails for the reason you expect.

```bash
uv run pytest tests/unit/test_user.py::test_user_email_rejects_missing_at_sign -v
```

Read the failure output. If it fails for the wrong reason (import error, typo, wrong exception type), fix the test before proceeding. The failure message must describe the missing behavior, not a broken test.

**Do not skip this step.** This is where you learn whether your test is actually testing what you intend.

### 3. GREEN: Write the Simplest Code to Pass

Write the absolute minimum code that makes the failing test pass. Nothing more.

**Good — minimal implementation:**
```python
class User:
    def __init__(self, email: str):
        if "@" not in email:
            raise ValidationError("Invalid email")
        self.email = email
```

**Bad — speculative implementation (YAGNI violation):**
```python
class User:
    def __init__(self, email: str):
        if "@" not in email:
            raise ValidationError("Invalid email")
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            raise ValidationError("Invalid email format")
        self.email = email
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.login_count = 0
```

The regex, `is_active`, `created_at`, and `login_count` are not required by any failing test. They do not belong here yet.

### 4. Verify GREEN (MANDATORY)

Run the test suite. Confirm the new test passes and no existing tests broke.

```bash
uv run pytest tests/unit/ -v
```

If anything regressed, fix it before moving forward. A green bar means all tests pass, not just the new one.

### 5. REFACTOR: Clean Up While Staying Green

With all tests passing, improve the code structure. Extract helpers, rename for clarity, remove duplication. Run tests after every change to confirm you stay green.

```bash
uv run pytest tests/unit/ -v
```

If a refactor breaks a test, undo it immediately. Refactoring means changing structure without changing behavior.

### 6. Repeat

Go back to step 1 with the next behavior.

## What Makes a Good Test

| Property | Meaning | Example |
|----------|---------|---------|
| Minimal | Tests one thing only | `test_rejects_negative_age` not `test_user_validation` |
| Clear | Name describes the expected behavior | `test_returns_empty_list_when_no_matches` |
| Real | Uses actual objects when possible | Construct a real `User`, don't mock everything |
| Fast | Runs in milliseconds | No network, no database, no filesystem unless necessary |
| Deterministic | Same result every run | No random data, no time-dependent logic |
| Independent | No shared state between tests | Each test sets up its own data |

## Why Order Matters

**Tests-first** (TDD) forces you to:
- Define the exact behavior before implementing it
- Discover edge cases while thinking about inputs and outputs
- Write only the code you need
- Produce tests that actually catch regressions

**Tests-after** lets you:
- Write tests that pass immediately, proving nothing
- Skip edge cases you forgot about during implementation
- Unconsciously shape tests around existing code rather than desired behavior
- Rationalize skipping tests for "simple" code

A test you write after implementation will almost always pass on first run. That means you have zero evidence it would catch a regression.

## Common Rationalizations

| Rationalization | Why It Is Wrong |
|----------------|-----------------|
| "This is too simple to need a test" | Simple code gets called by complex code. When it breaks, you will not know where the bug is. |
| "I will write the tests after" | You will not. And if you do, they will be shaped around the implementation, not the requirements. |
| "I tested it manually" | Manual testing is not repeatable. It vanishes the moment you finish. |
| "Writing the test first is slower" | Writing the test first prevents debugging sessions that take 10x longer. |
| "I already know the implementation" | Then the test will take 30 seconds to write. Do it anyway. |
| "Deleting working code is wasteful" | Keeping untested code is technical debt. Deleting it costs seconds; debugging it costs hours. |
| "Just this once, I will skip the test" | Every codebase with poor test coverage started with "just this once." |
| "The test is obvious from the code" | If it is obvious, it takes one minute to write. You do not get to skip obvious tests. |
| "I need to prototype first" | Prototypes become production code. Write the test, then prototype to green. |
| "Mocking is too hard for this" | If it is hard to test, the design needs to change. That is valuable feedback. |

## Red Flags

Stop and reassess if you observe any of these:

- **Code written before a test exists** — delete it, write the test first
- **A new test passes immediately** — the test is not testing new behavior, or the behavior already exists and you do not need new code
- **Rationalizing "just this once"** — this is the beginning of abandoning the practice
- **Multiple tests written before any code** — write one test, make it pass, then write the next
- **Test names describe implementation** — `test_calls_validate_method` instead of `test_rejects_invalid_input`
- **Mocking the thing you are testing** — you are testing the mock, not the code

## Verification Checklist

Before considering any task complete:

- [ ] Every new function/method has at least one test
- [ ] Every test was watched failing (RED) before implementation
- [ ] Implementation is minimal — no speculative code
- [ ] All tests pass (GREEN) with zero warnings
- [ ] No skipped tests without documented reason
- [ ] Test names describe behavior, not implementation

## Bug Fix Example

A user reports that empty emails are accepted. Apply TDD:

### RED — Write the failing test

```python
def test_rejects_empty_email():
    with pytest.raises(ValidationError, match="empty"):
        User(email="")
```

Run it:

```bash
uv run pytest tests/unit/test_user.py::test_rejects_empty_email -v
```

Confirm it fails because empty string passes validation (the bug).

### GREEN — Add the minimal fix

```python
class User:
    def __init__(self, email: str):
        if not email:
            raise ValidationError("Email cannot be empty")
        if "@" not in email:
            raise ValidationError("Invalid email")
        self.email = email
```

Run the full suite:

```bash
uv run pytest tests/unit/ -v
```

Confirm the new test passes and nothing else broke.

### REFACTOR — Extract if needed

If validation logic is growing, extract it:

```python
def _validate_email(email: str) -> None:
    if not email:
        raise ValidationError("Email cannot be empty")
    if "@" not in email:
        raise ValidationError("Invalid email")

class User:
    def __init__(self, email: str):
        _validate_email(email)
        self.email = email
```

Run tests again. Still green. Done.

## SuperClaude Integration

- Use the `/sc:test` command to run targeted test suites during the cycle
- Use the `quality-engineer` agent for comprehensive test coverage analysis
- All examples in this skill use `uv run pytest` — the project standard
- After completing TDD cycles, hand off to the verification-before-completion skill to confirm nothing was missed

<handoff next="/sc:test /sc:review"/>
