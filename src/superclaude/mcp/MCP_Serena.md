<component name="serena" type="mcp">
  <role>
    <mission>Semantic code understanding with project memory and session persistence</mission>
  </role>

  <initialization note="Required sequence on first use">
    1. `initial_instructions` — loads Serena operating manual (only needed in non-system-prompt contexts)
    2. `check_onboarding_performed` — verifies project is set up
    3. `activate_project` — activates the project by name or path
    If onboarding not performed: call `onboarding` before `activate_project`
  </initialization>

  <tools_active note="20 tools active in claude-code context">
    **Symbol Operations (7):**
    - `find_symbol` — search by name path pattern (supports substring, depth, kind filtering)
    - `find_referencing_symbols` — find all references to a symbol
    - `get_symbols_overview` — high-level file symbol map (call first for new files)
    - `replace_symbol_body` — replace entire symbol definition
    - `insert_after_symbol` — insert code after a symbol
    - `insert_before_symbol` — insert code before a symbol
    - `rename_symbol` — rename across entire codebase

    **Memory (5):**
    - `write_memory` — persist named memory (md format, project-scoped)
    - `read_memory` — retrieve a named memory
    - `list_memories` — list all available memories
    - `delete_memory` — remove a memory
    - `edit_memory` — regex/literal replace within a memory

    **Search and Navigation (3):**
    - `search_for_pattern` — regex search with context lines, glob filtering
    - `list_dir` — directory listing (recursive optional)
    - `find_file` — find files by mask

    **Project Management (5):**
    - `activate_project` — activate project by name/path
    - `check_onboarding_performed` — check setup status
    - `onboarding` — run initial project setup
    - `initial_instructions` — load operating manual
    - `get_current_config` — show active config, tools, modes
  </tools_active>

  <tools_thinking note="5 tools — available in Serena but restricted by claude-code context">
    - `think_about_collected_information` — assess completeness of gathered info
    - `think_about_task_adherence` — check goal alignment and detect deviation
    - `think_about_whether_you_are_done` — evaluate completion criteria
    - `summarize_changes` — document changes made in session
    - `prepare_for_new_conversation` — prepare context for session handoff

    **Status:** These tools exist in Serena but are NOT active in the `claude-code` context.
    The `included_optional_tools` setting in `.serena/project.yml` does not override context-level
    restrictions in Serena 0.1.4. When commands reference these tools (reflect.md, save.md),
    use native reasoning as a fallback.

    Future: May become available if Serena adds context-override support or a dedicated mode.
  </tools_thinking>

  <choose note="Decision matrix: Serena vs native tools">
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
    - Bulk pattern replacements: Morphllm (--morph flag)
    - File reading: Read tool (when you need full file, not symbols)

    **Decision rule:** If the operation is about _what the code means_ (symbols, references, types), use Serena. If it's about _what the text says_ (patterns, strings), use native tools.
  </choose>

  <memory_patterns note="Cross-session persistence via Serena memory">
    **Session start (/sc:load):**
    `activate_project` → `list_memories` → `read_memory("pm_context")` → report context

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
  </memory_patterns>

  <configuration>
    **Project config:** `.serena/project.yml`
    - `languages:` — LSP language servers to start
    - `included_optional_tools:` — enable thinking/context tools
    - `excluded_tools:` — disable specific tools
    - `encoding:` — text file encoding (default: utf-8)
    - `ignore_all_files_in_gitignore:` — respect .gitignore

    **Install:** `uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context claude-code --enable-web-dashboard false --enable-gui-log-window false`
  </configuration>

  <examples>
| Input | Tool | Reason |
|-------|------|--------|
| rename getUserData everywhere | `rename_symbol` | Semantic rename with reference tracking |
| find all class references | `find_referencing_symbols` | LSP-powered reference discovery |
| understand UserService class | `get_symbols_overview` → `find_symbol` (depth=1) | Token-efficient exploration |
| load project context | `activate_project` → `list_memories` | Session initialization |
| save work session | `write_memory` | Cross-session persistence |
| check if task is complete | `think_about_whether_you_are_done` | Structured completion assessment |
| update console.log to logger | Morphllm (not Serena) | Pattern-based bulk replacement |
  </examples>

</component>
