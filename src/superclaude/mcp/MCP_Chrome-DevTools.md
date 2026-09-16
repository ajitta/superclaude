<component name="chrome-devtools" type="mcp">
  <role>
    <mission>Browser debug, perf analysis, a11y audit, mem profiling via Chrome DevTools Protocol</mission>
  </role>

  <choose>
  <use>Core Web Vitals measure (CLS, LCP, INP, TTFB) via `performance_start_trace` → `performance_stop_trace` → `performance_analyze_insight`, Lighthouse audits over a11y / SEO / best-practices via `lighthouse_audit` (it excludes performance — traces carry that), heap-snapshot mem analysis with `compare_heapsnapshots` + retainer/retaining-path queries, auto WCAG a11y checks on live pages, network req-timing + bundle-size + cache-behavior inspect, and `pageId`-routed multi-agent flows on diff pages.</use>
  <never>live browser interact or E2E user-journey scripts (use Playwright via `--play`), static code analysis (use native Claude for code review), and server-side backend profile (use native tools — `perf`, flamegraph).</never>
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
  - Frontend-Verify (`--frontend-verify`): Playwright:interact + DevTools:profile + Serena:code-review.
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
    <does>perf profile, Lighthouse audits, Core Web Vitals, mem analysis, a11y audit, network inspect, and multi-agent pageId routing.</does>
    <never>live browser interact, E2E test, static code analysis, and backend profile.</never>
    <fallback>Use Playwright for E2E, native Claude for code review.</fallback>
  </bounds>

  <handoff next="/sc:analyze --focus perf /sc:improve --type performance /sc:troubleshoot"/>
</component>