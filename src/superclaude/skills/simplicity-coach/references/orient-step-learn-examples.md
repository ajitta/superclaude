<component name="osl-examples" type="reference" parent="simplicity-coach">
  <meta>Referenced from SKILL.md as `references/orient-step-learn-examples.md`</meta>

  <example name="New API Endpoint">
Orient: Only `/users` API exists → add `/users/{id}/profile` → done when GET returns name, email, registration date as JSON

Step 1: Retrieve one user by id, return only name.
```python
@app.get("/users/{user_id}/profile")
def get_profile(user_id: int):
    user = db.get_user(user_id)
    return {"name": user.name}
```
Learn 1: Works. Non-existent user_id → 500 error → need 404. DB fetches all columns → optimize next.

Step 2: Add 404 handling + return only required fields.
Learn 2: Error handling inconsistent with other endpoints → common handler needed. Process bug: no team convention for error handling.
  </example>

  <example name="Refactoring Legacy Code">
Orient: 5,000-line `utils.py` with everything mixed → separate into modules → done when each module = single concern, all tests pass

Step 1: Extract 10 date functions into `date_utils.py`. Fix imports, run tests.
Learn 1: Tests pass. 3 date functions call `string_utils` → potential circular dependency → verify next.

Step 2: Dependency graph shows string_utils → date_utils OK, no reverse. Separated 8 string_utils functions.
Learn 2: 1 test failed — mock referencing `utils.string_format` directly. 3-level feedback: code bug (fix mock path), expectation bug (N/A), process bug (hardcoding paths in mocks is fragile during refactoring).
  </example>

  <example name="Technology Selection — State Management">
Orient: React app, prop drilling 5+ levels deep → introduce state management → done when drilling ≤2 levels, minimal bundle increase

Dependency gate:
| Option | Features Used | Build Ourselves? | Reversibility |
|--------|--------------|-------------------|---------------|
| Redux | Global store + selector | Excessive boilerplate | Low |
| Zustand | Global store | Replaceable with 3-line hook | Medium |
| React Context | Provider + useContext | Already built-in | High |
| Jotai | Atomic state | Hard to implement | Medium |

Step 1: Try React Context first (highest reversibility). Convert only deepest prop drilling chain.
Learn 1: 5 levels → 1. Much clearer. 20 components read Context → re-rendering concern. No actual perf issue now. YAGNI: address when it becomes a problem.
  </example>

  <example name="Dependency Audit">
Orient: 47 direct deps in `package.json`, 1,200 packages in `node_modules`

Step 1 (identify unused): `npx depcheck` → 8 unused found. 3 implicitly used by build tools → actually unused: 5. Removed 5, build/tests pass.

Step 2 (identify replaceable): `moment.js` (300KB) → only 3 functions used: `format()`, `diff()`, `isValid()`. Replaced with native `Intl.DateTimeFormat` + 20-line utility.
Learn 2: Bundle -280KB, build -2s. `'Do'` format not native → 10 extra lines. Process bug: moment.js added because "everyone uses it."
  </example>

  <example name="Debugging — 3-Level Feedback">
Bug: Form submission intermittently fails to save data.

Level 1 (code): Race condition — two async requests, one ignored. Fix: debounce.
Level 2 (expectation): Tests only verify single submission. Fix: add concurrent submission tests.
Level 3 (process): No button disable → multi-click. No loading spinner → user retries. Root cause: no UI feedback pattern for async operations. Fix: establish guidelines.

Recording this 3-level analysis in DAYBOOK.md builds intuition to detect similar patterns.
  </example>
</component>
