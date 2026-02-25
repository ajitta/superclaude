---
description: SuperClaude command dispatcher - main entry point for all features
---
<component name="sc" type="command">

  <role>
    /sc
    <mission>SuperClaude command dispatcher - main entry point for all features</mission>
  </role>

  <syntax>/sc:[command] [args...]</syntax>

  <commands>
    - agent: Session controller + workflow orchestration
    - analyze: Code analysis across quality/security/perf/arch
    - brainstorm: Requirements discovery via Socratic dialogue
    - build: Build, compile, package with error handling
    - business-panel: Multi-expert business analysis
    - cleanup: Dead code removal + structure optimization
    - design: System architecture + API design
    - document: Focused documentation generation
    - estimate: Development time/effort estimates
    - explain: Code + concept explanations
    - git: Intelligent git operations + PR integration
    - help: Complete command reference
    - implement: Feature implementation + MCP integration
    - improve: Code quality + performance improvements
    - index: Project documentation + knowledge base
    - index-repo: Repository indexing (94% token reduction)
    - load: Session context loading (Serena)
    - pm: Project Manager Agent (default orchestration)
    - recommend: Get command recommendations
    - reflect: Task reflection + validation
    - research: Deep web research with parallel search
    - save: Session context persistence
    - select-tool: Intelligent MCP tool selection
    - spawn: Meta-system task orchestration
    - spec-panel: Multi-expert specification review
    - task: Complex task workflow management
    - test: Test execution + coverage analysis
    - troubleshoot: Issue diagnosis + resolution
    - workflow: PRD → implementation workflow
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

  <example name="unknown-command" type="error-path">
    <input>/sc:deploy (command does not exist)</input>
    <why_wrong>'deploy' is not a registered /sc command.</why_wrong>
    <correct>Use /sc:help to see available commands. For deployment: /sc:build --type prod then /ship</correct>
  </example>
  </examples>

  <meta>
    - version: SuperClaude v4.2.1+ajitta
    - package: superclaude 4.2.1+ajitta
    - install: superclaude install
    - docs: github.com/ajitta/superclaude
  </meta>

  <bounds will="command dispatch|feature routing|context-aware help" wont="execute without explicit command|modify files|bypass command validation" fallback="Ask user for guidance when uncertain"/>

  <handoff next="/sc:recommend /sc:help"/>
</component>
