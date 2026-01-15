<component name="mcp-index" type="routing">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>mcp|tool|--tavily|--c7|--context7|--seq|--sequential|--serena|--magic|--morph|--morphllm|--play|--playwright|--perf|--devtools|--mindbase|--airis</triggers>

  <role>
    <mission>MCP routing index - triggers to detailed file mapping</mission>
    <note>Detailed usage loaded dynamically via context_loader.py hook</note>
  </role>

  <mcp_index note="All MCPs optional - load via claude_desktop_config.json">
| MCP | Status | Triggers | Fallback | File |
|-----|--------|----------|----------|------|
| Context7 | Optional | context7, c7, library, docs, framework, documentation, --c7, --context7 | Tavily/WebSearch | MCP_Context7.md |
| Tavily | Optional | tavily, search, research, news, current, web, fact-check, --tavily | WebSearch (native) | MCP_Tavily.md |
| Sequential | Optional | sequential, seq, debug, architecture, analysis, reasoning, --seq, --sequential | Native reasoning | MCP_Sequential.md |
| Serena | Optional | serena, symbol, rename, extract, move, LSP, memory, --serena | Native search | MCP_Serena.md |
| Morphllm | Optional | morphllm, morph, pattern, bulk edit, transform, --morph, --morphllm | Edit (native) | MCP_Morphllm.md |
| Magic | Optional | magic, 21st, ui, component, /ui, /21, --magic | Write (native) | MCP_Magic.md |
| Playwright | Optional | playwright, browser, E2E, test, screenshot, WCAG, --play, --playwright | --chrome (native) | MCP_Playwright.md |
| DevTools | Optional | devtools, performance, CLS, LCP, metrics, --perf, --devtools | Playwright | MCP_Chrome-DevTools.md |
| Mindbase | Experimental | mindbase, memory, conversation, semantic, --mindbase | Serena memory | MCP_Mindbase.md |
| Airis-Agent | Experimental | airis, confidence, repo index, --airis | Native | MCP_Airis-Agent.md |
  </mcp_index>

  <decision_flow>
1. Official docs? → Context7
2. Web search? → Tavily
3. Complex reasoning? → Sequential
4. Symbol ops? → Serena
5. Bulk edits? → Morphllm
6. UI components? → Magic
7. E2E test? → Playwright
8. Live browser (authenticated)? → Claude in Chrome (native /chrome)
9. Performance metrics? → DevTools
10. Memory/session? → Mindbase
11. Confidence/index? → Airis-Agent
  </decision_flow>

  <fallback_behavior note="First notification only per session">
    <rule>MCP 미로드 시 첫 사용에만 알림, 이후 자동 fallback</rule>
    <format>⚠️ [MCP명] unavailable → using [Fallback]</format>
    <tracking>hook_tracker.py session state 활용</tracking>
  </fallback_behavior>

  <cross_reference note="FLAGS.md와 MCP 연동">
| FLAGS.md Flag | Triggers MCP | Triggers Mode |
|---------------|--------------|---------------|
| --think | Sequential | - |
| --think-hard | Sequential + Context7 | - |
| --ultrathink | All loaded MCP | - |
| --brainstorm | - | Brainstorming |
| --uc | - | TokenEfficiency |
  </cross_reference>

  <native_features note="Built-in Claude Code capabilities, not MCP">
| Feature | Flag | Use Case |
|---------|------|----------|
| Chrome Automation | --chrome | Live browser, auth sessions, GIF recording |
| Web Search | (none) | Fact-check, current info |
  </native_features>
</component>
