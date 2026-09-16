<component name="serena" type="mcp">
  <role>
    <mission>Semantic code understanding with project memory + session persistence</mission>
  </role>

  <recovery>
  Project auto-activate from CWD. Recovery: call `initial_instructions` if agent forget manual; `onboarding` only when `list_memories` returns none (it performs onboarding, not a check).
  </recovery>

  <fallback_tools>
  Some upstream Serena tools not exposed in `claude-code` context. Use native fallback:

  | Removed Serena tool | Native fallback | When to use |
  |---|---|---|
  | `activate_project` | (automatic via `--project-from-cwd`) | No action needed |
  | `search_for_pattern` | native `Grep` | Regex/text search; same capability, no LSP overhead |
  | `list_dir` / `find_file` | native `Glob` | Directory listing + filename pattern matching |

  The thinking tools (`think_about_*`, `summarize_changes`, `prepare_for_new_conversation`) were removed upstream — use native reasoning when older commands reference them. `jet_brains_*` refactor tools are optional and off by default (JetBrains backend only).
  </fallback_tools>

  <choose>
  Decision rule — if op about what code _means_ (symbols, refs, types), Serena; if about what text _says_ (patterns, strings), native tools.

  <use>symbol-level ops (rename, find refs, declaration, implementations, safe delete), cross-file semantic refactor where renames propagate through all refs, structural code understanding via symbol overview before reading full files, post-edit verification with `get_diagnostics_for_file`, cross-session persistence through `write_memory` / `read_memory`, LSP-powered nav in large multi-language projects.</use>
  <never>simple text edits, filename/content pattern search, whole-file reading — those go through native `Edit`, `Glob`, `Grep`, `Read` for lower overhead. Bulk find-and-replace is native `Grep` + `Edit` by default; `replace_in_files` is the Serena route when a dry-run preview with per-occurrence selection is wanted.</never>
  </choose>

  <memory_patterns>
  Session lifecycle flows and memory key names live in `/sc:load` and `/sc:save` — not restated here. During work: native reasoning for goal-alignment checks; `write_memory` for checkpoints + discoveries as they surface.
  </memory_patterns>

  <examples>
  | Input | Tool | Reason |
  |---|---|---|
  | rename getUserData everywhere | `rename_symbol` | Semantic rename with reference tracking |
  | find all class references | `find_referencing_symbols` | LSP-powered reference discovery |
  | understand UserService class | `get_symbols_overview` → `find_symbol` (depth=1) | Token-efficient exploration |
  | jump to where a type is defined | `find_declaration` / `find_implementations` | LSP definition + implementors, no grep guessing |
  | confirm an edit compiles | `get_diagnostics_for_file` | LSP errors/warnings for the touched file, no build run |
  | load project context | `list_memories` → `read_memory` | Project auto-active; just read memory |
  | save work session | `write_memory` | Cross-session persistence |
  | check if task is complete | native reasoning (not Serena) | `think_about_*` tools removed upstream |
  | update console.log to logger | `Grep` + `Edit` (not Serena) | Text pattern bulk replacement |
  </examples>

  <bounds>
    <does>semantic code understanding, symbol ops, cross-session memory.</does>
    <never>simple text edits, bulk pattern replacement, file-level ops.</never>
    <fallback>Use native `Grep` / `Glob` / `Edit` for text-level ops.</fallback>
  </bounds>

  <handoff next="/sc:reflect /sc:save /sc:load"/>
</component>