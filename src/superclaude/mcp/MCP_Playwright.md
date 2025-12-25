<component name="playwright" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>browser|E2E|test|screenshot|validation|accessibility|WCAG|playwright</triggers>

  <role>
    <mission>Browser automation and E2E testing with real browser interaction</mission>
  </role>

  <choose>
    <use context="real browser">Actual rendering, not just code</use>
    <use context="integration testing">User journeys, visual validation over unit tests</use>
    <use context="E2E">Login flows, form submissions, multi-page workflows</use>
    <use context="visual testing">Screenshots, responsive design validation</use>
    <avoid context="code analysis">Static review, syntax, logic validation</avoid>
  </choose>

  <synergy>
    <with n="Sequential">Sequential plans test strategy → Playwright executes</with>
    <with n="Magic">Magic creates UI → Playwright validates accessibility</with>
  </synergy>

  <examples>
    <ex i="test login flow" o="Playwright" r="browser automation"/>
    <ex i="form validation works" o="Playwright" r="real user interaction"/>
    <ex i="screenshots responsive design" o="Playwright" r="visual testing"/>
    <ex i="accessibility compliance" o="Playwright" r="automated WCAG"/>
    <ex i="review function logic" o="Native Claude" r="static analysis"/>
  </examples>
</component>
