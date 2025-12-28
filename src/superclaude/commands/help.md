---
description: List all available /sc commands and their functionality
---
<component name="help" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:help
    <mission>List all available /sc commands and their functionality</mission>
  </role>

  <triggers>
    - Command discovery + reference
    - Framework capability overview
    - Documentation for commands
  </triggers>

  <flow>
    1. **Display**: Complete command list
    2. **Complete**: End after display
  </flow>

  <commands>
    - **analyze**: Code analysis: quality, security, performance, architecture
    - **brainstorm**: Requirements discovery via Socratic dialogue
    - **build**: Build, compile, package with error handling
    - **business-panel**: Multi-expert business analysis
    - **cleanup**: Dead code removal + structure optimization
    - **design**: System architecture + API design
    - **document**: Focused documentation generation
    - **estimate**: Development time/effort estimates
    - **explain**: Code + concept explanations
    - **git**: Intelligent git operations
    - **help**: This command reference
    - **implement**: Feature implementation + MCP integration
    - **improve**: Code quality + performance improvements
    - **index**: Project documentation + knowledge base
    - **load**: Session context loading (Serena)
    - **reflect**: Task reflection + validation
    - **save**: Session context persistence
    - **select-tool**: Intelligent MCP tool selection
    - **spawn**: Meta-system task orchestration
    - **spec-panel**: Multi-expert specification review
    - **task**: Complex task workflow management
    - **test**: Test execution + coverage analysis
    - **troubleshoot**: Issue diagnosis + resolution
    - **workflow**: PRD → implementation workflow
  </commands>

  <flags>
    <category name="Mode">
      - **--brainstorm**: Collaborative discovery
      - **--introspect**: Expose thinking process
      - **--task-manage**: Systematic organization
      - **--orchestrate**: Parallel tool optimization
      - **--token-efficient**: 30-50% token reduction
    </category>
    <category name="MCP">
      - **--c7|--context7**: Curated documentation
      - **--seq|--sequential**: Multi-step reasoning
      - **--magic**: UI generation (21st.dev)
      - **--morph|--morphllm**: Bulk transformations
      - **--serena**: Semantic + memory
      - **--play|--playwright**: Browser automation
      - **--all-mcp**: Enable all servers
      - **--no-mcp**: Native tools only
    </category>
    <category name="Depth">
      - **--think**: ~4K tokens, Sequential
      - **--think-hard**: ~10K tokens, Seq+C7
      - **--ultrathink**: ~32K tokens, all MCP
    </category>
    <category name="Control">
      - **--delegate**: Sub-agent parallel processing
      - **--concurrency [n]**: Max concurrent ops (1-15)
      - **--loop**: Iterative improvement cycles
      - **--validate**: Pre-execution risk assessment
      - **--safe-mode**: Maximum validation
    </category>
    <category name="Output">
      - **--uc|--ultracompressed**: Symbol communication
      - **--scope**: file|module|project|system
      - **--focus**: perf|sec|qual|arch|a11y|test
    </category>
  </flags>

  <priority_rules>
    - **Safety**: --safe-mode > --validate > optimization
    - **Override**: User flags > auto-detection
    - **Depth**: --ultrathink > --think-hard > --think
    - **MCP**: --no-mcp overrides all MCP flags
    - **Scope**: system > project > module > file
  </priority_rules>

  <bounds will="display commands|flags|usage" wont="execute|create files|activate modes"/>
</component>
