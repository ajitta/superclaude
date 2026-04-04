<component name="ast-grep" type="mcp">
  <role>
    <mission>Structural AST pattern search and code analysis using tree-sitter</mission>
  </role>

  ## Activation
  Not always active. When structural code pattern search is needed:
  1. Use `--sg` or `--ast-grep` flag
  2. Auto-triggers on: ast-grep, syntax tree, structural pattern/search keywords
  3. Provides 4 tools for AST-aware code search

  <choose>
  Use:
  - Structural pattern matching: find all `console.log($$$)` calls, empty catch blocks
  - Anti-pattern detection: unused imports, missing error handling, eval() usage
  - Refactoring target identification: deprecated API patterns, duplicated structures
  - Code quality audits: structural checks beyond text grep capabilities
  - Pre-transformation analysis: find patterns before bulk edits with Morphllm

  Avoid:
  - Symbol navigation: find definitions, references, types → Serena (--serena)
  - Simple text search: literal string matching → Grep
  - Single file edits: one change in one file → Edit tool
  - Runtime analysis: performance, memory profiling → DevTools (--perf)
  </choose>

  ## Decision Rule: ast-grep vs Serena vs Grep
  | Scenario | Tool | Why |
  |----------|------|-----|
  | Find all empty catch blocks | ast-grep | Structural pattern, AST-aware |
  | Find where `getUserData` is defined | Serena | Symbol navigation |
  | Find string "TODO" in comments | Grep | Simple text match |
  | Find all `eval()` calls (not in strings) | ast-grep | Needs AST context to skip strings |
  | Rename `getData` and update all callers | Serena | Symbol-aware reference tracking |
  | Find deprecated `componentWillMount` usage | ast-grep | Structural pattern across files |
  | Find files containing "error" | Grep | Simple text search |

  ## Workflow
  ```
  dump_syntax_tree → test_match_code_rule → find_code / find_code_by_rule
  (understand AST)   (validate rule)         (search at scale)
  ```
  - **dump_syntax_tree**: Visualize AST node names before writing patterns
  - **test_match_code_rule**: Test YAML rules on code snippets before codebase-wide search
  - **find_code**: Simple structural pattern search (supports `$METAVAR` and `$$$` wildcards)
  - **find_code_by_rule**: Advanced search with YAML rules (constraints, meta-variables, regex)

  ## Integration Patterns
  - **Refactoring prep**: ast-grep:find-patterns → Serena:rename-symbols → /sc:test
  - **Security audit**: ast-grep:vulnerability-patterns → /sc:review → /sc:implement fixes
  - **Code quality**: /sc:analyze → ast-grep:anti-patterns → Morphllm:bulk-fix → /sc:test
  - **Migration**: Context7:new-api-docs → ast-grep:find-old-patterns → Morphllm:transform

  <examples>
| Input | Action | Reason |
|-------|--------|--------|
| find all empty catch blocks | ast-grep: `find_code` with `catch ($) {}` | Structural pattern |
| find eval() usage for security | ast-grep: `find_code` with `eval($$$)` | AST skips strings/comments |
| find deprecated React lifecycle | ast-grep: `find_code` with `componentWillMount` | Structural class method match |
| rename getUserData everywhere | Serena: `rename_symbol` (not ast-grep) | Needs reference tracking |
| find TODO comments | Grep (not ast-grep) | Simple text match |
  </examples>

  <bounds will="structural AST search|pattern matching|anti-pattern detection|code analysis" wont="symbol navigation|reference tracking|runtime analysis|file editing" fallback="Use Serena for symbol operations, Grep for text search, Edit for modifications"/>

  <handoff next="/sc:analyze /sc:improve /sc:cleanup"/>
</component>
