<component name="airis-agent" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>confidence|research|index|optimize|sync|airis</triggers>

  <role>
    <mission>Confidence checking, deep research, and repository indexing capabilities</mission>
  </role>

  <tools>
- **airis_confidence_check**: Validate decisions before implementation
- **airis_deep_research**: Comprehensive research with web search
- **airis_repo_index**: Index repository structure for better context
- **airis_docs_optimize**: Optimize documentation structure
- **airis_sync_manifest**: Sync manifest.toml with filesystem
  </tools>

  <install recommended="AIRIS MCP Gateway">
```bash
git clone https://github.com/agiletec-inc/airis-mcp-gateway.git
cd airis-mcp-gateway && docker compose up -d
claude mcp add --scope user --transport sse airis-mcp-gateway http://localhost:9400/sse
```
  </install>

  <links>
- **Gateway**: https://github.com/agiletec-inc/airis-mcp-gateway
- **Standalone**: https://github.com/agiletec-inc/airis-agent
  </links>
</component>
