<component name="morphllm" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>pattern|bulk|edit|transform|style|framework|text-replacement|morphllm</triggers>

  <role>
    <mission>Pattern-based code editing engine with token optimization for bulk transformations</mission>
  </role>

  <choose>
Use:
- Pattern-based edits: For bulk ops, not symbol ops (use Serena)
- Bulk operations: Style enforcement, framework updates, text replacements
- Token efficiency: Fast Apply with compression (30-50% gains)
- Moderate complexity: <10 files, straightforward transformations

Avoid:
- Semantic operations: Symbol renames, dependency tracking, LSP
  </choose>

  <synergy>
- Serena: Serena analyzes semantic → Morphllm executes edits
- Sequential: Sequential plans strategy → Morphllm applies changes
  </synergy>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| update React class to hooks | Morphllm | pattern transformation |
| enforce ESLint rules | Morphllm | style guide application |
| replace console.log with logger | Morphllm | bulk text replacement |
| rename getUserData everywhere | Serena | symbol operation |
| analyze code architecture | Sequential | complex analysis |
  </examples>
</component>
