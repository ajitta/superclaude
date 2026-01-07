<component name="mcp-index" type="routing">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>mcp|tool|--tavily|--c7|--context7|--seq|--sequential|--serena|--magic|--morph|--morphllm|--play|--playwright|--perf|--devtools|--mindbase|--airis</triggers>

  <role>
    <mission>MCP routing index - triggers to detailed file mapping</mission>
    <note>Detailed usage loaded dynamically via context_loader.py hook</note>
  </role>

  <mcp_index>
| MCP | Triggers | File |
|-----|----------|------|
| Context7 | context7, c7, library, docs, framework, documentation, import, require, library docs, framework docs, --c7, --context7 | MCP_Context7.md |
| Tavily | tavily, search, research, news, current, web, fact-check, /sc:research, web search, news search, --tavily | MCP_Tavily.md |
| Sequential | sequential, seq, think, think-hard, ultrathink, debug, architecture, analysis, reasoning, multi-step, reasoning chain, --seq, --sequential | MCP_Sequential.md |
| Serena | serena, symbol, rename, rename across, extract, move, LSP, session, memory, /sc:load, /sc:save, --serena | MCP_Serena.md |
| Morphllm | morphllm, morph, pattern, pattern replace, bulk, bulk edit, edit, transform, style, framework, text-replacement, --morph, --morphllm | MCP_Morphllm.md |
| Magic | magic, 21st, ui, component, button, form, modal, card, table, nav, /ui, /21, responsive, accessible, ui component, --magic | MCP_Magic.md |
| Playwright | playwright, browser, browser test, E2E, test, screenshot, validation, accessibility, WCAG, --play, --playwright | MCP_Playwright.md |
| DevTools | devtools, performance, performance audit, layout, layout debug, CLS, LCP, metrics, core web vitals, --perf, --devtools | MCP_Chrome-DevTools.md |
| Mindbase | mindbase, memory, conversation, conversation memory, session, semantic, embedding, pgvector, --mindbase | MCP_Mindbase.md |
| Airis-Agent | airis, confidence, confidence check, research, index, repo index, optimize, sync, --airis | MCP_Airis-Agent.md |
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

  <fallbacks>
| Primary | Fallback |
|---------|----------|
| Tavily | WebSearch (native) |
| Context7 | Tavily |
| Sequential | Native |
| Playwright | Chrome (native --chrome) |
| Serena | Native search |
| Morphllm | Native edit |
| Magic | Native coding |
| DevTools | Playwright |
| Mindbase | Serena |
| Airis-Agent | Native |
  </fallbacks>

  <native_features note="Built-in Claude Code capabilities, not MCP">
| Feature | Flag | Use Case |
|---------|------|----------|
| Chrome Automation | --chrome | Live browser, auth sessions, GIF recording |
| Web Search | (none) | Fact-check, current info |
  </native_features>
</component>
