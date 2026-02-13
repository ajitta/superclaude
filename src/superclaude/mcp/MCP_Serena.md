<component name="serena" type="mcp">
  <triggers>symbol|rename|extract|move|LSP|session|memory|/sc:load|/sc:save|serena</triggers>

  <role>
    <mission>Semantic code understanding with project memory and session persistence</mission>
  </role>

  <choose>
Use:
- Symbol operations: For semantic ops, not pattern-based (use Morphllm)
- Semantic understanding: Symbol refs, dependency tracking, LSP
- Session persistence: Project context, memory, cross-session learning
- Large projects: Multi-language, architectural understanding

Avoid:
- Simple edits: Basic text replacements, style, bulk ops
  </choose>


  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| rename getUserData everywhere | Serena | symbol op with dependency tracking |
| find all class references | Serena | semantic search |
| load project context | Serena | /sc:load with project activation |
| save work session | Serena | /sc:save with memory persistence |
| update console.log to logger | Morphllm | pattern-based replacement |
  </examples>

</component>
