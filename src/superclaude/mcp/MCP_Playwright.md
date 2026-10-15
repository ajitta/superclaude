<component name="playwright" type="mcp">
  <role>
    <mission>Browser automation, E2E testing, network mocking and visual validation via Microsoft's Playwright — the `playwright-cli` skill or the Playwright MCP</mission>
  </role>

  <cli_vs_mcp>
  Decision: `playwright-cli` skill installed → CLI (runs as `Bash(playwright-cli …)`; no tool schemas or a11y trees held in context, one command per action, per-project sessions via `-s=<name>`). Skill absent and the `playwright` MCP server connected → MCP (`browser_*` tools below). Both present and the task keeps one browser alive across many turns — exploratory automation, self-healing tests — → MCP. Server disabled for the current project via `/mcp` → the `browser_*` names do not exist; use the CLI. CLI commands map one-to-one onto the MCP tools; `playwright-cli --help` is the list.
  </cli_vs_mcp>

  <capability_system>
  MCP-side tools are grouped into capabilities, enabled with `--caps=`; every group except core is opt-in:

  - core: default — navigation, interaction, snapshots, screenshots, tabs, dialogs, console, network request inspection, WebMCP tool calls.
  - network: opt-in — `browser_route` mocking and `browser_unroute`, the route list, offline/online state (`browser_network_state_set`).
  - storage: opt-in — create, read, update and delete for cookies (`browser_cookie_set` and others), localStorage and sessionStorage; storage-state import and export.
  - testing: opt-in — `browser_verify_*` assertions (element/text/list visible, value) + `browser_generate_locator`.
  - devtools: opt-in — tracing, video and action recording, highlighting and annotation.
  - pdf: opt-in — PDF generation.
  - vision: opt-in — coordinate-based interaction.
  - config: opt-in — `browser_get_config` to read the running server config.
  </capability_system>

  <choose>
  <use>end-to-end user-journey validation (login → navigate → action → verify state), testing form input, validation, submission and errors, visual regression via screenshots at responsive breakpoints, accessibility assertions through accessibility snapshots, network-call interception for error-state and offline-mode tests (network capability), and cookie or localStorage manipulation for auth scenarios (storage capability).</use>
  <never>component-level unit tests (use the native test runner — vitest, jest), backend API endpoint tests (use native HTTP tools — curl, fetch), Core Web Vitals or profiling work (use Chrome DevTools `--perf`), and static code-quality review (use native Claude and `/sc:review`).</never>
  </choose>

  <network_mocking_patterns>
  URL patterns support glob matching:

  - `/api/users` — exact path.
  - `/api/*/details` — wildcard.
  - `/*.{png,jpg}` — file extensions.
  - `/search?q=*` — query parameters.
  </network_mocking_patterns>

  <integration_patterns>
  - Frontend-Verify (`--frontend-verify`): Playwright:interaction + DevTools:metrics.
  - E2E-Suite: `/sc:test --type e2e` → Playwright:execute → screenshot evidence → report.
  - Visual-QA: Playwright:screenshot → Claude:vision → `/sc:review`.
  - A11y-Audit: Playwright:snapshot → assert accessible names → `/sc:analyze --focus a11y`.
  - API-Mock-Testing: Playwright:`browser_route` (`--caps=network`) → navigate → verify the UI with mocked data.
  </integration_patterns>

  <examples>
| Input | Action | Reason |
|---|---|---|
| test login flow | navigate → type → click → assert snapshot | Real browser interaction |
| verify responsive navbar | screenshot at 3 viewports → compare | Visual validation |
| test offline behavior | browser_network_state_set(offline) (--caps=network) → verify | Network state test |
| mock API error response | browser_route(pattern, status:500) (--caps=network) → verify UI | Error state test |
| test auth cookie handling | browser_cookie_set (--caps=storage) → navigate → assert | Storage interaction |
| assert checkout total shown | browser_verify_text_visible (--caps=testing) | Assertion without a screenshot round-trip |
  </examples>

  <bounds>
    <does>browser automation, E2E testing, visual validation, accessibility testing, network mocking, and storage management.</does>
    <never>unit testing, API testing, static code analysis, and performance profiling.</never>
    <fallback>When the MCP is unavailable, use the `playwright-cli` skill if installed; otherwise the Chrome DevTools MCP can inspect a page and perform single interactions (not scripted journeys; it has no E2E assertions), and native WebFetch reads page content. Use the native test runner for unit tests.</fallback>
  </bounds>

  <handoff next="/sc:test --type e2e /sc:analyze --focus a11y /sc:review"/>
</component>