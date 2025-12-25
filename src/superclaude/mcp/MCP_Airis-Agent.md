<component name="airis-agent" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>confidence|research|index|optimize|sync|airis</triggers>

  <role>
    <mission>Confidence checking, deep research, and repository indexing capabilities</mission>
  </role>

  <tools>
    <t n="airis_confidence_check">Validate decisions before implementation</t>
    <t n="airis_deep_research">Comprehensive research with web search</t>
    <t n="airis_repo_index">Index repository structure for better context</t>
    <t n="airis_docs_optimize">Optimize documentation structure</t>
    <t n="airis_sync_manifest">Sync manifest.toml with filesystem</t>
  </tools>

  <install recommended="AIRIS MCP Gateway">
    <cmd>git clone https://github.com/agiletec-inc/airis-mcp-gateway.git</cmd>
    <cmd>cd airis-mcp-gateway &amp;&amp; docker compose up -d</cmd>
    <cmd>claude mcp add --scope user --transport sse airis-mcp-gateway http://localhost:9400/sse</cmd>
  </install>

  <links gateway="https://github.com/agiletec-inc/airis-mcp-gateway" standalone="https://github.com/agiletec-inc/airis-agent"/>
</component>
