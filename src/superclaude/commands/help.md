<component name="help" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:help
    <mission>List all available /sc commands and their functionality</mission>
  </role>

  <triggers>
    <t>Command discovery + reference</t>
    <t>Framework capability overview</t>
    <t>Documentation for commands</t>
  </triggers>

  <flow>
    <s n="1">Display: Complete command list</s>
    <s n="2">Complete: End after display</s>
  </flow>

  <commands>
    <c n="analyze">Code analysis: quality, security, performance, architecture</c>
    <c n="brainstorm">Requirements discovery via Socratic dialogue</c>
    <c n="build">Build, compile, package with error handling</c>
    <c n="business-panel">Multi-expert business analysis</c>
    <c n="cleanup">Dead code removal + structure optimization</c>
    <c n="design">System architecture + API design</c>
    <c n="document">Focused documentation generation</c>
    <c n="estimate">Development time/effort estimates</c>
    <c n="explain">Code + concept explanations</c>
    <c n="git">Intelligent git operations</c>
    <c n="help">This command reference</c>
    <c n="implement">Feature implementation + MCP integration</c>
    <c n="improve">Code quality + performance improvements</c>
    <c n="index">Project documentation + knowledge base</c>
    <c n="load">Session context loading (Serena)</c>
    <c n="reflect">Task reflection + validation</c>
    <c n="save">Session context persistence</c>
    <c n="select-tool">Intelligent MCP tool selection</c>
    <c n="spawn">Meta-system task orchestration</c>
    <c n="spec-panel">Multi-expert specification review</c>
    <c n="task">Complex task workflow management</c>
    <c n="test">Test execution + coverage analysis</c>
    <c n="troubleshoot">Issue diagnosis + resolution</c>
    <c n="workflow">PRD → implementation workflow</c>
  </commands>

  <flags>
    <category name="Mode">
      <f n="--brainstorm">Collaborative discovery</f>
      <f n="--introspect">Expose thinking process</f>
      <f n="--task-manage">Systematic organization</f>
      <f n="--orchestrate">Parallel tool optimization</f>
      <f n="--token-efficient">30-50% token reduction</f>
    </category>
    <category name="MCP">
      <f n="--c7|--context7">Curated documentation</f>
      <f n="--seq|--sequential">Multi-step reasoning</f>
      <f n="--magic">UI generation (21st.dev)</f>
      <f n="--morph|--morphllm">Bulk transformations</f>
      <f n="--serena">Semantic + memory</f>
      <f n="--play|--playwright">Browser automation</f>
      <f n="--all-mcp">Enable all servers</f>
      <f n="--no-mcp">Native tools only</f>
    </category>
    <category name="Depth">
      <f n="--think">~4K tokens, Sequential</f>
      <f n="--think-hard">~10K tokens, Seq+C7</f>
      <f n="--ultrathink">~32K tokens, all MCP</f>
    </category>
    <category name="Control">
      <f n="--delegate">Sub-agent parallel processing</f>
      <f n="--concurrency [n]">Max concurrent ops (1-15)</f>
      <f n="--loop">Iterative improvement cycles</f>
      <f n="--validate">Pre-execution risk assessment</f>
      <f n="--safe-mode">Maximum validation</f>
    </category>
    <category name="Output">
      <f n="--uc|--ultracompressed">Symbol communication</f>
      <f n="--scope">file|module|project|system</f>
      <f n="--focus">perf|sec|qual|arch|a11y|test</f>
    </category>
  </flags>

  <priority_rules>
    <r>Safety: --safe-mode > --validate > optimization</r>
    <r>Override: User flags > auto-detection</r>
    <r>Depth: --ultrathink > --think-hard > --think</r>
    <r>MCP: --no-mcp overrides all MCP flags</r>
    <r>Scope: system > project > module > file</r>
  </priority_rules>

  <bounds will="display commands|flags|usage" wont="execute|create files|activate modes"/>
</component>
