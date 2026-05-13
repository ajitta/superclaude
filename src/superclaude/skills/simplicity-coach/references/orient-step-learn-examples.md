<component name="osl-examples" type="reference" parent="simplicity-coach">
  <meta>Referenced from SKILL.md as `references/orient-step-learn-examples.md`</meta>

  <example name="New API Endpoint">
Orient: Only `/users` API exist → add `/users/{id}/profile` → done when GET return name, email, reg date as JSON

Step 1: Get one user by id, return only name.
```python
@app.get("/users/{user_id}/profile")
def get_profile(user_id: int):
    user = db.get_user(user_id)
    return {"name": user.name}
```
Learn 1: Work. Bad user_id → 500 → need 404. DB fetch all cols → optimize next.

Step 2: Add 404 + return only needed fields.
Learn 2: Error handling inconsistent with other endpoints → need common handler. Process bug: no team convention for error handling.
  </example>

  <example name="Refactoring Legacy Code">
Orient: 5,000-line `utils.py` everything mixed → split into modules → done when each module = single concern, all tests pass

Step 1: Pull 10 date funcs into `date_utils.py`. Fix imports, run tests.
Learn 1: Tests pass. 3 date funcs call `string_utils` → maybe circular dep → check next.

Step 2: Dep graph show string_utils → date_utils OK, no reverse. Split 8 string_utils funcs.
Learn 2: 1 test fail — mock point at `utils.string_format` direct. 3-level feedback: code bug (fix mock path), expectation bug (N/A), process bug (hardcode paths in mocks fragile when refactor).
  </example>

  <example name="Technology Selection — State Management">
Orient: React app, prop drill 5+ deep → add state mgmt → done when drill ≤2, bundle grow small

Dependency gate:
| Option | Features Used | Build Ourselves? | Reversibility |
|--------|--------------|-------------------|---------------|
| Redux | Global store + selector | Too much boilerplate | Low |
| Zustand | Global store | Swap with 3-line hook | Medium |
| React Context | Provider + useContext | Built-in already | High |
| Jotai | Atomic state | Hard to build | Medium |

Step 1: Try React Context first (most reversible). Convert only deepest drill chain.
Learn 1: 5 levels → 1. Clearer. 20 components read Context → re-render worry. No real perf issue now. YAGNI: fix when problem real.
  </example>

  <example name="Dependency Audit">
Orient: 47 direct deps in `package.json`, 1,200 packages in `node_modules`

Step 1 (find unused): `npx depcheck` → 8 unused. 3 used by build tools → real unused: 5. Drop 5, build/tests pass.

Step 2 (find replaceable): `moment.js` (300KB) → only 3 funcs used: `format()`, `diff()`, `isValid()`. Swap for native `Intl.DateTimeFormat` + 20-line util.
Learn 2: Bundle -280KB, build -2s. `'Do'` format not native → 10 extra lines. Process bug: moment.js added because "everyone use it."
  </example>

  <example name="Debugging — 3-Level Feedback">
Bug: Form submit sometimes fail to save.

Level 1 (code): Race — two async reqs, one dropped. Fix: debounce.
Level 2 (expectation): Tests only check single submit. Fix: add concurrent submit tests.
Level 3 (process): No button disable → multi-click. No spinner → user retry. Root cause: no UI feedback pattern for async ops. Fix: set guidelines.

Log this 3-level analysis in DAYBOOK.md → build intuition to spot similar patterns.
  </example>
</component>