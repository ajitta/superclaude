<component name="playwright" type="mcp">
  <role>
    <mission>Browser auto, E2E test, net mock, visual validate via Microsoft's Playwright — the `playwright-cli` skill or the Playwright MCP</mission>
  </role>

  <cli_vs_mcp>
  Decision: `playwright-cli` skill installed → CLI (runs as `Bash(playwright-cli …)`; no tool schemas or a11y trees held in context, one command per action, per-project sessions via `-s=<name>`). Skill absent and the `playwright` MCP server connected → MCP (`browser_*` tools below). Both present and the task keeps one browser alive across many turns — exploratory automation, self-healing tests — → MCP. Server disabled for the current project via `/mcp` → the `browser_*` names do not exist; use the CLI. CLI commands map one-to-one onto the MCP tools; `playwright-cli --help` is the list.
  </cli_vs_mcp>

  <capability_system>
  MCP-side tools group into opt-in caps via `--caps=`:

  - core: default — nav, interact, snapshots, screenshots, tabs, dialogs, console, network request inspect, WebMCP tool calls.
  - network: opt-in — `browser_route` mock + `browser_unroute`, route list, offline/online state.
  - storage: opt-in — cookies, localStorage, sessionStorage CRUD, storage-state import/export.
  - testing: opt-in — `browser_verify_*` assertions (element/text/list visible, value) + `browser_generate_locator`.
  - devtools: opt-in — tracing, video + action recording, highlight/annotate.
  - pdf: opt-in — PDF gen.
  - vision: opt-in — coord-based interact.
  - config: opt-in — `browser_get_config` to read the running server config.
  </capability_system>

  <choose>
  <use>end-to-end user-journey validate (login → nav → action → verify state), form input/validate/submit/error test, visual regression via screenshots at responsive breakpoints, a11y assert through a11y snapshots, net-call intercept for error-state + offline-mode test, cookie/localStorage manip for auth scenarios.</use>
  <never>component-level unit test (use native test runner — vitest, jest), backend API endpoint test (use native HTTP tools — curl, fetch), Core Web Vitals or profile work (use Chrome DevTools `--perf`), static code-quality review (use native Claude + `/sc:review`).</never>
  </choose>

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
  - API-Mock-Testing: Playwright:`browser_route` → nav → verify UI with mocked data.
  </integration_patterns>

  <examples>
| Input | Action | Reason |
|---|---|---|
| test login flow | nav → type → click → assert snapshot | Real browser interact |
| verify responsive navbar | screenshot at 3 viewports → compare | Visual validate |
| test offline behavior | browser_network_state_set(offline) → verify | Net state test |
| mock API error response | browser_route(pattern, status:500) → verify UI | Error state test |
| test auth cookie handling | browser_cookie_set → nav → assert | Storage interact |
| assert checkout total shown | browser_verify_text_visible (--caps=testing) | Assertion without a screenshot round-trip |
  </examples>

  <bounds>
    <does>browser auto, E2E test, visual validate, a11y test, net mock, storage mgmt.</does>
    <never>unit test, API test, static code analysis, perf profile.</never>
    <fallback>MCP unavailable → `playwright-cli` skill if installed, else Chrome DevTools MCP for browser work, native WebFetch for page content; native test runner for unit tests.</fallback>
  </bounds>

  <handoff next="/sc:test --type e2e /sc:analyze --focus a11y /sc:review"/>
</component>