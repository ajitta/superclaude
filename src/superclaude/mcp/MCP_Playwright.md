<component name="playwright" type="mcp">
  <role>
    <mission>Browser automation, E2E testing, network mocking, and visual validation via official Microsoft Playwright MCP</mission>
  </role>

  ## Plugin Install (manual)
  ```
  claude mcp add playwright -s user -- npx -y @playwright/mcp@latest
  ```
  Or via MCP Docker: `mcp-find("playwright")` → `mcp-add("playwright")`

  ## Capability System
  Tools are grouped into opt-in capabilities via `--caps=`:
  - **core** (default): navigation, interaction, screenshots, tabs, dialogs
  - **network** (opt-in): request inspection, route mocking, state control
  - **storage** (opt-in): cookies CRUD, localStorage CRUD
  - **pdf** (opt-in): PDF generation
  - **vision** (opt-in): coordinate-based interactions
  - **devtools** (opt-in): developer tools features

  <tools note="30+ tools — capability-grouped">
    **Core (default):**
    - `browser_navigate` / `browser_go_back` / `browser_go_forward` — navigation
    - `browser_wait` — wait for condition
    - `browser_press_key` — keyboard input
    - `browser_take_screenshot` — capture page
    - `browser_save_as_pdf` — PDF export (requires --caps=pdf)
    - `browser_snapshot` — accessibility snapshot (primary assertion tool)
    - `browser_click` / `browser_drag` / `browser_hover` — mouse interaction
    - `browser_type` — text input
    - `browser_select_option` — dropdown selection
    - `browser_handle_dialog` — alert/confirm/prompt handling
    - `browser_file_upload` — file input
    - `browser_tab_new` / `browser_tab_list` / `browser_tab_select` / `browser_tab_close` — tab management
    - `browser_console_messages` — read console output

    **Network (--caps=network):**
    - `browser_network_requests` — list captured requests (headers, body)
    - `browser_network_state_set` — toggle online/offline
    - `browser_route_set` — mock responses by URL pattern (glob matching)
    - `browser_route_list` — list active routes
    - `browser_unroute` — remove routes

    **Storage (--caps=storage):**
    - `browser_cookie_get` / `browser_cookie_get_all` / `browser_cookie_set` / `browser_cookie_delete` / `browser_cookie_clear`
    - `browser_localstorage_get` / `browser_localstorage_set` / `browser_localstorage_remove` / `browser_localstorage_clear`
  </tools>

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
|-------|--------|--------|
| test login flow | navigate → type → click → assert snapshot | Real browser interaction |
| verify responsive navbar | screenshot at 3 viewports → compare | Visual validation |
| test offline behavior | browser_network_state_set(offline) → verify | Network state testing |
| mock API error response | browser_route_set(pattern, status:500) → verify UI | Error state testing |
| test auth cookie handling | browser_cookie_set → navigate → assert | Storage interaction |
  </examples>

  <bounds will="browser automation|E2E testing|visual validation|accessibility testing|network mocking|storage management" wont="unit testing|API testing|static code analysis|performance profiling" fallback="Use Chrome DevTools for performance, native test runner for unit tests"/>

  <handoff next="/sc:test --type e2e /sc:analyze --focus a11y /sc:review"/>
</component>
