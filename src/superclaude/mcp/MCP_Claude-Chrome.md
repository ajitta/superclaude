<component name="claude-chrome" type="native">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>/chrome|logged-in|gmail|google docs|notion|live debug|authenticated|multi-site|gif recording</triggers>

  <role>
    <mission>Live browser interaction with user's authenticated browser state</mission>
    <invoke>claude --chrome or /chrome command</invoke>
    <note>Native Claude Code capability via Chrome extension (v1.0.36+)</note>
  </role>

  <capabilities>
- Navigate pages, click, type, fill forms, scroll
- Read console logs and network requests
- Manage tabs, resize windows
- Record GIFs of browser interactions
- Access authenticated web apps (Gmail, Notion, Google Docs)
- Multi-site workflows with user's session
  </capabilities>

  <choose>
Use:
- Authenticated web apps: Gmail, Notion, Google Docs, any logged-in site
- Live debugging: Console/network inspection in real browser
- Multi-site workflows: Coordinate tasks across multiple websites
- GIF recording: Document browser interactions
- Form filling: Data entry in logged-in contexts

Avoid:
- E2E test automation: Use Playwright (--play) for repeatable CI/CD tests
- Performance metrics: Use DevTools (--perf) for CLS, LCP, Core Web Vitals
- Headless/isolated testing: Use Playwright for CI pipelines
- Cross-browser testing: Use Playwright for Chrome/Firefox/Safari
  </choose>

  <synergy>
- Playwright: Repeatable test automation, CI/CD pipelines
- DevTools: Deep performance analysis (CLS, LCP, memory profiling)
- Serena: Code context while debugging live issues
  </synergy>

  <activation>
```bash
# From CLI
claude --chrome

# From session
/chrome
```
  </activation>

  <examples>
| Input | Tool | Reason |
|-------|------|--------|
| debug live console errors | Claude in Chrome | live browser state |
| fill form in Google Docs | Claude in Chrome | authenticated app |
| record demo GIF | Claude in Chrome | GIF recording |
| multi-site workflow | Claude in Chrome | cross-tab coordination |
| test login flow in CI | Playwright | repeatable automation |
| analyze CLS score | DevTools | Core Web Vitals metrics |
  </examples>

  <tools note="Available via mcp__claude-in-chrome__*">
- javascript_tool: Execute JS in page context
- read_page: Get accessibility tree
- find: Natural language element search
- form_input: Set form values
- computer: Mouse/keyboard actions, screenshots
- navigate: URL navigation
- gif_creator: Record browser interactions
- get_page_text: Extract page text
- tabs_context_mcp: Get tab info
- read_console_messages: Read console output
- read_network_requests: Monitor network
  </tools>
</component>
