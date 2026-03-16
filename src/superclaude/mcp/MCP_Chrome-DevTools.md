<component name="chrome-devtools" type="mcp">
  <role>
    <mission>Performance analysis and Core Web Vitals measurement</mission>
    <flags>--perf, --devtools</flags>
  </role>

  ## Activation
  Not always active. When performance profiling is needed:
  1. `mcp-find("chrome-devtools")` — locate in MCP Docker catalog
  2. `mcp-add("chrome-devtools")` — activate for current session
  3. Ensure target app is running and accessible

  <choose>
  Use:
  - Core Web Vitals: CLS, LCP, FID/INP, TTFB measurement
  - CPU profiling: flame charts, long tasks, main thread blocking
  - Memory analysis: heap snapshots, leak detection, GC pressure
  - Rendering: layout shifts, paint timing, compositing layers
  - Network waterfall: request timing, bundle size, cache behavior

  Avoid:
  - Live browser interaction: Use Claude in Chrome (native /chrome)
  - E2E testing: Use Playwright (--play) for user journey validation
  - Static analysis: Use native Claude for code-level performance review
  - Backend profiling: Use native tools (perf, flamegraph) for server-side
  </choose>

  ## CWV Measurement Workflow
  1. Profile page load → capture LCP, FID/INP, CLS baseline
  2. Identify worst metric → drill into contributing factors
  3. For LCP: check resource loading, render-blocking, server response
  4. For CLS: identify layout shift sources, missing dimensions, dynamic injection
  5. For INP: find long tasks, main thread blocking, event handler latency
  6. Re-profile after changes → compare before/after

  ## Metric Thresholds (Google standards)
  | Metric | Good | Needs Work | Poor |
  |--------|------|------------|------|
  | LCP | < 2.5s | 2.5-4.0s | > 4.0s |
  | INP | < 200ms | 200-500ms | > 500ms |
  | CLS | < 0.1 | 0.1-0.25 | > 0.25 |
  | TTFB | < 800ms | 800-1800ms | > 1800ms |

  ## Profiling Strategy
  - **Baseline first**: always measure before optimizing
  - **One variable**: change one thing, re-measure, compare
  - **Real conditions**: throttle CPU/network to simulate user devices
  - **Multiple runs**: take 3+ measurements to account for variance

  ## Integration Patterns
  - **Performance audit**: DevTools:measure → Sequential:analyze bottlenecks → /sc:improve --type performance
  - **Frontend verify** (--frontend-verify): Playwright:interact + DevTools:profile + Serena:code-review
  - **Optimization loop**: DevTools:baseline → /sc:implement fix → DevTools:re-measure → compare

  <examples>
| Input | Action | Reason |
|-------|--------|--------|
| analyze CLS score | DevTools: profile page → identify shift sources → measure | Core Web Vitals |
| why is page load slow | DevTools: LCP breakdown → network waterfall → render timeline | Performance diagnosis |
| memory leak in SPA | DevTools: heap snapshots → compare → identify retained objects | Memory profiling |
| debug live console errors | Claude in Chrome (not DevTools MCP) | Needs live browser session |
  </examples>

  <bounds will="performance profiling|Core Web Vitals|memory analysis|rendering diagnostics|network analysis" wont="live browser interaction|E2E testing|static code analysis|backend profiling" fallback="Use Playwright for E2E, Claude in Chrome for live debugging, native tools for server-side profiling"/>

  <handoff next="/sc:analyze --focus perf /sc:improve --type performance /sc:troubleshoot"/>
</component>
