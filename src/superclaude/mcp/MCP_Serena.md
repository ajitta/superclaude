<component name="serena" type="mcp">
  <role>
    <mission>Semantic code understanding with project memory and session persistence</mission>
  </role>

  Project auto-activates from CWD. Recovery: call `initial_instructions` if the agent forgets the manual; `check_onboarding_performed` / `onboarding` if setup is unverified.

  ## Fallback for context-disabled tools
  Some upstream Serena tools are not exposed in the `claude-code` context. Use the native fallback:

  | Removed Serena tool | Native fallback | When to use |
  |---|---|---|
  | `activate_project` | (automatic via `--project-from-cwd`) | No action needed; verify with `check_onboarding_performed` if uncertain |
  | `search_for_pattern` | native `Grep` | Regex/text search; same capability, no LSP overhead |
  | `list_dir` / `find_file` | native `Glob` | Directory listing and filename pattern matching |

  Thinking tools (`think_about_*`, `summarize_changes`, `prepare_for_new_conversation`) and JetBrains-only refactoring tools are not active in the `claude-code` context — use native reasoning when commands reference them.

  <choose>
    **Use Serena for:**
    - Symbol operations: rename, find references, extract, move (semantic precision)
    - Cross-file refactoring: rename propagates through all references
    - Code understanding: symbol overview before reading full files
    - Session persistence: write_memory/read_memory for cross-session context
    - Reflection: think_about_* tools for structured self-assessment
    - Large projects: multi-language LSP-powered navigation

    **Use native tools instead for:**
    - Simple text edits: Edit tool (pattern-based, no LSP needed)
    - File search by name: Glob (faster for simple patterns)
    - Content search: Grep (faster for text patterns)
    - Bulk pattern replacements: Grep + Edit (native)
    - File reading: Read tool (when you need full file, not symbols)

    **Decision rule:** If the operation is about _what the code means_ (symbols, references, types), use Serena. If it's about _what the text says_ (patterns, strings), use native tools.
  </choose>

  ## Memory Patterns
    **Session start (/sc:load):**
    `list_memories` → `read_memory("pm_context")` → report context (project auto-active via `--project-from-cwd`)

    **During work:**
    `think_about_task_adherence` for goal alignment checks
    `write_memory` for checkpoints and discoveries

    **Session end (/sc:save):**
    `write_memory("session_[date]", ...)` → `write_memory("learnings_[topic]", ...)` → verify with `list_memories`

    **Memory naming conventions:**
    - `pm_context` — PM agent state
    - `last_session` — previous session summary
    - `next_actions` — queued work items
    - `session_[YYYY-MM-DD]` — dated session snapshots
    - `learnings_[topic]` — accumulated insights by topic

  <examples>
| Input | Tool | Reason |
|---|---|---|
| rename getUserData everywhere | `rename_symbol` | Semantic rename with reference tracking |
| find all class references | `find_referencing_symbols` | LSP-powered reference discovery |
| understand UserService class | `get_symbols_overview` → `find_symbol` (depth=1) | Token-efficient exploration |
| load project context | `list_memories` → `read_memory` | Project auto-active; just read memory |
| save work session | `write_memory` | Cross-session persistence |
| check if task is complete | `think_about_whether_you_are_done` | Structured completion assessment |
| update console.log to logger | Grep + Edit (not Serena) | Text pattern bulk replacement |
  </examples>

  <bounds>
    <should>semantic code understanding, symbol operations, and cross-session memory.</should>
    <avoid>simple text edits, bulk pattern replacement, and file-level operations.</avoid>
    <fallback>Use native Grep/Glob/Edit for text-level operations.</fallback>
  </bounds>

  <handoff next="/sc:reflect /sc:save /sc:load"/>
</component>
