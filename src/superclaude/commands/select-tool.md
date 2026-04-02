---
description: Intelligent MCP tool selection based on complexity scoring and operation analysis
---
<component name="select-tool" type="command">

  <role>
    /sc:select-tool
    <mission>Intelligent MCP tool selection based on complexity scoring and operation analysis</mission>
  </role>

  <syntax>/sc:select-tool [operation] [--analyze] [--explain]</syntax>

  <flow>
    1. Parse: Operation type + scope + file count
    2. Score: Multi-dimensional complexity
    3. Match: Requirements vs capabilities
    4. Select: Optimal tool via scoring matrix
    5. Validate: Selection accuracy + confidence
  </flow>


  <decision_matrix>
    - Symbol ops: Serena (LSP, navigation)
    - Pattern edits: Morphllm (bulk, speed)
    - Memory ops: Serena (persistence)
    - Threshold >0.6: Serena (accuracy)
    - Threshold <0.4: Morphllm (speed)
    - Threshold 0.4-0.6: Feature-based selection
  </decision_matrix>

  <patterns>
    - Serena: Semantic ops | LSP | symbol nav | project context
    - Morphllm: Pattern edits | bulk transforms | speed-critical
    - Fallback: Serena → Morphllm → Native tools
  </patterns>

  <performance>
    - decision-time: <100ms
    - accuracy: >95%
  </performance>

  <examples>

| Input | Output |
|-------|--------|
| `'rename function across 10 files' --analyze` | Serena (LSP, semantic) |
| `'update console.log to logger.info' --explain` | Morphllm (pattern, bulk) |
| `'save project context'` | Serena (memory direct) |

  <example name="wrong-tool-choice" type="error-path">
    <input>/sc:select-tool 'rename a variable across the project' → suggests Morphllm</input>
    <why_wrong>Variable renaming is a semantic operation. Morphllm does text patterns, not semantic renames.</why_wrong>
    <correct>Serena (LSP-based rename) for semantic operations. Morphllm for text-pattern transformations only.</correct>
  </example>
  </examples>

  <bounds will="optimal selection|complexity scoring|sub-100ms decision" wont="override explicit preference|skip analysis|compromise performance" fallback="Ask user for guidance when uncertain" type="document-only">

    Provide tool selection recommendation, then complete | Do not execute the selected tool automatically | Defer execution to the user or calling command → Output: Tool recommendation with scoring rationale

  </bounds>

  <handoff next="/sc:implement /sc:analyze"/>
</component>
