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
| Sequential | Optional | sequential, seq, --effort medium/high, debug, architecture, analysis, reasoning, --seq, --sequential | Native reasoning | MCP_Sequential.md |
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
    <rule>Notify only on first use when MCP not loaded, then auto fallback</rule>
    <format>⚠️ [MCP_NAME] unavailable → using [Fallback]</format>
    <tracking>Uses hook_tracker.py session state</tracking>
  </fallback_behavior>

  <auto_mode note="v2.1.7+ - MCP tool search auto mode">
    <rule>When MCP tool descriptions exceed threshold, defer to MCPSearch tool</rule>
    <default>10% of context window</default>
    <config>`auto:N` syntax where N is percentage (0-100)</config>
    <disable>Add `MCPSearch` to `disallowedTools` in settings</disable>
    <benefit>Reduces context usage for users with many MCP tools</benefit>
  </auto_mode>

  <list_changed note="v2.1.0+ - Dynamic tool updates">
    <rule>MCP servers can emit list_changed notifications</rule>
    <effect>Tools, prompts, resources update without reconnection</effect>
    <use_case>Dynamic tool registration, capability changes</use_case>
  </list_changed>

  <cross_reference note="FLAGS.md and MCP integration">
| FLAGS.md Flag | Triggers MCP | Triggers Mode |
|---------------|--------------|---------------|
| --effort medium | Sequential | - |
| --effort high | Sequential + Context7 | - |
| --think (legacy) | Sequential | - |
| --think-hard (legacy) | Sequential + Context7 | - |
| --ultrathink (legacy) | All loaded MCP | - |
| --brainstorm | - | Brainstorming |
| --uc | - | TokenEfficiency |

Note: When `alwaysThinkingEnabled: true`, legacy --think flags map to --effort levels.
  </cross_reference>

  <native_features note="Built-in Claude Code capabilities, not MCP">
| Feature | Flag | Use Case |
|---------|------|----------|
| Chrome Automation | --chrome | Live browser, auth sessions, GIF recording |
| Web Search | (none) | Fact-check, current info |
  </native_features>
</component>
