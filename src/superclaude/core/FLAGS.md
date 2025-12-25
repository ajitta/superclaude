<component name="flags" type="core" priority="high">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>flag|--|mode|mcp|think|effort|delegate</triggers>

  <role>
    <mission>Behavioral flags for Claude Code execution modes and tool selection</mission>
  </role>

  <modes>
    <f n="--brainstorm" trigger="vague requests, 'maybe', 'thinking about'">Collaborative discovery, probing questions</f>
    <f n="--introspect" trigger="self-analysis, error recovery, meta-cognition">Expose thinking (🤔🎯⚡📊💡)</f>
    <f n="--task-manage" trigger=">3 steps, >2 dirs, >3 files">Delegation, progressive enhancement</f>
    <f n="--orchestrate" trigger="multi-tool, perf constraints, parallel ops">Tool matrix optimization, parallel thinking</f>
    <f n="--token-efficient" trigger="context >75%, large ops, --uc">Symbol communication, 30-50% reduction</f>
  </modes>

  <mcp>
    <f n="--c7|--context7" trigger="imports, frameworks, official docs">Context7: curated docs, patterns</f>
    <f n="--seq|--sequential" trigger="complex debug, system design">Sequential: multi-step reasoning</f>
    <f n="--magic" trigger="/ui, /21, design systems">Magic: 21st.dev UI components</f>
    <f n="--morph|--morphllm" trigger="bulk transforms, pattern edits">Morphllm: multi-file patterns</f>
    <f n="--serena" trigger="symbol ops, project memory">Serena: semantic understanding</f>
    <f n="--play|--playwright" trigger="browser testing, E2E, visual">Playwright: browser automation</f>
    <f n="--chrome|--devtools" trigger="perf audit, debug, layout">Chrome DevTools: real-time inspection</f>
    <f n="--tavily" trigger="web search, real-time info">Tavily: web search</f>
    <f n="--frontend-verify" trigger="UI testing, frontend debug">Playwright + DevTools + Serena</f>
    <f n="--all-mcp" trigger="max complexity">Enable all MCP servers</f>
    <f n="--no-mcp" trigger="native-only, perf priority">Disable all MCP, use native + WebSearch</f>
  </mcp>

  <analysis>
    <f n="--think" trigger="moderate complexity">~4K tokens, enables Sequential</f>
    <f n="--think-hard" trigger="architecture, system-wide">~10K tokens, Sequential + Context7</f>
    <f n="--ultrathink" trigger="critical redesign, legacy, complex debug">~32K tokens, all MCP</f>
  </analysis>

  <effort note="Opus 4.5 specific">
    <f n="--effort low">Minimal reasoning (~76% fewer tokens), fastest</f>
    <f n="--effort medium">Balanced (default)</f>
    <f n="--effort high">Maximum reasoning depth</f>
  </effort>

  <execution>
    <f n="--delegate [auto|files|folders]" trigger=">7 dirs, >50 files, complexity >0.8">Sub-agent parallel processing</f>
    <f n="--concurrency [n]" range="1-15">Max concurrent operations</f>
    <f n="--loop" trigger="polish, refine, enhance">Iterative improvement cycles</f>
    <f n="--iterations [n]" range="1-10">Improvement cycle count</f>
    <f n="--validate" trigger="risk >0.7, usage >75%, production">Pre-execution risk assessment</f>
    <f n="--safe-mode" trigger="usage >85%, production, critical">Max validation, conservative, auto --uc</f>
  </execution>

  <output>
    <f n="--uc|--ultracompressed" trigger="context pressure, efficiency">Symbol system, 30-50% reduction</f>
    <f n="--scope [file|module|project|system]">Analysis boundary</f>
    <f n="--focus [perf|security|quality|arch|a11y|testing]">Target domain</f>
  </output>

  <priority_rules>
    <r>Safety First: --safe-mode > --validate > optimization</r>
    <r>Explicit Override: User flags > auto-detection</r>
    <r>Depth: --ultrathink > --think-hard > --think</r>
    <r>MCP: --no-mcp overrides individual flags</r>
    <r>Scope: system > project > module > file</r>
  </priority_rules>
</component>
