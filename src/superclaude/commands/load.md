---
description: Session lifecycle mgmt w/ Serena MCP + Claude auto memory for proj context load. Use ONLY when user explicitly type `/sc:load` — session-start action prime context from Serena memory + proj state. Do NOT auto-trigger on session resume or "let's continue".
---
<component name="load" type="command">

  <role command="/sc:load">
    <mission>Session lifecycle mgmt w/ Serena MCP + Claude auto memory for proj context load</mission>
  </role>

  <syntax>/sc:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]</syntax>

  <flow>
  1. Initialize: MCP auto-activate from CWD; verify w/ check_onboarding_performed()
  2. Load (Serena): list_memories() → read_memory("pm_context") → read_memory("last_session") → read_memory("next_actions")
  3. Load (auto memory): MEMORY.md (auto-load) + topic files linked from MEMORY.md
  4. Discover: Proj struct + reqs (get_symbols_overview, Read/Grep/Glob)
  5. Activate: Proj context + workflow prep
  6. Validate: Context integrity + session ready
  7. Session Goal (optional): If user give goal, record as 1-line objective. Show as reminder when context > 60%.
    Fallback (no Serena): Claude auto memory + Read CLAUDE.md, PLANNING.md, TASK.md; Glob for struct discover
  </flow>

  <storage>
    Serena (primary): .serena/memories/ — semantic proj memories, symbol-aware context
    Auto memory (supplementary): .claude/memory/MEMORY.md (proj-scoped, committable, max 200 lines)
    Topic files: .claude/memory/{topic}.md (linked from MEMORY.md)
    Agent memory: .claude/agent-memory/{name}/MEMORY.md (proj-scoped, per-agent)
  </storage>


  <tools>
  - list_memories/read_memory: Serena memory retrieval
  - get_symbols_overview: Serena struct analysis (use native Glob for dir listing)
  - Read/Grep/Glob: Auto memory + proj file analysis
  - Write: Checkpoint create
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
| `/path/to/project --type project --analyze` | Specific proj + analysis |
| `session_123 --type checkpoint` | Restore checkpoint |
| `--type deps --refresh` | Fresh dep analysis |

  <example name="load-wrong-project" type="error-path">
    - Input: /sc:load /path/to/wrong/project --type project
    - Why wrong: Load context for wrong proj pollute session w/ irrelevant info.
    - Correct: Verify proj path first (ls, git remote -v), then /sc:load w/ confirmed path.
  </example>

  </examples>


  <gotchas>
  - stale-memory: Verify loaded memory vs current file state before act on it
  - dual-persistence: Check both Serena memory + auto memory for full context
  </gotchas>

  <bounds>
    <does>Serena integration, auto memory load, cross-session persist, context load.</does>
    <never>modify struct, load w/o validation, override w/o checkpoint.</never>
    <fallback>Without Serena: use Claude auto memory + Read CLAUDE.md/PLANNING.md/TASK.md, Glob for struct. Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:analyze /sc:index-repo /sc:task"/>
</component>