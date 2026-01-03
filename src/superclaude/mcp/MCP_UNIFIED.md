---
name: mcp-index
type: mcp
cache: pinned
triggers: [mcp, tool, --tavily, --c7, --seq, --serena, --magic, --morph, --play, --chrome]
---
<component name="mcp-index" type="routing">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>mcp|tool|--tavily|--c7|--seq|--serena|--magic|--morph|--play|--chrome|--devtools</triggers>

  <role>
    <mission>MCP routing index - triggers to detailed file mapping</mission>
    <note>Detailed usage loaded dynamically via context_loader.py hook</note>
  </role>

  <mcp_index>
| MCP | Triggers | File |
|-----|----------|------|
| Context7 | docs, framework, import, --c7 | MCP_Context7.md |
| Tavily | search, news, research, --tavily | MCP_Tavily.md |
| Sequential | think, debug, architecture, --seq | MCP_Sequential.md |
| Serena | symbol, rename, memory, --serena | MCP_Serena.md |
| Morphllm | pattern, bulk, transform, --morph | MCP_Morphllm.md |
| Magic | UI, component, form, --magic | MCP_Magic.md |
| Playwright | browser, E2E, test, --play | MCP_Playwright.md |
| DevTools | performance, layout, CLS, --chrome | MCP_Chrome-DevTools.md |
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
  </decision_flow>

  <fallbacks>
| Primary | Fallback |
|---------|----------|
| Tavily | WebSearch |
| Context7 | Tavily |
| Sequential | Native |
| Playwright | Tavily |
  </fallbacks>
</component>
