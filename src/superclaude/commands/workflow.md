---
description: Generate structured implementation workflows from PRDs and feature requirements
---
<component name="workflow" type="command">

  <role command="/sc:workflow">
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
|---|---|
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
|---|---|
| `Claudedocs/PRD/feature.md --strategy systematic --depth deep` | Comprehensive PRD workflow |
| `'user auth system' --strategy agile --parallel` | Agile + parallel coordination |
| `enterprise-prd.md --strategy enterprise --depth deep` | Enterprise + compliance |
| `project-brief.md --depth normal` | Cross-session with Serena |

  <example name="workflow-no-prd" type="error-path">
    - Input: /sc:workflow --strategy enterprise --parallel (with no PRD or feature doc)
    - Why wrong: Workflow generation requires a PRD or feature document as input. No input means no tasks to generate.
    - Correct: Create a PRD first: /sc:brainstorm → /sc:design → save to file → /sc:workflow PRD.md
  </example>

  </examples>


  <gotchas>
  - scope-match: Workflow scope must match the PRD or feature request exactly
  - step-granularity: Each workflow step should be independently verifiable
  </gotchas>

  <bounds>
    <does>comprehensive workflows, multi-agent+MCP, and cross-session management.</does>
    <never>execute impl beyond planning, override dev process, and generate without analysis.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:task"/>
</component>
