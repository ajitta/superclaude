<component name="serena" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>symbol|rename|extract|move|LSP|session|memory|/sc:load|/sc:save|serena</triggers>

  <role>
    <mission>Semantic code understanding with project memory and session persistence</mission>
  </role>

  <choose>
    <use context="symbol operations">For semantic ops, not pattern-based (use Morphllm)</use>
    <use context="semantic understanding">Symbol refs, dependency tracking, LSP</use>
    <use context="session persistence">Project context, memory, cross-session learning</use>
    <use context="large projects">Multi-language, architectural understanding</use>
    <avoid context="simple edits">Basic text replacements, style, bulk ops</avoid>
  </choose>

  <synergy>
    <with n="Morphllm">Serena analyzes semantic → Morphllm executes edits</with>
    <with n="Sequential">Serena provides context → Sequential does architectural analysis</with>
  </synergy>

  <examples>
    <ex i="rename getUserData everywhere" o="Serena" r="symbol op with dependency tracking"/>
    <ex i="find all class references" o="Serena" r="semantic search"/>
    <ex i="load project context" o="Serena" r="/sc:load with project activation"/>
    <ex i="save work session" o="Serena" r="/sc:save with memory persistence"/>
    <ex i="update console.log to logger" o="Morphllm" r="pattern-based replacement"/>
  </examples>
</component>
