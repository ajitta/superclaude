<component name="serena" type="mcp">
  <role>
    <mission>Semantic code understanding with project memory and session persistence</mission>
  </role>

  ## Initialization
  Project auto-activates from CWD via `--project-from-cwd`. Onboarding runs automatically on first project use.

  Recovery actions (only when needed):
  - If the agent ignores Serena tools or appears to have forgotten the manual: call `initial_instructions` once. (Permanent fix: install Serena's SessionStart hook — see "Optional: Serena hooks" below.)
  - To verify project setup: `check_onboarding_performed`.
  - If onboarding hasn't run: `onboarding`.

  <tools note="17 tools active in claude-code context">
    **Symbol Operations (8):**
    - `find_symbol` — search by name path pattern (supports substring, depth, kind filtering)
    - `find_referencing_symbols` — find all references to a symbol
    - `get_symbols_overview` — high-level file symbol map (call first for new files)
    - `replace_symbol_body` — replace entire symbol definition
    - `insert_after_symbol` — insert code after a symbol
    - `insert_before_symbol` — insert code before a symbol
    - `rename_symbol` — rename across entire codebase
    - `safe_delete_symbol` — remove symbol with unused code propagation

    **Memory (6):**
    - `write_memory` — persist named memory (md format, project-scoped)
    - `read_memory` — retrieve a named memory
    - `list_memories` — list all available memories
    - `delete_memory` — remove a memory
    - `edit_memory` — regex/literal replace within a memory
    - `rename_memory` — rename existing memory

    **Project Management (3):**
    - `check_onboarding_performed` — check setup status
    - `onboarding` — run initial project setup
    - `initial_instructions` — load operating manual
  </tools>

  ## Fallback for context-disabled tools
  These tools exist in upstream Serena but are not exposed in the claude-code context (per upstream README §How Serena Works). Use the native fallback when you would have reached for one.

  | Removed Serena tool | Native fallback | When to use |
  |---|---|---|
  | `activate_project` | (automatic via `--project-from-cwd`) | No action needed; verify with `check_onboarding_performed` if uncertain |
  | `get_current_config` | (none — MCP itself reports tools at startup) | Use `claude mcp list` from shell when you need to verify |
  | `search_for_pattern` | native `Grep` | Regex/text search; same capability, no LSP overhead |
  | `list_dir` | native `Glob` (e.g., `**/*.py`) | Directory listing and file discovery |
  | `find_file` | native `Glob` | Filename pattern matching |

  ## Thinking Tools (restricted in claude-code context)
    - `think_about_collected_information` — assess completeness of gathered info
    - `think_about_task_adherence` — check goal alignment and detect deviation
    - `think_about_whether_you_are_done` — evaluate completion criteria
    - `summarize_changes` — document changes made in session
    - `prepare_for_new_conversation` — prepare context for session handoff

    **Status:** These tools exist in Serena but are NOT active in the `claude-code` context.
    The `included_optional_tools` setting in `.serena/project.yml` does not override context-level
    restrictions. When commands reference these tools (reflect.md, save.md),
    use native reasoning as a fallback.

    **Note:** Serena also has JetBrains Plugin support with additional refactoring capabilities
    (move, inline, propagate deletions, type hierarchy, find implementations).
    These are available in the `ide-assistant` context, not `claude-code`.

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
    - Bulk pattern replacements: ast-grep + Edit (native)
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

  ## Configuration
    **Project config:** `.serena/project.yml`
    - `languages:` — LSP language servers to start
    - `included_optional_tools:` — enable thinking/context tools
    - `excluded_tools:` — disable specific tools
    - `encoding:` — text file encoding (default: utf-8)
    - `ignore_all_files_in_gitignore:` — respect .gitignore

    **Install:** `claude mcp add --scope user serena -- serena start-mcp-server --context=claude-code --project-from-cwd`
    (Equivalent shorthand: `serena setup claude-code`. Already installed via old command? `claude mcp remove serena` first, then re-run.)

    **Scope choice** — `superclaude install` accepts `--scope user|project|local`. Upstream `serena setup claude-code` hardcodes `--scope user`; SC defaults to the same. Trade-offs:

    | Scope | Stored in | Effect with `--project-from-cwd` |
    |---|---|---|
    | `user` (recommended) | `~/.claude.json` | One registration; auto-detects project per CWD at launch. |
    | `project` | `.mcp.json` (committed) | Team-shared registration; each clone needs Serena binary locally; `--project-from-cwd` is redundant per-repo but harmless. |
    | `local` | `~/.claude.json` (per-project) | Per-machine + per-repo; defeats the "register once" benefit of `--project-from-cwd`. |

    **Optional: Serena hooks (recommended by upstream)** — Counteracts agent drift (forgetting Serena's manual mid-session) and missing tool-load on session start. Add to `.claude/settings.json` (user or project scope):

    ```json
    {
      "hooks": {
        "PreToolUse": [
          { "matcher": "", "hooks": [{ "type": "command", "command": "serena-hooks remind --client=claude-code" }] },
          { "matcher": "mcp__serena__*", "hooks": [{ "type": "command", "command": "serena-hooks auto-approve --client=claude-code" }] }
        ],
        "SessionStart": [
          { "matcher": "", "hooks": [{ "type": "command", "command": "serena-hooks activate --client=claude-code" }] }
        ],
        "Stop": [
          { "matcher": "", "hooks": [{ "type": "command", "command": "serena-hooks cleanup --client=claude-code" }] }
        ]
      }
    }
    ```

    Prerequisite: `serena-hooks` binary on PATH (e.g., `uv tool install --from git+https://github.com/oraios/serena serena`). Caveat: the `mcp__serena__*` PreToolUse hook auto-approves all Serena tool calls — if you rely on permission prompts as a guardrail, drop that one entry. Source: `oraios.github.io/serena/02-usage/030_clients.html`.

  <examples>
| Input | Tool | Reason |
|-------|------|--------|
| rename getUserData everywhere | `rename_symbol` | Semantic rename with reference tracking |
| find all class references | `find_referencing_symbols` | LSP-powered reference discovery |
| understand UserService class | `get_symbols_overview` → `find_symbol` (depth=1) | Token-efficient exploration |
| load project context | `list_memories` → `read_memory` | Project auto-active; just read memory |
| save work session | `write_memory` | Cross-session persistence |
| check if task is complete | `think_about_whether_you_are_done` | Structured completion assessment |
| update console.log to logger | ast-grep + Edit (not Serena) | Pattern-based bulk replacement |
  </examples>

  <bounds should="semantic code understanding|symbol operations|cross-session memory" avoid="simple text edits|bulk pattern replacement|file-level operations" fallback="Use native Grep/Glob/Edit for text-level operations"/>

  <handoff next="/sc:reflect /sc:save /sc:load"/>
</component>
