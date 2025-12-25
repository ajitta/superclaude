<component name="morphllm" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>pattern|bulk|edit|transform|style|framework|text-replacement|morphllm</triggers>

  <role>
    <mission>Pattern-based code editing engine with token optimization for bulk transformations</mission>
  </role>

  <choose>
    <use context="pattern-based edits">For bulk ops, not symbol ops (use Serena)</use>
    <use context="bulk operations">Style enforcement, framework updates, text replacements</use>
    <use context="token efficiency">Fast Apply with compression (30-50% gains)</use>
    <use context="moderate complexity">&lt;10 files, straightforward transformations</use>
    <avoid context="semantic operations">Symbol renames, dependency tracking, LSP</avoid>
  </choose>

  <synergy>
    <with n="Serena">Serena analyzes semantic → Morphllm executes edits</with>
    <with n="Sequential">Sequential plans strategy → Morphllm applies changes</with>
  </synergy>

  <examples>
    <ex i="update React class to hooks" o="Morphllm" r="pattern transformation"/>
    <ex i="enforce ESLint rules" o="Morphllm" r="style guide application"/>
    <ex i="replace console.log with logger" o="Morphllm" r="bulk text replacement"/>
    <ex i="rename getUserData everywhere" o="Serena" r="symbol operation"/>
    <ex i="analyze code architecture" o="Sequential" r="complex analysis"/>
  </examples>
</component>
