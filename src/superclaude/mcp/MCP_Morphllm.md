<component name="morphllm" type="mcp">
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


  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| update React class to hooks | Morphllm | pattern transformation |
| enforce ESLint rules | Morphllm | style guide application |
| replace console.log with logger | Morphllm | bulk text replacement |
| rename getUserData everywhere | Serena | symbol operation |
| analyze code architecture | Sequential | complex analysis |
  </examples>

  <bounds will="pattern-based bulk edits|style enforcement|token-efficient transformations" wont="semantic symbol operations|dependency tracking|LSP-powered refactoring" fallback="Use Serena for symbol-level operations, Edit for single-file changes"/>

  <handoff next="/sc:improve /sc:cleanup"/>
</component>
