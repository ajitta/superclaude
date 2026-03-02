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

  <workflows>
    <core_web_vitals_audit>
1. Navigate to target page via Playwright (--play)
2. Measure LCP: largest contentful paint element and timing
3. Measure CLS: layout shift sources (images, ads, dynamic content)
4. Measure FID/INP: interaction responsiveness
5. Measure TTFB: server response time
6. Prioritize fixes by impact; re-measure to confirm
    </core_web_vitals_audit>
    <memory_leak_detection>
1. Heap snapshot after page load → perform suspected leak action
2. Force GC → second heap snapshot → compare
3. Trace retainers: detached DOM nodes, uncleaned listeners
    </memory_leak_detection>
  </workflows>

  <scenarios>
    <network_waterfall>
Scenario: diagnose slow page load
1. Capture network waterfall during full page load
2. Identify render-blocking CSS/JS and oversized assets (>200KB)
3. Check Cache-Control headers; detect sequential chains
4. Recommend: preload hints, code splitting, image optimization
    </network_waterfall>
  </scenarios>

  <tool_guide>
- Pair with --play: Playwright navigates, DevTools measures
- CLS: look for elements without explicit width/height
- LCP: focus on hero images, font loading, server response
- Memory: always force GC before snapshots for accuracy
- Combine with --seq for systematic performance root cause analysis
  </tool_guide>
</component>
