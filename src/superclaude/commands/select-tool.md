---
description: Intelligent MCP tool selection based on complexity scoring and operation analysis. Use ONLY when user explicitly types `/sc:select-tool` — meta-utility for analyzing which MCP fits given operation. Do NOT auto-trigger during normal tool selection — pick appropriate MCP directly from context.
---
<component name="select-tool" type="command">

  <role command="/sc:select-tool">
    <mission>Intelligent MCP tool selection via complexity scoring + operation analysis</mission>
  </role>

  <syntax>/sc:select-tool [operation] [--analyze] [--explain]</syntax>

  <flow>
  1. Parse: op type + scope + file count
  2. Score: multi-dim complexity
  3. Match: requirements vs capabilities
  4. Select: optimal tool via scoring matrix
  5. Validate: accuracy + confidence
  </flow>

  <flags>
  - --analyze: show the complexity score and the decision-matrix rule that picked the tool.
  - --explain: explain the choice in plain terms, including why the runner-up loses.
  </flags>


  <decision_matrix>
    - Symbol ops: symbol-aware MCP when connected (LSP rename, references)
    - Pattern edits: Edit (native) after Grep or a reference query confirms targets
    - Memory ops: /sc:save, /sc:load (`.claude/memories/` + auto memory)
    - Threshold >0.6: symbol-aware MCP when connected (accuracy)
    - Threshold <0.4: Native tools (speed)
    - Threshold 0.4-0.6: Feature-based selection
    - Fallback: no symbol-aware tool → Native tools (Grep/Glob/Edit)
  </decision_matrix>

  <examples>

| Input | Output |
|---|---|
| `'rename function across 10 files' --analyze` | Symbol-aware MCP (LSP rename) when connected |
| `'update console.log to logger.info' --explain` | Grep targets + Edit (text replace) |
| `'save project context'` | /sc:save (memory folder) |

  <example name="wrong-tool-choice" type="error-path">
    - Input: /sc:select-tool 'rename a variable across the project' → suggests Grep + Edit
    - Why wrong: Variable rename = semantic op. Plain text replace risks aliasing matches in strings/comments.
    - Correct: symbol-aware rename (LSP) when connected; otherwise Grep every occurrence and review each before Edit; reserve plain Grep+Edit for unambiguous text patterns.
  </example>
  </examples>


  <gotchas>
  - native-first: Recommend native tools (Grep, Glob, Read) before MCP for simple ops
  - mcp-justify: Recommend MCP only when native insufficient. State why
  </gotchas>

  <bounds>
    <does>optimal selection, complexity scoring.</does>
    <never>override explicit preference, skip analysis, compromise performance.</never>
  </bounds>

  <handoff next="/sc:implement /sc:analyze"/>
</component>