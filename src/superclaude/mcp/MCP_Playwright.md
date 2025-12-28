<component name="playwright" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>browser|E2E|test|screenshot|validation|accessibility|WCAG|playwright</triggers>

  <role>
    <mission>Browser automation and E2E testing with real browser interaction</mission>
  </role>

  <choose>
**Use for:**
- Real browser: Actual rendering, not just code
- Integration testing: User journeys, visual validation over unit tests
- E2E: Login flows, form submissions, multi-page workflows
- Visual testing: Screenshots, responsive design validation

**Avoid for:**
- Code analysis: Static review, syntax, logic validation
  </choose>

  <synergy>
- **Sequential**: Sequential plans test strategy → Playwright executes
- **Magic**: Magic creates UI → Playwright validates accessibility
  </synergy>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| test login flow | Playwright | browser automation |
| form validation works | Playwright | real user interaction |
| screenshots responsive design | Playwright | visual testing |
| accessibility compliance | Playwright | automated WCAG |
| review function logic | Native Claude | static analysis |
  </examples>
</component>
