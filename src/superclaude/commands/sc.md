---
description: SuperClaude command dispatcher - main entry point for all features
---
<component name="sc" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc
    <mission>SuperClaude command dispatcher - main entry point for all features</mission>
  </role>

  <syntax>/sc:[command] [args...]</syntax>

  <triggers>
    <t>/sc or /sc:sc</t>
    <t>superclaude-help</t>
    <t>command-list</t>
  </triggers>

  <commands>
    <c n="research">Deep web research with parallel search</c>
    <c n="index-repo">Repository indexing for context optimization</c>
    <c n="agent">Launch specialized AI agents</c>
    <c n="recommend">Get command recommendations</c>
    <c n="brainstorm">Requirements discovery via Socratic dialogue</c>
    <c n="analyze">Code analysis across quality/security/perf/arch</c>
    <c n="design">System architecture + API design</c>
    <c n="implement">Feature implementation + MCP integration</c>
    <c n="test">Test execution + coverage analysis</c>
    <c n="troubleshoot">Issue diagnosis + resolution</c>
    <c n="load">Session context loading (Serena)</c>
    <c n="save">Session context persistence</c>
    <c n="help">Complete command reference</c>
  </commands>

  <features>
    <f>Parallel execution: multiple searches concurrent</f>
    <f>Evidence-based: findings backed by sources</f>
    <f>Context-aware: uses repo context when available</f>
    <f>Token efficient: optimized minimal usage</f>
  </features>

  <examples>
    <ex i="/sc:research React 18 features" o="Deep research"/>
    <ex i="/sc:index-repo" o="Create project index"/>
    <ex i="/sc:agent deep-research" o="Launch agent"/>
    <ex i="/sc:recommend" o="Get suggestions"/>
  </examples>

  <meta>
    <version>SuperClaude v4.1.7</version>
    <package>superclaude 0.4.0</package>
    <install>superclaude install</install>
    <docs>github.com/SuperClaude-Org/SuperClaude_Framework</docs>
  </meta>

  <bounds will="display commands|provide help|route to features" wont="execute without command|modify files"/>
</component>
