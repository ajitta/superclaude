<component name="chrome-devtools" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>performance|debug|layout|CLS|LCP|console|network|DOM|CSS|devtools</triggers>

  <role>
    <mission>Performance analysis, debugging, and real-time browser inspection</mission>
  </role>

  <choose>
Use for:
- Deep performance analysis: Understand performance bottlenecks
- Live debugging: Inspect runtime page state, debug live issues
- Network analysis: Inspect requests, CORS errors

Avoid for:
- E2E testing: Use Playwright
- Static analysis: Use native Claude
  </choose>

  <synergy>
- Sequential: Sequential plans perf strategy → DevTools verifies
- Playwright: Playwright automates flow → DevTools analyzes
  </synergy>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| analyze page performance | DevTools | performance analysis |
| debug layout shift | DevTools | live debugging |
| network requests failing | DevTools | network analysis |
| test login flow | Playwright | browser automation |
| review function logic | Native Claude | static analysis |
  </examples>
</component>
