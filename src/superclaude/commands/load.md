---
description: Session lifecycle management with Serena MCP integration for project context loading
---
<component name="load" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:load
    <mission>Session lifecycle management with Serena MCP integration for project context loading</mission>
  </role>

  <syntax>/sc:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]</syntax>

  <triggers>
    - Session initialization
    - Cross-session persistence
    - Project activation
    - Checkpoint loading
  </triggers>

  <flow>
    1. Initialize: Serena MCP + session context
    2. Discover: Project structure + requirements
    3. Load: Memories + checkpoints + persistence data
    4. Activate: Project context + workflow prep
    5. Validate: Context integrity + session readiness
  </flow>

  <mcp servers="serena:memory|serena:persistence"/>

  <tools>
    - activate_project: Core project activation
    - list_memories/read_memory: Memory retrieval
    - Read/Grep/Glob: Structure analysis
    - Write: Checkpoint creation
  </tools>

  <patterns>
    - Activation: Directory → memory → context establish
    - Restoration: Checkpoint → validation → workflow prep
    - Memory: Cross-session → continuity → efficiency
    - Performance: <500ms init | <200ms core | <1s checkpoint
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `/sc:load` | Current dir + Serena memory |
| `/path/to/project --type project --analyze` | Specific project + analysis |
| `--type checkpoint --checkpoint session_123` | Restore checkpoint |
| `--type deps --refresh` | Fresh dependency analysis |

  </examples>

  <bounds will="Serena integration|cross-session persistence|context loading" wont="modify structure|load without validation|override without checkpoint"/>

  <boundaries type="execution" critical="true">
    <rule>EXECUTE session/project activation</rule>
    <rule>DO NOT modify project structure</rule>
    <rule>Validate context before proceeding</rule>
  </boundaries>

  <completion_criteria>
    - [ ] Project activated successfully
    - [ ] Memories loaded (if available)
    - [ ] Context validated for integrity
    - [ ] Session ready for work
  </completion_criteria>

  <handoff>
    <next command="/sc:analyze">For understanding loaded project</next>
    <next command="/sc:index-repo">For quick project overview</next>
    <next command="/sc:task">For resuming work from checkpoint</next>
    <format>Project context loaded and ready</format>
  </handoff>
</component>
