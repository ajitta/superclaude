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
    - /sc or /sc:sc
    - superclaude-help
    - command-list
  </triggers>

  <commands>
    - research: Deep web research with parallel search
    - index-repo: Repository indexing for context optimization
    - agent: Launch specialized AI agents
    - recommend: Get command recommendations
    - brainstorm: Requirements discovery via Socratic dialogue
    - analyze: Code analysis across quality/security/perf/arch
    - design: System architecture + API design
    - implement: Feature implementation + MCP integration
    - test: Test execution + coverage analysis
    - troubleshoot: Issue diagnosis + resolution
    - load: Session context loading (Serena)
    - save: Session context persistence
    - help: Complete command reference
  </commands>

  <features>
    - Parallel execution: multiple searches concurrent
    - Evidence-based: findings backed by sources
    - Context-aware: uses repo context when available
    - Token efficient: optimized minimal usage
  </features>

  <examples>

| Input | Output |
|-------|--------|
| `/sc:research React 18 features` | Deep research |
| `/sc:index-repo` | Create project index |
| `/sc:agent deep-research` | Launch agent |
| `/sc:recommend` | Get suggestions |

  </examples>

  <meta>
    - version: SuperClaude v4.1.7
    - package: superclaude 0.4.0
    - install: superclaude install
    - docs: github.com/SuperClaude-Org/SuperClaude_Framework
  </meta>

  <bounds will="display commands|provide help|route to features" wont="execute without command|modify files"/>
</component>
