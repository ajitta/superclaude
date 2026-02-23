---
description: Session lifecycle management with Serena MCP integration for project context loading
---
<component name="load" type="command">

  <role>
    /sc:load
    <mission>Session lifecycle management with Serena MCP integration for project context loading</mission>
  </role>

  <syntax>/sc:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]</syntax>

  <triggers>session initialization|cross-session persistence|project activation|checkpoint loading</triggers>

  <flow>
    1. Initialize: activate_project() → check_onboarding_performed()
    2. Load: list_memories() → read_memory("pm_context") → read_memory("last_session") → read_memory("next_actions")
    3. Discover: Project structure + requirements (get_symbols_overview, list_dir)
    4. Activate: Project context + workflow prep
    5. Validate: Context integrity + session readiness
    Fallback (no Serena): Read CLAUDE.md, PLANNING.md, TASK.md; Glob for structure discovery
  </flow>

  <mcp servers="serena"/>

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
| `session_123 --type checkpoint` | Restore checkpoint |
| `--type deps --refresh` | Fresh dependency analysis |

  <example name="load-wrong-project" type="error-path">
    <input>/sc:load /path/to/wrong/project --type project</input>
    <why_wrong>Loading context for the wrong project pollutes the session with irrelevant information.</why_wrong>
    <correct>Verify project path first (ls, git remote -v), then /sc:load with confirmed path.</correct>
  </example>

  </examples>

  <bounds will="Serena integration|cross-session persistence|context loading" wont="modify structure|load without validation|override without checkpoint" fallback="Without Serena: use Read for CLAUDE.md/PLANNING.md/TASK.md, Glob for structure discovery. Ask user for guidance when uncertain"/>

  <boundaries type="execution">Execute session/project activation | Preserve project structure unchanged | Validate context before proceeding</boundaries>




  <handoff next="/sc:analyze /sc:index-repo /sc:task"/>
</component>
