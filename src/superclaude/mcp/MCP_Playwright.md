<component name="playwright" type="mcp">
  <role>
    <mission>Browser auto, E2E test, net mock, visual validate via official Microsoft Playwright MCP</mission>
  </role>

  <capability_system>
  Tools group into opt-in caps via `--caps=`:

  - core: default — nav, interact, screenshots, tabs, dialogs.
  - network: opt-in — request inspect, route mock, state ctrl.
  - storage: opt-in — cookies CRUD, localStorage CRUD.
  - pdf: opt-in — PDF gen.
  - vision: opt-in — coord-based interact.
  - devtools: opt-in — dev tools features.
  </capability_system>

  <choose>
  <use>end-to-end user-journey validate (login → nav → action → verify state), form input/validate/submit/error test, visual regression via screenshots at responsive breakpoints, a11y assert thru a11y snapshots, net-call intercept for error-state + offline-mode test, cookie/localStorage manip for auth scenarios.</use>
  <never>component-level unit test (use native test runner — vitest, jest), backend API endpoint test (use native HTTP tools — curl, fetch), Core Web Vitals or profile work (use Chrome DevTools `--perf`), static code-quality review (use native Claude + `/sc:review`).</never>
  </choose>

  <key_flags>
  - `--caps=network,storage` — enable more caps.
  - `--persistent` — persistent browser profile (default: incognito).
  - `-s=<name>` — session mgmt.
  - `--snapshot-mode=full|none` — ctrl snapshot gen.
  - `--slim` — token save mode.
  - `--test-id-attribute=<attr>` — custom test ID selector (default: `data-testid`).
  - `--secrets=<path>` — dotenv-format secrets file.
  - `--timeout-action=<ms>` — action timeout (default: 5000).
  </key_flags>

  <network_mocking_patterns>
  URL patterns support glob match:

  - `/api/users` — exact path.
  - `/api/*/details` — wildcard.
  - `/*.{png,jpg}` — file ext.
  - `/search?q=*` — query params.
  </network_mocking_patterns>

  <integration_patterns>
  - Frontend-Verify (`--frontend-verify`): Playwright:interaction + DevTools:metrics + Serena:code.
  - E2E-Suite: `/sc:test --type e2e` → Playwright:execute → screenshot evidence → report.
  - Visual-QA: Playwright:screenshot → Claude:vision → `/sc:review`.
  - A11y-Audit: Playwright:snapshot → assert accessible names → `/sc:analyze --focus a11y`.
  - API-Mock-Testing: Playwright:`browser_route` → nav → verify UI w/ mocked data.
  </integration_patterns>

  <examples>
| Input | Action | Reason |
|---|---|---|
| test login flow | nav → type → click → assert snapshot | Real browser interact |
| verify responsive navbar | screenshot at 3 viewports → compare | Visual validate |
| test offline behavior | browser_network_state_set(offline) → verify | Net state test |
| mock API error response | browser_route(pattern, status:500) → verify UI | Error state test |
| test auth cookie handling | browser_cookie_set → nav → assert | Storage interact |
  </examples>

  <bounds>
    <does>browser auto, E2E test, visual validate, a11y test, net mock, storage mgmt.</does>
    <never>unit test, API test, static code analysis, perf profile.</never>
    <fallback>Use Chrome DevTools for perf, native test runner for unit tests.</fallback>
  </bounds>

  <handoff next="/sc:test --type e2e /sc:analyze --focus a11y /sc:review"/>
</component>