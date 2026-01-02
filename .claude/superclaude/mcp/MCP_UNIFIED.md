---
name: mcp-unified
type: mcp
cache: pinned
triggers: [mcp, tool, --tavily, --c7, --seq, --serena, --magic, --morph, --play, --chrome]
---
<component name="mcp-reference" type="unified">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>mcp|tool|--tavily|--c7|--seq|--serena|--magic|--morph|--play|--chrome|--devtools|--airis|--mindbase</triggers>

  <role>
    <mission>Unified MCP tool selection and routing guide</mission>
  </role>

  <quick_reference>
| MCP | Triggers | Use For | Avoid |
|-----|----------|---------|-------|
| Context7 | imports, docs, framework, --c7 | Official library docs, framework patterns | Simple explanations |
| Tavily | search, news, research, --tavily | Web search, current events, fact-check | Code gen, training knowledge |
| Sequential | think, debug, architecture, --seq | Complex multi-step analysis, reasoning | Simple tasks |
| Serena | symbol, rename, memory, --serena | Semantic ops, session persistence, LSP | Simple text edits |
| Morphllm | pattern, bulk, transform, --morph | Bulk edits, style enforcement | Symbol operations |
| Magic | UI, component, form, --magic | Modern UI components (21st.dev) | Backend logic |
| Playwright | browser, E2E, test, --play | Browser automation, visual testing | Static analysis |
| DevTools | performance, layout, CLS, --chrome | Live debugging, perf analysis | E2E testing |
| Airis | confidence, index, optimize | Pre-implementation validation | Simple queries |
| Mindbase | memory, conversation, embedding | Semantic memory, session persistence | Temporary data |
  </quick_reference>

  <decision_flow>
1. Official docs needed? → Context7 (curated, version-specific)
2. Web search needed? → Tavily (current events, multi-source)
3. Complex reasoning? → Sequential (3+ interconnected components)
4. Symbol operations? → Serena (rename, refs, LSP)
5. Bulk pattern edits? → Morphllm (<10 files, patterns)
6. UI components? → Magic (accessible, modern)
7. Browser testing? → Playwright (E2E, visual)
8. Performance debug? → DevTools (live inspection)
  </decision_flow>

  <synergies>
- Context7 + Sequential: Docs → Strategy analysis
- Tavily + Sequential: Search → Synthesis
- Serena + Morphllm: Semantic analysis → Bulk edits
- Magic + Playwright: UI creation → Accessibility validation
- Playwright + DevTools: Automation → Performance analysis
  </synergies>

  <config_requirements>
| MCP | Requirement |
|-----|-------------|
| Tavily | TAVILY_API_KEY from app.tavily.com |
| Context7 | (built-in) |
| Sequential | (built-in) |
| Serena | Project activation required |
| Airis/Mindbase | airis-mcp-gateway (Docker) |
  </config_requirements>

  <fallbacks>
| Primary | Fallback |
|---------|----------|
| Tavily | Native WebSearch |
| Context7 | Tavily search |
| Sequential | Native reasoning |
| Playwright | Tavily extraction |
| Serena | Manual search |
  </fallbacks>
</component>
