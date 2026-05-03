<component name="playwright" type="mcp">
  <role>
    <mission>Browser automation, E2E testing, network mocking, and visual validation via official Microsoft Playwright MCP</mission>
  </role>

  ## Capability System
  Tools are grouped into opt-in capabilities via `--caps=`:
  - **core** (default): navigation, interaction, screenshots, tabs, dialogs
  - **network** (opt-in): request inspection, route mocking, state control
  - **storage** (opt-in): cookies CRUD, localStorage CRUD
  - **pdf** (opt-in): PDF generation
  - **vision** (opt-in): coordinate-based interactions
  - **devtools** (opt-in): developer tools features

  <choose>
  Use:
  - User journey validation: login → navigate → action → verify state
  - Form testing: input, validation, submission, error display
  - Visual regression: screenshots at responsive breakpoints
  - Accessibility: assertions via accessibility snapshots
  - Network mocking: intercept API calls, test error states, offline mode
  - Storage testing: cookie/localStorage manipulation for auth testing

  Avoid:
  - Unit tests: component logic → native test runner (vitest, jest)
  - API testing: backend endpoints → native HTTP tools (curl, fetch)
  - Performance metrics: CWV, profiling → Chrome DevTools (--perf)
  - Static analysis: code quality → native Claude + /sc:review
  </choose>

  ## Key Flags
  - `--caps=network,storage` — enable additional capabilities
  - `--persistent` — persistent browser profile (default: incognito)
  - `-s=<name>` — session management
  - `--snapshot-mode=incremental|full|none` — control snapshot generation
  - `--slim` — token savings mode
  - `--test-id-attribute=<attr>` — custom test ID selector (default: data-testid)
  - `--secrets=<path>` — dotenv-format secrets file
  - `--timeout-action=<ms>` — action timeout (default: 5000)

  ## Network Mocking Patterns
  URL patterns support glob matching:
  - `/api/users` — exact path
  - `/api/*/details` — wildcard
  - `/*.{png,jpg}` — file extensions
  - `/search?q=*` — query params

  ## Integration Patterns
  - **Frontend verify** (--frontend-verify): Playwright:interaction + DevTools:metrics + Serena:code
  - **E2E suite**: /sc:test --type e2e → Playwright:execute → screenshot evidence → report
  - **Visual QA**: Playwright:screenshot → Claude:vision → /sc:review
  - **A11y audit**: Playwright:snapshot → assert accessible names → /sc:analyze --focus a11y
  - **API mock testing**: Playwright:browser_route_set → navigate → verify UI with mocked data

  <examples>
| Input | Action | Reason |
|---|---|---|
| test login flow | navigate → type → click → assert snapshot | Real browser interaction |
| verify responsive navbar | screenshot at 3 viewports → compare | Visual validation |
| test offline behavior | browser_network_state_set(offline) → verify | Network state testing |
| mock API error response | browser_route_set(pattern, status:500) → verify UI | Error state testing |
| test auth cookie handling | browser_cookie_set → navigate → assert | Storage interaction |
  </examples>

  <bounds>
    <should>browser automation, E2E testing, visual validation, accessibility testing, network mocking, and storage management.</should>
    <avoid>unit testing, API testing, static code analysis, and performance profiling.</avoid>
    <fallback>Use Chrome DevTools for performance, native test runner for unit tests.</fallback>
  </bounds>

  <handoff next="/sc:test --type e2e /sc:analyze --focus a11y /sc:review"/>
</component>
