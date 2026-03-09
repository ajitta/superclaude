<component name="playwright" type="mcp">
  <role>
    <mission>Browser automation and E2E testing with real browser interaction</mission>
  </role>

  <choose>
Use:
- Real browser: Actual rendering, not just code
- Integration testing: User journeys, visual validation over unit tests
- E2E: Login flows, form submissions, multi-page workflows
- Visual testing: Screenshots, responsive design validation

Avoid:
- Code analysis: Static review, syntax, logic validation
  </choose>


  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| test login flow | Playwright | browser automation |
| form validation works | Playwright | real user interaction |
| screenshots responsive design | Playwright | visual testing |
| accessibility compliance | Playwright | automated WCAG |
| review function logic | Native Claude | static analysis |
  </examples>

  <bounds will="browser automation|E2E testing|visual validation|accessibility testing" wont="static code analysis|unit testing|backend logic" fallback="Use native Claude for code review, DevTools for performance profiling"/>

  <handoff next="/sc:test --type e2e /sc:analyze"/>
</component>
