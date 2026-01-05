<component name="mcp-index" type="routing">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>mcp|tool|--tavily|--c7|--context7|--seq|--sequential|--serena|--magic|--morph|--morphllm|--play|--playwright|--chrome|--devtools|--mindbase|--airis</triggers>

  <role>
    <mission>MCP routing index - triggers to detailed file mapping</mission>
    <note>Detailed usage loaded dynamically via context_loader.py hook</note>
  </role>

  <mcp_index>
| MCP | Triggers | File |
|-----|----------|------|
| Context7 | library, docs, framework, documentation, import, require, --c7, --context7 | MCP_Context7.md |
| Tavily | search, research, news, current, web, fact-check, /sc:research, --tavily | MCP_Tavily.md |
| Sequential | think, think-hard, ultrathink, debug, architecture, analysis, reasoning, --seq, --sequential | MCP_Sequential.md |
| Serena | symbol, rename, extract, move, LSP, session, memory, /sc:load, /sc:save, --serena | MCP_Serena.md |
| Morphllm | pattern, bulk, edit, transform, style, framework, text-replacement, --morph, --morphllm | MCP_Morphllm.md |
| Magic | UI, component, button, form, modal, card, table, nav, /ui, /21, responsive, accessible, --magic | MCP_Magic.md |
| Playwright | browser, E2E, test, screenshot, validation, accessibility, WCAG, --play, --playwright | MCP_Playwright.md |
| DevTools | performance, debug, layout, CLS, LCP, console, network, DOM, CSS, --chrome, --devtools | MCP_Chrome-DevTools.md |
| Mindbase | memory, conversation, session, semantic, embedding, pgvector, --mindbase | MCP_Mindbase.md |
| Airis-Agent | confidence, research, index, optimize, sync, --airis | MCP_Airis-Agent.md |
  </mcp_index>

  <decision_flow>
1. Official docs? → Context7
2. Web search? → Tavily
3. Complex reasoning? → Sequential
4. Symbol ops? → Serena
5. Bulk edits? → Morphllm
6. UI components? → Magic
7. Browser test? → Playwright
8. Perf debug? → DevTools
9. Memory/session? → Mindbase
10. Confidence/index? → Airis-Agent
  </decision_flow>

  <fallbacks>
| Primary | Fallback |
|---------|----------|
| Tavily | WebSearch |
| Context7 | Tavily |
| Sequential | Native |
| Playwright | Tavily |
| Serena | Native search |
| Morphllm | Native edit |
| Magic | Native coding |
| DevTools | Playwright |
| Mindbase | Serena |
| Airis-Agent | Native |
  </fallbacks>
</component>
