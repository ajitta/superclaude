<component name="chrome-devtools" type="mcp">
  <role>
    <mission>Browser debugging, performance analysis, accessibility auditing, and memory profiling via Chrome DevTools Protocol</mission>
  </role>

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

  <key_flags>
  - `--slim` — maximum token savings (reduces response verbosity).
  - `--auto-connect` — reuse existing Chrome session.
  - `--persistent` — persistent browser profile.
  - `--read-only` — disable all mutation tools.
  </key_flags>

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
  - Performance-Audit: DevTools:trace → `lighthouse_audit` → Sequential:analyze → `/sc:improve`.
  - Frontend-Verify (`--frontend-verify`): Playwright:interact + DevTools:profile + Serena:code-review.
  - A11y-Audit: DevTools:accessibility-skill → snapshot → `/sc:analyze --focus a11y`.
  - Memory-Leak: DevTools:`take_memory_snapshot` → compare snapshots → identify retained objects.
  </integration_patterns>

  <examples>
| Input | Action | Reason |
|---|---|---|
| analyze page performance | DevTools: lighthouse_audit → trace → analyze insights | Comprehensive CWV + Lighthouse |
| debug memory leak in SPA | DevTools: take_memory_snapshot → compare → identify | Heap analysis |
| check accessibility score | DevTools: lighthouse_audit (a11y category) → snapshot | Automated WCAG |
| profile network requests | DevTools: list_network_requests → get_network_request | Request timing/size |
| debug in live Chrome session | DevTools: --auto-connect to existing browser | Reuse dev session |
  </examples>

  <bounds>
    <does>performance profiling, Lighthouse audits, Core Web Vitals, memory analysis, accessibility auditing, network inspection, and multi-agent pageId routing.</does>
    <never>live browser interaction, E2E testing, static code analysis, and backend profiling.</never>
    <fallback>Use Playwright for E2E, native Claude for code review.</fallback>
  </bounds>

  <handoff next="/sc:analyze --focus perf /sc:improve --type performance /sc:troubleshoot"/>
</component>
