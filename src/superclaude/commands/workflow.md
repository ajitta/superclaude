---
description: Generate structured implementation workflows from PRDs and feature requirements
---
<component name="workflow" type="command">

  <role>
    /sc:workflow
    <mission>Generate structured implementation workflows from PRDs and feature requirements</mission>
  </role>

  <syntax>/sc:workflow [prd-file|feature] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]</syntax>

  <flow>
    1. Analyze: Parse PRD + understand requirements
    2. Plan: Workflow structure + dependency mapping
    3. Coordinate: Multi-agent + domain expertise
    4. Execute: Step-by-step workflows + task coordination
    5. Validate: Quality gates + workflow completeness
  </flow>

  <outputs>
| Artifact | Purpose |
|----------|---------|
| `docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md` | Implementation workflow document (with Status section) |
| TaskCreate/TaskUpdate items | Task tracking hierarchy |
  </outputs>


  <tools>
    - Read/Write/Edit: PRD analysis + workflow docs
    - TaskCreate/TaskUpdate: Multi-phase progress tracking
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
| `enterprise-prd.md --strategy enterprise --depth deep` | Enterprise + compliance |
| `project-brief.md --depth normal` | Cross-session with Serena |

  <example name="workflow-no-prd" type="error-path">
    <input>/sc:workflow --strategy enterprise --parallel (with no PRD or feature doc)</input>
    <why_wrong>Workflow generation requires a PRD or feature document as input. No input means no tasks to generate.</why_wrong>
    <correct>Create a PRD first: /sc:brainstorm → /sc:design → save to file → /sc:workflow PRD.md</correct>
  </example>

  </examples>

  <bounds will="comprehensive workflows|multi-agent+MCP|cross-session management" wont="execute impl beyond planning|override dev process|generate without analysis" fallback="Ask user for guidance when uncertain">

    Produce workflow document, then complete | Defer implementation to /sc:implement or /sc:task | Planning and coordination only → Output: docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md with task hierarchy and quality gates

  </bounds>

  <handoff next="/sc:implement /sc:task"/>
</component>
