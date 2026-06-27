---
description: SuperClaude command dispatcher - main entry point for all features. Use ONLY when the user explicitly types `/sc:sc` — this is a meta-dispatcher that routes to other /sc:* commands. Do NOT auto-trigger; if intent matches a specific /sc:* command, invoke that one directly.
---
<component name="sc" type="command">

  <role command="/sc:sc">
    <mission>SuperClaude command dispatcher - main entry for all features</mission>
  </role>

  <syntax>/sc:[command] [args...]</syntax>
  <flow>
  1. Parse: identify /sc: subcommand + flags from input
  2. Route: dispatch to matching command file in commands/sc/
  3. Execute: run command with args + flags
  </flow>


  <commands>
    - agent: Session controller + workflow orchestration
    - analyze: Code analysis across quality/security/perf/arch
    - brainstorm: Requirements discovery via Socratic dialogue
    - build: Build, compile, package with error handling
    - business-panel: Multi-expert business analysis
    - cleanup: Dead code removal + structure optimization
    - design: System architecture + API design
    - document: Focused doc generation
    - estimate: Dev time/effort estimates
    - explain: Code + concept explanations
    - git: Smart git ops + PR integration
    - help: Full command reference
    - implement: Feature implementation + MCP integration
    - improve: Code quality + perf improvements
    - index: Project docs + knowledge base
    - index-repo: Repo indexing (94% token reduction)
    - load: Session context loading (Serena)
    - pm: Project Manager Agent (default orchestration)
    - recommend: Get command recommendations
    - reflect: Task reflection + validation
    - research: Deep web research with parallel search
    - save: Session context persistence
    - select-tool: Smart MCP tool selection
    - sc: Command dispatcher (this command)
    - spec-panel: Multi-expert spec review
    - task: Complex task workflow management
    - test: Test execution + coverage analysis
    - troubleshoot: Issue diagnosis + resolution
    - roadmap: Generate task plan from PRD
    - init: Interactive project env setup
    - insight: Capture structured session insights
    - plan: Detailed impl plans with TDD tasks
    - review: Code review with structured feedback
    - auto-improve: Autonomous overnight code improvement loop (Karpathy AutoResearch)
    - promote-feature: Promote standalone docs into a feature folder
  </commands>

  <features>
    - Parallel execution: multiple searches concurrent
    - Evidence-based: findings backed by sources
    - Context-aware: uses repo context when available
    - Token efficient: optimized minimal usage
  </features>


  <examples>

| Input | Output |
|---|---|
| `/sc:research React 18 features` | Deep research |
| `/sc:index-repo` | Create project index |
| `/sc:agent deep-research` | Launch agent |
| `/sc:recommend` | Get suggestions |

  <example name="unknown-command" type="error-path">
    - Input: /sc:deploy (command not exist)
    - Why wrong: 'deploy' not registered /sc command.
    - Correct: Use /sc:help for available commands. For deployment: /sc:build --type prod then /ship
  </example>
  </examples>

  <meta>
    - version: SuperClaude v4.6.0+ajitta
    - package: superclaude 4.6.0+ajitta
    - install: superclaude install
    - docs: github.com/ajitta/superclaude
  </meta>

  <gotchas>
  - phantom-command: No reference to commands not exist. Verify against actual files in commands/sc/
  - stale-list: Command list may go outdated. When adding new commands, update this dispatcher
  </gotchas>

  <bounds>
    <does>command dispatch, feature routing, context-aware help.</does>
    <never>execute without explicit command, modify files, bypass command validation.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:recommend /sc:help"/>
</component>