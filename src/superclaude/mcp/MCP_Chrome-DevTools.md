<component name="chrome-devtools" type="mcp">
  <role>
    <mission>Browser debugging, performance analysis, accessibility auditing, and memory profiling via Chrome DevTools Protocol</mission>
    <flags>--perf, --devtools</flags>
  </role>

  ## Plugin Install (manual)
  ```
  claude mcp add chrome-devtools -s user -- npx -y chrome-devtools-mcp@latest
  ```
  Or via MCP Docker: `mcp-find("chrome-devtools")` → `mcp-add("chrome-devtools")`

  <tools note="26 tools across 6 capability domains — v0.21.0">
    **Page & Navigation:**
    - `navigate` — go to URL
    - `go_back` / `go_forward` — browser history
    - `new_page` — open new tab (supports background param)
    - `list_pages` — list open tabs
    - `select_page` — switch tab (supports pageId for multi-agent)
    - `close_page` — close current tab
    - `reload` — reload page (option to ignore cache)
    - `press_key` — keyboard input
    - `screenshot` — capture page (JPEG quality param)

    **Performance:**
    - `performance_start_trace` / `performance_stop_trace` — record performance traces
    - `performance_analyze_insight` — drill into specific insights (insightSetId)
    - `lighthouse_audit` — run Lighthouse audits (performance, a11y, SEO, best practices)

    **Console & Network:**
    - `get_console_messages` — with stack traces (v0.14.0+)
    - `list_network_requests` — paginated, filterable by resource type
    - `get_network_request` — inspect individual request (headers, body via filePath)

    **DOM & Inspection:**
    - `snapshot` — accessibility snapshot of page structure
    - `get_selected_element` — fetch DOM node from DevTools Elements panel
    - `inject_script` — run script on page load (v0.15.0+)

    **Memory:**
    - `take_memory_snapshot` — heap snapshot for leak detection

    **Skills (built-in guides):**
    - Onboarding skill — first-use setup guide
    - Accessibility debugging — WCAG audit workflow
    - LCP optimization — Largest Contentful Paint debugging
    - Memory leak detection — heap snapshot comparison
  </tools>

  <choose>
  Use:
  - Core Web Vitals: CLS, LCP, INP, TTFB measurement via traces
  - Lighthouse audits: performance, accessibility, SEO, best practices scores
  - Memory analysis: heap snapshots, leak detection, GC pressure
  - Accessibility debugging: automated WCAG checks on live pages
  - Network inspection: request timing, bundle size, cache behavior
  - Multi-agent: pageId routing for parallel workflows on different pages

  Avoid:
  - Live browser interaction: use Playwright (--play)
  - E2E test flows: use Playwright for user journey validation
  - Static code analysis: use native Claude for code-level review
  - Backend profiling: use native tools (perf, flamegraph) for server-side
  </choose>

  ## Key Flags
  - `--slim` — maximum token savings (reduces response verbosity)
  - `--auto-connect` — reuse existing Chrome session
  - `--persistent` — persistent browser profile
  - `--read-only` — disable all mutation tools

  ## CWV Thresholds (Google standards)
  | Metric | Good | Needs Work | Poor |
  |--------|------|------------|------|
  | LCP | < 2.5s | 2.5-4.0s | > 4.0s |
  | INP | < 200ms | 200-500ms | > 500ms |
  | CLS | < 0.1 | 0.1-0.25 | > 0.25 |
  | TTFB | < 800ms | 800-1800ms | > 1800ms |

  ## Integration Patterns
  - **Performance audit**: DevTools:trace → lighthouse_audit → Sequential:analyze → /sc:improve
  - **Frontend verify** (--frontend-verify): Playwright:interact + DevTools:profile + Serena:code-review
  - **A11y audit**: DevTools:accessibility-skill → snapshot → /sc:analyze --focus a11y
  - **Memory leak**: DevTools:take_memory_snapshot → compare snapshots → identify retained objects

  <examples>
| Input | Action | Reason |
|-------|--------|--------|
| analyze page performance | DevTools: lighthouse_audit → trace → analyze insights | Comprehensive CWV + Lighthouse |
| debug memory leak in SPA | DevTools: take_memory_snapshot → compare → identify | Heap analysis |
| check accessibility score | DevTools: lighthouse_audit (a11y category) → snapshot | Automated WCAG |
| profile network requests | DevTools: list_network_requests → get_network_request | Request timing/size |
| debug in live Chrome session | DevTools: --auto-connect to existing browser | Reuse dev session |
  </examples>

  <bounds will="performance profiling|Lighthouse audits|Core Web Vitals|memory analysis|accessibility auditing|network inspection|multi-agent pageId routing" wont="live browser interaction|E2E testing|static code analysis|backend profiling" fallback="Use Playwright for E2E, native Claude for code review"/>

  <handoff next="/sc:analyze --focus perf /sc:improve --type performance /sc:troubleshoot"/>
</component>
