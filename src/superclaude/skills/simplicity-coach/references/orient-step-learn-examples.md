<component name="osl-examples" type="reference" parent="simplicity-coach">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <meta>Referenced from SKILL.md as `references/orient-step-learn-examples.md`</meta>

  <example name="New API Endpoint">
    <orient>
- **Current**: Only a `/users` API exists that returns a user list
- **Goal**: Add `/users/{id}/profile` for detailed user profile retrieval
- **Completion criteria**: GET request returns user name, email, and registration date as JSON
    </orient>
    <step n="1">
Most essential scenario: retrieve one user by id, return only their name.
```python
@app.get("/users/{user_id}/profile")
def get_profile(user_id: int):
    user = db.get_user(user_id)
    return {"name": user.name}
```
    </step>
    <learn n="1">
- Verified it works. Non-existent user_id causes 500 error → need 404 handling.
- DB query unnecessarily fetches all columns → optimize in next step.
    </learn>
    <step n="2">Add 404 handling + return only required fields.</step>
    <learn n="2">
- Error handling pattern inconsistent with other endpoints → consider common error handler.
- **Process bug**: team had no convention for error handling.
    </learn>
  </example>

  <example name="Refactoring Legacy Code">
    <orient>
- **Current**: 5,000-line `utils.py` with all sorts of functions mixed together
- **Goal**: Separate related functions into modules for improved readability
- **Completion criteria**: Each module handles a single concern, all existing tests pass
    </orient>
    <step n="1">Extract largest function group (10 date-related functions) into `date_utils.py`. Fix imports, run tests.</step>
    <learn n="1">
- Tests pass. However, 3 date functions call functions from `string_utils`.
- Potential circular dependency → verify dependency direction in next step.
    </learn>
    <step n="2">Drew dependency graph. string_utils → date_utils direction OK. No reverse dependency. Separated 8 string_utils functions.</step>
    <learn n="2">
- 1 test failed: mock directly referencing `utils.string_format`.
- 3-level feedback applied:
  - Code bug: fix mock path
  - Expectation bug: N/A
  - **Process bug**: hardcoding implementation paths in mocks is fragile during refactoring
    </learn>
  </example>

  <example name="Technology Selection — State Management">
    <orient>
- **Current**: React app, prop drilling 5+ levels deep
- **Goal**: Introduce appropriate state management
- **Completion criteria**: Reduce prop drilling to 2 levels or fewer, minimize bundle size increase
    </orient>
    <dependency_gate>
| Option | Features Used | Build Ourselves? | Reversibility |
|--------|--------------|-------------------|---------------|
| Redux | Global store + selector | Excessive boilerplate | Low (changes entire structure) |
| Zustand | Global store | Replaceable with 3-line hook | Medium |
| React Context | Provider + useContext | Already built-in | High (standard API) |
| Jotai | Atomic state | Hard to implement | Medium |
    </dependency_gate>
    <step n="1">Try React Context first (highest reversibility). Convert only deepest prop drilling chain.</step>
    <learn n="1">
- Reduced from 5 levels to 1. Code much clearer.
- 20 components read from Context → re-rendering concern.
- No actual performance issue. YAGNI: address when it actually becomes a problem.
    </learn>
  </example>

  <example name="Dependency Audit">
    <orient>
- **Current**: 47 direct dependencies in `package.json`. 1,200 packages in `node_modules`.
    </orient>
    <step n="1" title="Identify Unused">
```bash
npx depcheck
```
Result: 8 unused dependencies found.
    </step>
    <learn n="1">3 of 8 implicitly used by build tools → actually unused: 5. Removed 5, build/tests pass.</learn>
    <step n="2" title="Identify Replaceable">
`moment.js` (300KB) → Functions used: `format()`, `diff()`, `isValid()` — only 3.
Replaced with native `Intl.DateTimeFormat` + 20-line utility function.
    </step>
    <learn n="2">
- Bundle size reduced by 280KB, build time reduced by 2 seconds
- `'Do'` format ("1st", "2nd") not native → solved with 10 extra lines
- **Process bug**: moment.js added at project start with "everyone uses it" as only reason
    </learn>
  </example>

  <example name="Debugging — 3-Level Feedback">
    <bug>Form submission intermittently fails to save data.</bug>
    <level n="1" title="Bug in the Code">
Race condition — two async requests fire simultaneously, one gets ignored.
Fix: apply debounce.
    </level>
    <level n="2" title="Bug in Expectations">
Tests only verify "data is saved on form submission." No concurrent submission test.
Fix: add concurrent submission tests.
    </level>
    <level n="3" title="Bug in the Process">
Why did this race condition occur?
- No disable on button → users click multiple times
- No UI feedback (loading spinner) → users think "it didn't register"
Root cause: project had no UI feedback pattern for async operations.
Fix: establish UI feedback guidelines for async operations.
    </level>
    <insight>Recording this 3-level analysis in DAYBOOK.md builds intuition to detect similar patterns.</insight>
  </example>
</component>
