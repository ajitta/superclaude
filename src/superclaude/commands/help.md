---
description: List all available /sc commands and their functionality
---
<component name="help" type="command">

  <role>
    /sc:help
    <mission>List all available /sc commands and their functionality</mission>
  </role>

  <triggers>command discovery|framework capabilities|command documentation</triggers>

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
      - --effort low: May skip thinking
      - --effort medium: Selective thinking, Sequential
      - --effort high: Default, almost always thinks, Seq+C7
      - --effort max: Unconstrained depth (Claude 4 models), all MCP
      Legacy: --think→medium, --think-hard→high, --ultrathink→max+all-mcp
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
      - --focus: perf|sec|qual|arch|a11y|test
    </category>
  </flags>

  <priority_rules>
    - Safety: --safe-mode > --validate > optimization
    - Override: User flags > auto-detection
    - Effort: high > medium > low
    - MCP: --no-mcp overrides all MCP flags
    - Scope: system > project > module > file
  </priority_rules>


  <bounds will="complete reference display|categorized flag listing|usage examples" wont="execute commands|create files|activate modes|modify project state" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Display reference information only, then complete | Do not execute any commands automatically | Do not modify files or project state → Output: Command and flag reference documentation</boundaries>


  <handoff>
    <next command="/sc:recommend">For intelligent command suggestions</next>
    <next command="/sc:[command]">Execute specific command</next>
    <format>Reference documentation for user selection</format>
  </handoff>
</component>
