<component name="mindbase" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>memory|conversation|session|semantic|embedding|pgvector|mindbase</triggers>

  <role>
    <mission>Semantic memory storage and retrieval using PostgreSQL with pgvector</mission>
  </role>

  <tools>
    <t n="conversation_save">Save conversations with auto embedding</t>
    <t n="conversation_get">Retrieve conversations with filtering</t>
    <t n="conversation_search">Semantic search across conversations</t>
    <t n="conversation_delete">Remove specific conversations</t>
    <t n="memory_write">Store memories (markdown + DB)</t>
    <t n="memory_read">Read memories</t>
    <t n="memory_list">List all memories</t>
    <t n="memory_search">Semantic search across memories</t>
    <t n="session_create">Create session for organizing</t>
    <t n="session_start">Start/resume a session</t>
  </tools>

  <install recommended="AIRIS MCP Gateway">
    <cmd>git clone https://github.com/agiletec-inc/airis-mcp-gateway.git</cmd>
    <cmd>cd airis-mcp-gateway &amp;&amp; docker compose up -d</cmd>
    <cmd>claude mcp add --scope user --transport sse airis-mcp-gateway http://localhost:9400/sse</cmd>
    <note>MindBase managed via airis-catalog.yaml. PostgreSQL+pgvector included.</note>
  </install>

  <links gateway="https://github.com/agiletec-inc/airis-mcp-gateway" standalone="https://github.com/agiletec-inc/mindbase"/>
</component>
