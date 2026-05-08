---
description: Session lifecycle management with Serena MCP + Claude auto memory for project context loading. Use ONLY when the user explicitly types `/sc:load` — this is a session-start action that primes context from Serena memory and project state. Do NOT auto-trigger on session resumption or "let's continue".
---
<component name="load" type="command">

  <role command="/sc:load">
    <mission>Session lifecycle management with Serena MCP + Claude auto memory for project context loading</mission>
  </role>

  <syntax>/sc:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]</syntax>

  <flow>
  1. Initialize: MCP auto-activates from CWD; verify with check_onboarding_performed()
  2. Load (Serena): list_memories() → read_memory("pm_context") → read_memory("last_session") → read_memory("next_actions")
  3. Load (auto memory): MEMORY.md (auto-loaded) + topic files linked from MEMORY.md
  4. Discover: Project structure + requirements (get_symbols_overview, Read/Grep/Glob)
  5. Activate: Project context + workflow prep
  6. Validate: Context integrity + session readiness
  7. Session Goal (optional): If user provides a goal, record as 1-line objective. Display as reminder when context exceeds 60%.
    Fallback (no Serena): Claude auto memory + Read CLAUDE.md, PLANNING.md, TASK.md; Glob for structure discovery
  </flow>

  <storage>
    Serena (primary): .serena/memories/ — semantic project memories, symbol-aware context
    Auto memory (supplementary): .claude/memory/MEMORY.md (project-scoped, committable, max 200 lines)
    Topic files: .claude/memory/{topic}.md (linked from MEMORY.md)
    Agent memory: .claude/agent-memory/{name}/MEMORY.md (project-scoped, per-agent)
  </storage>


  <tools>
  - list_memories/read_memory: Serena memory retrieval
  - get_symbols_overview: Serena structure analysis (use native Glob for directory listing)
  - Read/Grep/Glob: Auto memory + project file analysis
  - Write: Checkpoint creation
  </tools>

  <patterns>
    - Activation: Serena memories (auto-active) → auto memory → context establish
    - Restoration: Checkpoint → validation → workflow prep
    - Memory: Cross-session → continuity → efficiency
    - Performance: <500ms init | <200ms core | <1s checkpoint
  </patterns>

  <examples>

| Input | Output |
|---|---|
| `/sc:load` | Current dir + Serena memory + auto memory |
| `/path/to/project --type project --analyze` | Specific project + analysis |
| `session_123 --type checkpoint` | Restore checkpoint |
| `--type deps --refresh` | Fresh dependency analysis |

  <example name="load-wrong-project" type="error-path">
    - Input: /sc:load /path/to/wrong/project --type project
    - Why wrong: Loading context for the wrong project pollutes the session with irrelevant information.
    - Correct: Verify project path first (ls, git remote -v), then /sc:load with confirmed path.
  </example>

  </examples>


  <gotchas>
  - stale-memory: Verify loaded memory against current file state before acting on it
  - dual-persistence: Check both Serena memory and auto memory for complete context
  </gotchas>

  <bounds>
    <does>Serena integration, auto memory loading, cross-session persistence, and context loading.</does>
    <never>modify structure, load without validation, and override without checkpoint.</never>
    <fallback>Without Serena: use Claude auto memory + Read CLAUDE.md/PLANNING.md/TASK.md, Glob for structure. Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:analyze /sc:index-repo /sc:task"/>
</component>
