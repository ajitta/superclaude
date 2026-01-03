---
description: Generate structured implementation workflows from PRDs and feature requirements
---
<component name="workflow" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5"/>

  <role>
    /sc:workflow
    <mission>Generate structured implementation workflows from PRDs and feature requirements</mission>
  </role>

  <syntax>/sc:workflow [prd-file|feature] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]</syntax>

  <triggers>
    - PRD + spec analysis
    - Implementation workflow generation
    - Multi-persona coordination
    - Cross-session workflow management
  </triggers>

  <flow>
    1. Analyze: Parse PRD + understand requirements
    2. Plan: Workflow structure + dependency mapping
    3. Coordinate: Multi-persona + domain expertise
    4. Execute: Step-by-step workflows + task coordination
    5. Validate: Quality gates + workflow completeness
  </flow>

  <outputs note="Per execution">
| Artifact | Purpose |
|----------|---------|
| WORKFLOW.md | Implementation workflow document |
| TodoWrite items | Task tracking hierarchy |
| WORKFLOW_STATUS.md | Progress + quality gates |
  </outputs>

  <checklist note="MUST complete all">
    - [ ] PRD/requirements fully parsed
    - [ ] Workflow document generated
    - [ ] Dependencies mapped in TodoWrite
    - [ ] Quality gates defined and tracked
  </checklist>

  <mcp servers="seq:analysis|c7:patterns|magic:UI|play:testing|morph:transform|serena:persistence"/>
  <personas p="arch|anal|fe|be|sec|ops|pm"/>

  <tools>
    - Read/Write/Edit: PRD analysis + workflow docs
    - TodoWrite: Multi-phase progress tracking
    - Task: Parallel workflow + multi-agent
    - WebSearch: Tech research + framework validation
    - sequentialthinking: Dependency analysis
  </tools>

  <patterns>
    - PRD: Document parsing → requirement extraction → strategy
    - Generation: Task decomposition → dependency → planning
    - Multi-Domain: Cross-functional → comprehensive strategies
    - Quality: Validation → testing → deployment planning
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `Claudedocs/PRD/feature.md --strategy systematic --depth deep` | Comprehensive PRD workflow |
| `'user auth system' --strategy agile --parallel` | Agile + parallel coordination |
| `enterprise-prd.md --strategy enterprise --validate` | Enterprise + compliance |
| `project-brief.md --depth normal` | Cross-session with Serena |

  </examples>

  <bounds will="comprehensive workflows|multi-persona+MCP|cross-session management" wont="execute impl beyond planning|override dev process|generate without analysis"/>
</component>
