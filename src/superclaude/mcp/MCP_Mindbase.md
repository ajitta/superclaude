<component name="mindbase" type="mcp" status="deprecated">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>memory|conversation|session|semantic|embedding|pgvector|mindbase</triggers>

  <deprecated>Standalone mindbase is deprecated. Use airis-mcp-gateway instead: https://github.com/agiletec-inc/airis-mcp-gateway</deprecated>

  <role>
    <mission>Semantic memory storage and retrieval using PostgreSQL with pgvector</mission>
  </role>

  <tools>
- conversation_save: Save conversations with auto embedding
- conversation_get: Retrieve conversations with filtering
- conversation_search: Semantic search across conversations
- conversation_delete: Remove specific conversations
- memory_write: Store memories (markdown + DB)
- memory_read: Read memories
- memory_list: List all memories
- memory_search: Semantic search across memories
- session_create: Create session for organizing
- session_start: Start/resume a session
  </tools>

  <install recommended="AIRIS MCP Gateway">
```bash
git clone https://github.com/agiletec-inc/airis-mcp-gateway.git
cd airis-mcp-gateway && docker compose up -d
claude mcp add --scope user --transport sse airis-mcp-gateway http://localhost:9400/sse
```
Note: MindBase managed via airis-catalog.yaml. PostgreSQL+pgvector included.
  </install>

  <links>
- Gateway: https://github.com/agiletec-inc/airis-mcp-gateway
- Standalone: https://github.com/agiletec-inc/mindbase
  </links>
</component>
