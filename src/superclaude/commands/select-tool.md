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


  <decision_matrix>
    - Symbol ops: Serena (LSP, navigation)
    - Pattern edits: Edit (native) after Grep/Serena confirms targets
    - Memory ops: Serena (persistence)
    - Threshold >0.6: Serena (accuracy)
    - Threshold <0.4: Native tools (speed)
    - Threshold 0.4-0.6: Feature-based selection
  </decision_matrix>

  <patterns>
    - Serena: Semantic ops | LSP | symbol nav | project context
    - Fallback: Serena → Native tools (Grep/Glob/Edit)
  </patterns>

  <performance>
    - decision-time: <100ms
    - accuracy: >95%
  </performance>

  <examples>

| Input | Output |
|---|---|
| `'rename function across 10 files' --analyze` | Serena (LSP, semantic) |
| `'update console.log to logger.info' --explain` | Grep targets + Edit (text replace) |
| `'save project context'` | Serena (memory direct) |

  <example name="wrong-tool-choice" type="error-path">
    - Input: /sc:select-tool 'rename a variable across the project' → suggests Grep + Edit
    - Why wrong: Variable rename = semantic op. Plain text replace risks aliasing matches in strings/comments.
    - Correct: Serena (LSP rename) for semantic ops; reserve Grep+Edit for unambiguous text patterns.
  </example>
  </examples>


  <gotchas>
  - native-first: Recommend native tools (Grep, Glob, Read) before MCP for simple ops
  - mcp-justify: Recommend MCP only when native insufficient. State why
  </gotchas>

  <bounds>
    <does>optimal selection, complexity scoring, sub-100ms decision.</does>
    <never>override explicit preference, skip analysis, compromise performance.</never>
    <fallback>Ask user when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:analyze"/>
</component>