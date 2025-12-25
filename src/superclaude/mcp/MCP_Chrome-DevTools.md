<component name="chrome-devtools" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>performance|debug|layout|CLS|LCP|console|network|DOM|CSS|devtools</triggers>

  <role>
    <mission>Performance analysis, debugging, and real-time browser inspection</mission>
  </role>

  <choose>
    <use context="deep performance analysis">Understand performance bottlenecks</use>
    <use context="live debugging">Inspect runtime page state, debug live issues</use>
    <use context="network analysis">Inspect requests, CORS errors</use>
    <avoid context="E2E testing">Use Playwright</avoid>
    <avoid context="static analysis">Use native Claude</avoid>
  </choose>

  <synergy>
    <with n="Sequential">Sequential plans perf strategy → DevTools verifies</with>
    <with n="Playwright">Playwright automates flow → DevTools analyzes</with>
  </synergy>

  <examples>
    <ex i="analyze page performance" o="DevTools" r="performance analysis"/>
    <ex i="debug layout shift" o="DevTools" r="live debugging"/>
    <ex i="network requests failing" o="DevTools" r="network analysis"/>
    <ex i="test login flow" o="Playwright" r="browser automation"/>
    <ex i="review function logic" o="Native Claude" r="static analysis"/>
  </examples>
</component>
