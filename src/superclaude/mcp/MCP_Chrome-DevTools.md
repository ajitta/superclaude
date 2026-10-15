<component name="chrome-devtools" type="mcp">
  <role>
    <mission>Browser debugging, performance analysis, accessibility auditing and memory profiling via the Chrome DevTools Protocol</mission>
  </role>

  <choose>
  <use>Core Web Vitals measurement (CLS, LCP, INP, TTFB) via `performance_start_trace` → `performance_stop_trace` → `performance_analyze_insight`, including the clicks or typing an INP reading needs during the trace; Lighthouse audits over accessibility, SEO and best practices via `lighthouse_audit` (it excludes performance — traces carry that); heap-snapshot memory analysis with `compare_heapsnapshots` and retainer and retaining-path queries; automated WCAG accessibility checks on live pages; inspection of network request timing, bundle size and cache behavior; and `pageId`-routed multi-agent workflows on different pages.</use>
  <never>scripted E2E user journeys or test suites (use Playwright via `--play`, which asserts page state; DevTools drives the page only as far as a measurement needs), static code analysis (use native Claude for code review), and server-side backend profiling (use native tools — `perf`, flamegraph).</never>
  </choose>

  <cwv_thresholds>
  Google Core Web Vitals thresholds:

  | Metric | Good | Needs Work | Poor |
  |---|---|---|---|
  | LCP | < 2.5s | 2.5-4.0s | > 4.0s |
  | INP | < 200ms | 200-500ms | > 500ms |
  | CLS | < 0.1 | 0.1-0.25 | > 0.25 |
  | TTFB | < 800ms | 800-1800ms | > 1800ms |
  </cwv_thresholds>

  <integration_patterns>
  - Performance-Audit: `performance_start_trace` (reload + autoStop) → `performance_stop_trace` → `performance_analyze_insight` per insight → `/sc:improve`.
  - Frontend-Verify (`--frontend-verify`): Playwright:interact + DevTools:profile.
  - A11y-Audit: `lighthouse_audit` → read the accessibility section of the report + `take_snapshot` (a11y tree) → `/sc:analyze --focus a11y`.
  - Memory-Leak: `take_heapsnapshot` before/after → `compare_heapsnapshots` → `get_heapsnapshot_retaining_paths` on the grown classes.
  </integration_patterns>

  <examples>
| Input | Action | Reason |
|---|---|---|
| analyze page performance | DevTools: performance_start_trace → performance_stop_trace → performance_analyze_insight | CWV come from the trace, not Lighthouse |
| debug memory leak in SPA | DevTools: take_heapsnapshot ×2 → compare_heapsnapshots → get_heapsnapshot_retaining_paths | Heap diff + retainers |
| check accessibility score | DevTools: lighthouse_audit → accessibility section → take_snapshot | Automated WCAG; the audit has no category filter |
| profile network requests | DevTools: list_network_requests → get_network_request | Request timing/size |
  </examples>

  <bounds>
    <does>performance profiling, Lighthouse audits, Core Web Vitals, memory analysis, accessibility auditing, network inspection, and multi-agent pageId routing.</does>
    <never>scripted E2E journeys and tests, static code analysis, and backend profiling.</never>
    <fallback>Use Playwright for E2E journeys and tests, native Claude for code review.</fallback>
  </bounds>

  <handoff next="/sc:analyze --focus perf /sc:improve --type performance /sc:troubleshoot"/>
</component>