---
description: Generate comprehensive project documentation and knowledge base with intelligent organization
---
<component name="index" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:index
    <mission>Generate comprehensive project documentation and knowledge base with intelligent organization</mission>
  </role>

  <syntax>/sc:index [target] [--type docs|api|structure|readme] [--format md|json|yaml]</syntax>

  <triggers>
    - Project documentation creation
    - Knowledge base generation
    - API documentation needs
    - Cross-referencing requirements
  </triggers>

  <flow>
    1. **Analyze**: Project structure + key components
    2. **Organize**: Intelligent patterns + cross-refs
    3. **Generate**: Comprehensive docs + framework patterns
    4. **Validate**: Completeness + quality standards
    5. **Maintain**: Update while preserving manual additions
  </flow>

  <mcp servers="seq:analysis|c7:patterns"/>
  <personas p="arch|scribe|qual"/>

  <tools>
    - **Read/Grep/Glob**: Structure analysis + content extraction
    - **Write**: Doc creation + cross-referencing
    - **TodoWrite**: Multi-component progress
    - **Task**: Large-scale doc delegation
  </tools>

  <patterns>
    - **Structure**: Examination → component ID → organization → cross-refs
    - **Types**: API docs | Structure docs | README | Knowledge base
    - **Quality**: Completeness → accuracy → compliance → maintenance
    - **Framework**: C7 patterns → official standards → best practices
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `project-root --type structure --format md` | Navigable structure docs |
| `src/api --type api --format json` | API docs + validation |
| `. --type docs` | Knowledge base creation |

  </examples>

  <bounds will="comprehensive docs|multi-persona|framework patterns" wont="override manual docs|generate without analysis|bypass standards"/>
</component>
