<component name="playwright" type="mcp">
  <role>
    <mission>Browser automation and E2E testing with real browser interaction</mission>
  </role>

  ## Activation
  Not always active. When browser testing is needed:
  1. `mcp-find("playwright")` — locate in MCP Docker catalog
  2. `mcp-add("playwright")` — activate for current session
  3. Tools become available immediately

  <choose>
  Use:
  - User journey validation: login → navigate → action → verify state
  - Form testing: input, validation, submission, error display
  - Visual regression: screenshots before/after, responsive breakpoints
  - Accessibility: automated WCAG checks against rendered DOM
  - SPA behavior: client-side routing, lazy loading, dynamic content

  Avoid:
  - Unit tests: component logic → native test runner (vitest, jest)
  - API testing: backend endpoints → native HTTP tools (curl, fetch)
  - Static analysis: code quality → native Claude + /sc:review
  - Performance metrics: CWV, profiling → Chrome DevTools (--perf)
  </choose>

  ## Test Patterns
  - **Smoke test**: navigate → verify critical elements visible → screenshot
  - **User flow**: login → perform action → assert outcome → logout
  - **Responsive**: resize viewport → screenshot → compare breakpoints
  - **Error path**: trigger error → verify error UI → verify recovery

  ## Assertion Strategy
  - Prefer `visible` assertions over DOM checks (tests what user sees)
  - Wait for network idle before asserting dynamic content
  - Use screenshot comparison for visual layout, not pixel-perfect matching
  - Assert accessible names (aria-label) over CSS selectors

  ## Integration Patterns
  - **Frontend verify** (--frontend-verify): Playwright:interaction + DevTools:metrics + Serena:code
  - **E2E suite**: /sc:test --type e2e → Playwright:execute → screenshot evidence → report
  - **Visual QA**: Playwright:screenshot → Claude:vision → /sc:review findings
  - **A11y audit**: Playwright:render → axe-core assertions → /sc:analyze --focus a11y

  <examples>
| Input | Action | Reason |
|-------|--------|--------|
| test login flow | Playwright: navigate → fill → submit → assert redirect | Real browser interaction needed |
| verify responsive navbar | Playwright: resize 3 viewports → screenshot each → compare | Visual validation |
| check form validation | Playwright: submit empty → assert error messages visible | User-facing behavior |
| review auth logic | Native Claude | Static analysis, no browser needed |
  </examples>

  <bounds will="browser automation|E2E testing|visual validation|accessibility testing|screenshot capture" wont="unit testing|API testing|static code analysis|performance profiling" fallback="Use native Claude for code review, Chrome DevTools for performance, native test runner for unit tests"/>

  <handoff next="/sc:test --type e2e /sc:analyze --focus a11y /sc:review"/>
</component>
