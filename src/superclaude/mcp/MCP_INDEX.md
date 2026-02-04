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
| Context7 | Optional | context7, c7, library, docs, framework, --c7 | Tavily/WebSearch | MCP_Context7.md |
| Tavily | Optional | tavily, search, research, news, current, --tavily | WebSearch (native) | MCP_Tavily.md |
| Sequential | Optional | sequential, seq, --effort medium/high, debug, --seq | Native reasoning | MCP_Sequential.md |
| Serena | Optional | serena, symbol, rename, LSP, memory, --serena | Native search | MCP_Serena.md |
| Morphllm | Optional | morphllm, morph, pattern, bulk edit, --morph | Edit (native) | MCP_Morphllm.md |
| Magic | Optional | magic, 21st, ui, component, /ui, --magic | Write (native) | MCP_Magic.md |
| Playwright | Optional | playwright, browser, E2E, test, --play | --chrome (native) | MCP_Playwright.md |
| DevTools | Optional | devtools, performance, CLS, LCP, --perf | Playwright | MCP_Chrome-DevTools.md |
| Mindbase | Deprecated | mindbase, memory, conversation, --mindbase | Serena memory | MCP_Mindbase.md |
| Airis-Agent | Deprecated | airis, confidence, repo index, --airis | Native | MCP_Airis-Agent.md |
  </mcp_index>

  <decision_flow>
1. Official docs? → Context7
2. Web search? → Tavily
3. Complex reasoning? → Sequential
4. Symbol ops? → Serena
5. Bulk edits? → Morphllm
6. UI components? → Magic
7. E2E test? → Playwright
8. Live browser? → Claude in Chrome (native /chrome)
9. Performance? → DevTools
10. Memory? → Mindbase
  </decision_flow>

  <fallback_behavior>
Notify only on first use when MCP not loaded → auto fallback
Format: ⚠️ [MCP_NAME] unavailable → using [Fallback]
  </fallback_behavior>

  <auto_mode note="v2.1.7+">
When MCP tool descriptions exceed 10% of context → defer to MCPSearch tool
Disable: Add MCPSearch to disallowedTools
  </auto_mode>

  <cross_reference note="See FLAGS.md for --effort/--think mappings">
| Flag | MCP | Mode |
|------|-----|------|
| --effort medium/high | Sequential (+Context7) | - |
| --brainstorm | - | Brainstorming |
| --uc | - | TokenEfficiency |
  </cross_reference>

  <native_features>
| Feature | Flag | Use Case |
|---------|------|----------|
| Chrome Automation | /chrome | Live browser, auth sessions, GIF |
| Web Search | (none) | Fact-check, current info |
  </native_features>
</component>
