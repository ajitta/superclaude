---
description: Intelligent MCP tool selection based on complexity scoring and operation analysis
---
<component name="select-tool" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5"/>

  <role>
    /sc:select-tool
    <mission>Intelligent MCP tool selection based on complexity scoring and operation analysis</mission>
  </role>

  <syntax>/sc:select-tool [operation] [--analyze] [--explain]</syntax>

  <triggers>
    - MCP tool selection (Serena vs Morphllm)
    - Complexity analysis needs
    - Tool routing decisions
    - Performance vs accuracy trade-offs
  </triggers>

  <flow>
    1. Parse: Operation type + scope + file count
    2. Score: Multi-dimensional complexity
    3. Match: Requirements vs capabilities
    4. Select: Optimal tool via scoring matrix
    5. Validate: Selection accuracy + confidence
  </flow>

  <mcp servers="serena:semantic|morph:pattern"/>

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

  </examples>

  <bounds will="optimal selection|complexity scoring|sub-100ms decision" wont="override explicit preference|skip analysis|compromise performance"/>
</component>
