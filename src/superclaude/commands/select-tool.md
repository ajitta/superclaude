<component name="select-tool" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:select-tool
    <mission>Intelligent MCP tool selection based on complexity scoring and operation analysis</mission>
  </role>

  <syntax>/sc:select-tool [operation] [--analyze] [--explain]</syntax>

  <triggers>
    <t>MCP tool selection (Serena vs Morphllm)</t>
    <t>Complexity analysis needs</t>
    <t>Tool routing decisions</t>
    <t>Performance vs accuracy trade-offs</t>
  </triggers>

  <flow>
    <s n="1">Parse: Operation type + scope + file count</s>
    <s n="2">Score: Multi-dimensional complexity</s>
    <s n="3">Match: Requirements vs capabilities</s>
    <s n="4">Select: Optimal tool via scoring matrix</s>
    <s n="5">Validate: Selection accuracy + confidence</s>
  </flow>

  <mcp servers="serena:semantic|morph:pattern"/>

  <decision_matrix>
    <direct n="Symbol ops">Serena (LSP, navigation)</direct>
    <direct n="Pattern edits">Morphllm (bulk, speed)</direct>
    <direct n="Memory ops">Serena (persistence)</direct>
    <threshold n=">0.6">Serena (accuracy)</threshold>
    <threshold n="<0.4">Morphllm (speed)</threshold>
    <threshold n="0.4-0.6">Feature-based selection</threshold>
  </decision_matrix>

  <patterns>
    <p n="Serena">Semantic ops | LSP | symbol nav | project context</p>
    <p n="Morphllm">Pattern edits | bulk transforms | speed-critical</p>
    <p n="Fallback">Serena → Morphllm → Native tools</p>
  </patterns>

  <performance>
    <metric n="decision-time">&lt;100ms</metric>
    <metric n="accuracy">>95%</metric>
  </performance>

  <examples>
    <ex i="'rename function across 10 files' --analyze" o="Serena (LSP, semantic)"/>
    <ex i="'update console.log to logger.info' --explain" o="Morphllm (pattern, bulk)"/>
    <ex i="'save project context'" o="Serena (memory direct)"/>
  </examples>

  <bounds will="optimal selection|complexity scoring|sub-100ms decision" wont="override explicit preference|skip analysis|compromise performance"/>
</component>
