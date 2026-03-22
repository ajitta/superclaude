---
description: List all available /sc commands and their functionality
---

<component name="help" type="command">

  <role>
    /sc:help
    <mission>List all available /sc commands and their functionality</mission>
  </role>

  <flow>
    1. Display: Complete command list
    2. Complete: End after display
  </flow>

  <commands>
    - agent: Session controller + workflow orchestration
    - analyze: Code analysis: quality, security, performance, architecture
    - brainstorm: Requirements discovery via Socratic dialogue
    - build: Build, compile, package with error handling
    - business-panel: Multi-expert business analysis
    - cleanup: Dead code removal + structure optimization
    - design: System architecture + API design
    - document: Focused documentation generation
    - estimate: Development time/effort estimates
    - explain: Code + concept explanations
    - git: Intelligent git operations + PR integration
    - help: This command reference
    - implement: Feature implementation + MCP integration
    - improve: Code quality + performance improvements
    - index: Project documentation + knowledge base
    - index-repo: Repository indexing (94% token reduction)
    - load: Session context loading (Serena)
    - pm: Project Manager Agent (default orchestration)
    - recommend: Intelligent command recommendations
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

  <scope_map note="Disambiguation for overlapping commands">
  Analysis: analyze (static quality metrics) | review (PR/diff-level) | reflect (post-implementation self-check)
  Project mgmt: task (single-session tracking) | pm (multi-session orchestration) | spawn (one-shot parallel sub-agents)
  Implementation: implement (write/modify code) | build (compile, package, deploy)
  Documentation: document (prose for humans) | index (structured knowledge base) | index-repo (repo catalog)
  Discovery: brainstorm (Socratic requirements) | research (evidence-based investigation)
  Advisory: business-panel (market/strategy) | spec-panel (technical specification review)
  </scope_map>

  <flags>
    <category name="Mode">
      - --brainstorm: Collaborative discovery
      - --business-panel: Multi-expert business analysis
      - --research: Systematic investigation mode
      - --introspect: Expose thinking process
      - --task-manage: Systematic organization
      - --orchestrate: Parallel tool optimization
      - --token-efficient: 30-50% token reduction
    </category>
    <category name="MCP">
      - --c7|--context7: Curated documentation
      - --seq|--sequential: Multi-step reasoning
      - --magic: UI generation (21st.dev)
      - --morph|--morphllm: Bulk transformations
      - --serena: Semantic + memory
      - --play|--playwright: Browser automation
      - --all-mcp: Enable all servers
      - --no-mcp: Native tools only
    </category>
    <category name="Effort">
      - Claude Code native (not managed by SuperClaude)
    </category>
    <category name="Control">
      - --delegate: Sub-agent parallel processing
      - --concurrency [n]: Max concurrent ops (1-15)
      - --loop: Iterative improvement cycles
      - --validate: Pre-execution risk assessment
      - --safe-mode: Maximum validation
    </category>
    <category name="Output">
      - --uc|--ultracompressed: Symbol communication
      - --scope: file|module|project|system
      - --focus: perf|security|quality|arch|a11y|testing
    </category>
  </flags>

<priority_rules> - Safety: --safe-mode > --validate > optimization - Override: User flags > auto-detection - Effort: high > medium > low - MCP: --no-mcp overrides all MCP flags - Scope: system > project > module > file
</priority_rules>

  <examples>

  <example name="help-as-execution" type="error-path">
    <input>/sc:help implement auth (expecting it to run /sc:implement)</input>
    <why_wrong>help is reference-only. It displays information but does not execute commands.</why_wrong>
    <correct>Use /sc:implement 'auth system' to execute. Use /sc:help to see what's available.</correct>
  </example>

  </examples>

  <workflows note="Common multi-command pipelines">

  <workflow name="feature-development">
    /sc:brainstorm 'user auth' → requirements doc
    /sc:design --type api → architecture spec
    /sc:implement --type feature --with-tests → code + tests
    /sc:test --type e2e --coverage → validation
    /ship --pr → delivery
  </workflow>

  <workflow name="performance-fix">
    /sc:analyze --focus perf --perf → bottleneck report
    /sc:troubleshoot --type performance --trace → root cause
    /sc:improve --type performance → optimized code
    /sc:test --type e2e → regression check
  </workflow>

  <workflow name="research-to-implementation">
    /sc:research 'topic' --depth deep → findings report
    /sc:brainstorm 'approach' → refined requirements
    /sc:design → architecture spec
    /sc:implement → code
  </workflow>

  <workflow name="code-quality">
    /sc:analyze --focus quality → issue report
    /sc:cleanup --type code --safe → dead code removal
    /sc:improve --type quality → refactored code
    /sc:test --coverage → verify improvements
  </workflow>

  </workflows>

  <bounds will="complete reference display|categorized flag listing|usage examples" wont="execute commands|create files|activate modes|modify project state" fallback="Ask user for guidance when uncertain" type="document-only">

    Display reference information only, then complete | Do not execute any commands automatically | Do not modify files or project state → Output: Command and flag reference documentation

  </bounds>

  <handoff next="/sc:recommend /sc:[command]"/>
</component>
