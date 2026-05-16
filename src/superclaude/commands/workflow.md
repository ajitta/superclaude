---
description: Generate structured implementation workflows from PRDs and feature requirements. Use when user types `/sc:workflow` or hands over PRD/feature doc and asks for task breakdown to commit under docs/plans/. Do NOT auto-trigger on "what's the order of steps" or short ad-hoc task lists — those get inline 2-3 step answer, not workflow file.
---
<component name="workflow" type="command">

  <role command="/sc:workflow">
    <mission>Generate structured implementation workflows from PRDs + feature requirements</mission>
  </role>

  <syntax>/sc:workflow [prd-file|feature] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--delegate]</syntax>

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
| `docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md` | Implementation workflow doc (with Status section) |
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
| `'user auth system' --strategy agile --delegate` | Agile + parallel coordination |
| `enterprise-prd.md --strategy enterprise --depth deep` | Enterprise + compliance |
| `project-brief.md --depth normal` | Cross-session with Serena |

  <example name="workflow-no-prd" type="error-path">
    - Input: /sc:workflow --strategy enterprise --delegate (no PRD or feature doc)
    - Why wrong: Workflow generation needs PRD or feature doc as input. No input = no tasks to generate.
    - Correct: Make PRD first: /sc:brainstorm → /sc:design → save to file → /sc:workflow PRD.md
  </example>

  </examples>


  <gotchas>
  - scope-match: Workflow scope must match PRD or feature request exactly
  - step-granularity: Each workflow step independently verifiable
  </gotchas>

  <bounds>
    <does>comprehensive workflows, multi-agent+MCP, cross-session management.</does>
    <never>execute impl beyond planning, override dev process, generate without analysis.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:task"/>
</component>