<component name="serena" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>symbol|rename|extract|move|LSP|session|memory|/sc:load|/sc:save|serena</triggers>

  <role>
    <mission>Semantic code understanding with project memory and session persistence</mission>
  </role>

  <choose>
**Use for:**
- Symbol operations: For semantic ops, not pattern-based (use Morphllm)
- Semantic understanding: Symbol refs, dependency tracking, LSP
- Session persistence: Project context, memory, cross-session learning
- Large projects: Multi-language, architectural understanding

**Avoid for:**
- Simple edits: Basic text replacements, style, bulk ops
  </choose>

  <synergy>
- **Morphllm**: Serena analyzes semantic → Morphllm executes edits
- **Sequential**: Serena provides context → Sequential does architectural analysis
  </synergy>

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
