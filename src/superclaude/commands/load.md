<component name="load" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:load
    <mission>Session lifecycle management with Serena MCP integration for project context loading</mission>
  </role>

  <syntax>/sc:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]</syntax>

  <triggers>
    <t>Session initialization</t>
    <t>Cross-session persistence</t>
    <t>Project activation</t>
    <t>Checkpoint loading</t>
  </triggers>

  <flow>
    <s n="1">Initialize: Serena MCP + session context</s>
    <s n="2">Discover: Project structure + requirements</s>
    <s n="3">Load: Memories + checkpoints + persistence data</s>
    <s n="4">Activate: Project context + workflow prep</s>
    <s n="5">Validate: Context integrity + session readiness</s>
  </flow>

  <mcp servers="serena:memory|serena:persistence"/>

  <tools>
    <t n="activate_project">Core project activation</t>
    <t n="list_memories/read_memory">Memory retrieval</t>
    <t n="Read/Grep/Glob">Structure analysis</t>
    <t n="Write">Checkpoint creation</t>
  </tools>

  <patterns>
    <p n="Activation">Directory → memory → context establish</p>
    <p n="Restoration">Checkpoint → validation → workflow prep</p>
    <p n="Memory">Cross-session → continuity → efficiency</p>
    <p n="Performance">&lt;500ms init | &lt;200ms core | &lt;1s checkpoint</p>
  </patterns>

  <examples>
    <ex i="/sc:load" o="Current dir + Serena memory"/>
    <ex i="/path/to/project --type project --analyze" o="Specific project + analysis"/>
    <ex i="--type checkpoint --checkpoint session_123" o="Restore checkpoint"/>
    <ex i="--type deps --refresh" o="Fresh dependency analysis"/>
  </examples>

  <bounds will="Serena integration|cross-session persistence|context loading" wont="modify structure|load without validation|override without checkpoint"/>
</component>
