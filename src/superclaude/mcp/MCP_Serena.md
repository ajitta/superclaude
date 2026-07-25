<component name="serena" type="mcp">
  <role>
    <mission>Semantic code understanding w/ project memory + session persistence</mission>
  </role>

  <recovery>
  Project auto-activate from CWD. Recovery: call `initial_instructions` if agent forget manual; `onboarding` if setup unverified.
  </recovery>

  <fallback_tools>
  Some upstream Serena tools not exposed in `claude-code` context. Use native fallback:

  | Removed Serena tool | Native fallback | When to use |
  |---|---|---|
  | `activate_project` | (automatic via `--project-from-cwd`) | No action needed; verify w/ `onboarding` if uncertain |
  | `search_for_pattern` | native `Grep` | Regex/text search; same capability, no LSP overhead |
  | `list_dir` / `find_file` | native `Glob` | Directory listing + filename pattern matching |

  Thinking tools (`think_about_*`, `summarize_changes`, `prepare_for_new_conversation`) + JetBrains-only refactor tools not active in `claude-code` context — use native reasoning when commands reference them.
  </fallback_tools>

  <choose>
  Decision rule — if op about what code _means_ (symbols, refs, types), Serena; if about what text _says_ (patterns, strings), native tools.

  <use>symbol-level ops (rename, find refs, extract, move), cross-file semantic refactor where renames propagate through all refs, structural code understanding via symbol overview before reading full files, cross-session persistence through `write_memory` / `read_memory`, LSP-powered nav in large multi-language projects.</use>
  <never>simple text edits, filename/content pattern search, bulk find-and-replace, whole-file reading — those go through native `Edit`, `Glob`, `Grep`, `Read` for lower overhead.</never>
  </choose>

  <memory_patterns>
  Session lifecycle flows and memory key names live in `/sc:load` and `/sc:save` — not restated here. During work: native reasoning for goal-alignment checks; `write_memory` for checkpoints + discoveries as they surface.
  </memory_patterns>

  <examples>
  | Input | Tool | Reason |
  |---|---|---|
  | rename getUserData everywhere | `rename_symbol` | Semantic rename w/ reference tracking |
  | find all class references | `find_referencing_symbols` | LSP-powered reference discovery |
  | understand UserService class | `get_symbols_overview` → `find_symbol` (depth=1) | Token-efficient exploration |
  | load project context | `list_memories` → `read_memory` | Project auto-active; just read memory |
  | save work session | `write_memory` | Cross-session persistence |
  | check if task is complete | native reasoning (not Serena) | `think_about_*` tools not active in `claude-code` |
  | update console.log to logger | `Grep` + `Edit` (not Serena) | Text pattern bulk replacement |
  </examples>

  <bounds>
    <does>semantic code understanding, symbol ops, cross-session memory.</does>
    <never>simple text edits, bulk pattern replacement, file-level ops.</never>
    <fallback>Use native `Grep` / `Glob` / `Edit` for text-level ops.</fallback>
  </bounds>

  <handoff next="/sc:reflect /sc:save /sc:load"/>
</component>