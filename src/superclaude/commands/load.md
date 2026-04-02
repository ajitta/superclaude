---
description: Session lifecycle management with Serena MCP + Claude auto memory for project context loading
---
<component name="load" type="command">

  <role>
    /sc:load
    <mission>Session lifecycle management with Serena MCP + Claude auto memory for project context loading</mission>
  </role>

  <syntax>/sc:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]</syntax>

  <flow>
    1. Initialize: activate_project() → check_onboarding_performed()
    2. Load (Serena): list_memories() → read_memory("pm_context") → read_memory("last_session") → read_memory("next_actions")
    3. Load (auto memory): MEMORY.md (auto-loaded) + topic files linked from MEMORY.md
    4. Discover: Project structure + requirements (get_symbols_overview, list_dir, Read/Grep/Glob)
    5. Activate: Project context + workflow prep
    6. Validate: Context integrity + session readiness
    7. Session Goal (optional): If user provides a goal, record as 1-line objective. Display as reminder when context exceeds 60%.
    Fallback (no Serena): Claude auto memory + Read CLAUDE.md, PLANNING.md, TASK.md; Glob for structure discovery
  </flow>

  <storage note="Dual persistence">
    Serena (primary): .serena/memories/ — semantic project memories, symbol-aware context
    Auto memory (supplementary): .claude/memory/MEMORY.md (project-scoped, committable, max 200 lines)
    Topic files: .claude/memory/{topic}.md (linked from MEMORY.md)
    Agent memory: .claude/agent-memory/{name}/MEMORY.md (project-scoped, per-agent)
  </storage>


  <tools>
    - activate_project: Serena project activation (primary)
    - list_memories/read_memory: Serena memory retrieval
    - get_symbols_overview/list_dir: Serena structure analysis
    - Read/Grep/Glob: Auto memory + project file analysis
    - Write: Checkpoint creation
  </tools>

  <patterns>
    - Activation: Serena activate → Serena memories → auto memory → context establish
    - Restoration: Checkpoint → validation → workflow prep
    - Memory: Cross-session → continuity → efficiency
    - Performance: <500ms init | <200ms core | <1s checkpoint
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `/sc:load` | Current dir + Serena memory + auto memory |
| `/path/to/project --type project --analyze` | Specific project + analysis |
| `session_123 --type checkpoint` | Restore checkpoint |
| `--type deps --refresh` | Fresh dependency analysis |

  <example name="load-wrong-project" type="error-path">
    <input>/sc:load /path/to/wrong/project --type project</input>
    <why_wrong>Loading context for the wrong project pollutes the session with irrelevant information.</why_wrong>
    <correct>Verify project path first (ls, git remote -v), then /sc:load with confirmed path.</correct>
  </example>

  </examples>

  <bounds will="Serena integration|auto memory loading|cross-session persistence|context loading" wont="modify structure|load without validation|override without checkpoint" fallback="Without Serena: use Claude auto memory + Read CLAUDE.md/PLANNING.md/TASK.md, Glob for structure. Ask user for guidance when uncertain" type="execution">
    Execute session/project activation | Preserve project structure unchanged | Validate context before proceeding
  </bounds>

  <handoff next="/sc:analyze /sc:index-repo /sc:task"/>
</component>
