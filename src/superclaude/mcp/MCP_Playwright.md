<component name="playwright" type="mcp">
  <role>
    <mission>Browser automation, E2E testing, network mocking, and visual validation via official Microsoft Playwright MCP</mission>
  </role>

  <capability_system>
  Tools are grouped into opt-in capabilities via `--caps=`:

  - core: default — navigation, interaction, screenshots, tabs, dialogs.
  - network: opt-in — request inspection, route mocking, state control.
  - storage: opt-in — cookies CRUD, localStorage CRUD.
  - pdf: opt-in — PDF generation.
  - vision: opt-in — coordinate-based interactions.
  - devtools: opt-in — developer tools features.
  </capability_system>

  <choose>
  <use>end-to-end user-journey validation (login → navigate → action → verify state), form input/validation/submission/error testing, visual regression via screenshots at responsive breakpoints, accessibility assertions through accessibility snapshots, network-call interception for error-state and offline-mode testing, and cookie / localStorage manipulation for auth scenarios.</use>
  <never>component-level unit tests (use native test runner — vitest, jest), backend API endpoint testing (use native HTTP tools — curl, fetch), Core Web Vitals or profiling work (use Chrome DevTools `--perf`), and static code-quality review (use native Claude + `/sc:review`).</never>
  </choose>

  <key_flags>
  - `--caps=network,storage` — enable additional capabilities.
  - `--persistent` — persistent browser profile (default: incognito).
  - `-s=<name>` — session management.
  - `--snapshot-mode=incremental|full|none` — control snapshot generation.
  - `--slim` — token savings mode.
  - `--test-id-attribute=<attr>` — custom test ID selector (default: `data-testid`).
  - `--secrets=<path>` — dotenv-format secrets file.
  - `--timeout-action=<ms>` — action timeout (default: 5000).
  </key_flags>

  <network_mocking_patterns>
  URL patterns support glob matching:

  - `/api/users` — exact path.
  - `/api/*/details` — wildcard.
  - `/*.{png,jpg}` — file extensions.
  - `/search?q=*` — query params.
  </network_mocking_patterns>

  <integration_patterns>
  - Frontend-Verify (`--frontend-verify`): Playwright:interaction + DevTools:metrics + Serena:code.
  - E2E-Suite: `/sc:test --type e2e` → Playwright:execute → screenshot evidence → report.
  - Visual-QA: Playwright:screenshot → Claude:vision → `/sc:review`.
  - A11y-Audit: Playwright:snapshot → assert accessible names → `/sc:analyze --focus a11y`.
  - API-Mock-Testing: Playwright:`browser_route_set` → navigate → verify UI with mocked data.
  </integration_patterns>

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
    <does>browser automation, E2E testing, visual validation, accessibility testing, network mocking, and storage management.</does>
    <never>unit testing, API testing, static code analysis, and performance profiling.</never>
    <fallback>Use Chrome DevTools for performance, native test runner for unit tests.</fallback>
  </bounds>

  <handoff next="/sc:test --type e2e /sc:analyze --focus a11y /sc:review"/>
</component>
