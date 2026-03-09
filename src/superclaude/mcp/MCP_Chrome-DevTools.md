<component name="chrome-devtools" type="mcp">
  <role>
    <mission>Performance analysis and Core Web Vitals measurement</mission>
    <flags>--perf, --devtools</flags>
    <note>For live debugging with logged-in browser, use Claude in Chrome (native /chrome)</note>
  </role>

  <choose>
Use:
- Core Web Vitals: CLS, LCP, FID, TTFB metrics
- Performance profiling: CPU, memory, rendering analysis
- Layout debugging: Layout shift detection, render blocking
- Performance audit: Lighthouse-style metrics

Avoid:
- Live browser interaction: Use Claude in Chrome (native /chrome)
- E2E testing: Use Playwright (--play)
- Static analysis: Use native Claude
  </choose>


  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| analyze CLS score | DevTools | Core Web Vitals |
| measure LCP | DevTools | performance metrics |
| profile memory usage | DevTools | performance profiling |
| debug live console errors | Claude in Chrome | live browser state |
| test login flow | Playwright | browser automation |
  </examples>

  <bounds will="performance profiling|Core Web Vitals|layout debugging" wont="live browser interaction|E2E testing|static code analysis" fallback="Use Playwright for E2E, Claude in Chrome for live debugging"/>

  <handoff next="/sc:analyze --focus perf /sc:improve --type performance"/>
</component>
