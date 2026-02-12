# Orient-Step-Learn Applied Examples

> This document is referenced from SKILL.md as `references/orient-step-learn-examples.md`.
> It contains concrete examples of applying the Orient-Step-Learn framework.

---

## Example 1: Developing a New API Endpoint

### Orient
- **Current**: Only a `/users` API exists that returns a user list
- **Goal**: Add `/users/{id}/profile` for detailed user profile retrieval
- **Completion criteria**: GET request returns user name, email, and registration date as JSON

### Step 1
Most essential scenario: an endpoint that retrieves one user by id and returns only their name.
```python
@app.get("/users/{user_id}/profile")
def get_profile(user_id: int):
    user = db.get_user(user_id)
    return {"name": user.name}
```

### Learn 1
- Verified it works. A non-existent user_id causes a 500 error → need 404 handling.
- DB query unnecessarily fetches all columns → optimize in the next step.

### Step 2
Add 404 handling + modify to return only the required fields.

### Learn 2
- Found that the error handling pattern is inconsistent with other endpoints → consider a common error handler.
- This is a process bug: the team had no convention for error handling.

---

## Example 2: Refactoring Legacy Code

### Orient
- **Current**: A 5,000-line `utils.py` with all sorts of functions mixed together
- **Goal**: Separate related functions into modules for improved readability
- **Completion criteria**: Each module handles a single concern, and all existing tests pass

### Step 1
Extract only the largest function group (10 date-related functions) into `date_utils.py`.
Fix imports, run tests.

### Learn 1
- Tests pass. However, 3 of the date functions call functions from `string_utils`.
- Potential circular dependency found → need to verify dependency direction in the next step.

### Step 2
Drew a dependency graph. string_utils → date_utils direction is OK. No reverse dependency confirmed.
Separated 8 string_utils-related functions.

### Learn 2
- 1 test failed after separation: a mock was directly referencing `utils.string_format`.
- Applied the 3-level feedback:
  - Code bug: Fix the mock path
  - Expectation bug: Not applicable
  - Process bug: The pattern of hardcoding implementation paths in mocks is fragile during refactoring

---

## Example 3: Technology Selection — State Management

### Orient
- **Current**: In a React app, prop drilling has gone 5+ levels deep
- **Goal**: Introduce appropriate state management
- **Completion criteria**: Reduce prop drilling to 2 levels or fewer, minimize bundle size increase

### Applying the Dependency Questions
| Option | Features Used | Can Build Ourselves? | Reversibility |
|--------|--------------|---------------------|---------------|
| Redux | Global store + selector | Excessive boilerplate | Low (changes entire structure) |
| Zustand | Global store | Replaceable with a 3-line hook | Medium |
| React Context | Provider + useContext | Already built-in | High (standard API) |
| Jotai | Atomic state | Hard to implement ourselves | Medium |

### Step 1
Try React Context first, as it has the highest reversibility.
Convert only the deepest prop drilling chain to Context.

### Learn 1
- Reduced from 5 levels to 1. Code is much clearer.
- However, 20 components read from the Context → re-rendering concern.
- No actual performance issue currently. YAGNI principle: address performance when it actually becomes a problem.

---

## Example 4: Dependency Audit

### Project Context
47 direct dependencies in `package.json`. 1,200 packages in `node_modules`.

### Step 1: Identify Unused Dependencies
```bash
npx depcheck
```
Result: 8 unused dependencies found.

### Learn 1
3 of the 8 are implicitly used by build tools → actually unused: 5.
Removed 5, confirmed build/tests pass.

### Step 2: Identify Replaceable Dependencies
`moment.js` (300KB) → Functions used in the project: `format()`, `diff()`, `isValid()` — only 3.
Replaced the 3 functions with native `Intl.DateTimeFormat` and a 20-line utility function.

### Learn 2
- Bundle size reduced by 280KB
- Build time reduced by 2 seconds
- One date format (`'Do'` — "1st", "2nd", etc.) not possible natively → solved with 10 extra lines
- Process bug: moment.js was added at project start with "everyone uses it" as the only reason

---

## Example 5: Debugging — 3-Level Feedback

### Bug
Form submission intermittently fails to save data.

### Level 1: Bug in the Code
Race condition — when two async requests fire simultaneously, one gets ignored.
Fix: Apply debounce.

### Level 2: Bug in Expectations
Tests only verify "data is saved on form submission."
No test for concurrent submission scenarios.
Fix: Add concurrent submission tests.

### Level 3: Bug in the Process
Why did this race condition occur?
- No disable on the button, allowing users to click multiple times
- No UI feedback (loading spinner), making users think "it didn't register" and click again

Root cause: The project had no UI feedback pattern for async operations.
Fix: Establish UI feedback guidelines for async operations.

Recording this 3-level analysis in DAYBOOK.md builds intuition to instinctively detect similar patterns in the future.
