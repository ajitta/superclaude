---
description: Generate structured implementation workflows from PRDs and feature requirements. Use ONLY when user explicitly types `/sc:roadmap` — commits a phased workflow file, so a wrong fire skips the approval gate and creates files unasked. For a TDD implementation plan with exact file paths from a spec, use /sc:plan. Do NOT auto-trigger on "what's the order of steps" or short ad-hoc task lists — those get inline 2-3 step answer, not workflow file.
---
<component name="roadmap" type="command">

  <role command="/sc:roadmap">
    <mission>Generate structured implementation workflows from PRDs + feature requirements</mission>
  </role>

  <syntax>/sc:roadmap [prd-file|feature] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--delegate]</syntax>

  <flow>
  1. Analyze: Parse PRD + understand requirements
  2. Plan: Workflow structure + dependency mapping
  3. Coordinate: Multi-agent + domain expertise
  4. Execute: Step-by-step workflows + task coordination
  5. Validate: Quality gates + workflow completeness
  6. Document: feature path `docs/features/<slug>/05-plan.md` (or `05a-plan-workflow.md` if primary plan exists per multi-of-same-phase rule), standalone `docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md` — slug resolution (zero-match default `[f]`), frontmatter, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`.
  </flow>

  <outputs>
| Artifact | Purpose |
|---|---|
| Feature path: `docs/features/<slug>/05-plan.md` (or `05a-plan-workflow.md` variant) | Phase doc when slug resolves to existing/new feature folder |
| Standalone path: `docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md` | One-off workflow, no related work expected |
| TaskCreate/TaskUpdate items | Task tracking hierarchy |
  </outputs>


  <tools>
  - Read/Write/Edit: PRD analysis + workflow docs
  - TaskCreate/TaskUpdate: Multi-phase progress tracking
  - Task: Parallel workflow + multi-agent
  - WebSearch: Tech research + framework validation
  </tools>

  <examples>

| Input | Output |
|---|---|
| `docs/PRD.md --strategy systematic --depth deep` | Comprehensive PRD workflow |
| `'user auth system' --strategy agile --delegate` | Agile + parallel coordination |
| `enterprise-prd.md --strategy enterprise --depth deep` | Enterprise + compliance |
| `project-brief.md --depth normal` | Cross-session with Serena |

  <example name="workflow-no-prd" type="error-path">
    - Input: /sc:roadmap --strategy enterprise --delegate (no PRD or feature doc)
    - Why wrong: Workflow generation needs PRD or feature doc as input. No input = no tasks to generate.
    - Correct: Make PRD first: /sc:brainstorm → /sc:design → save to file → /sc:roadmap PRD.md
  </example>

  </examples>


  <gotchas>
  - scope-match: Workflow scope must match PRD or feature request exactly
  - step-granularity: Each workflow step independently verifiable
  - name-vs-harness-tool: /sc:roadmap (SC content command — authors a PRD→task plan document) is distinct from the harness Workflow tool (deterministic multi-subagent execution). This command writes a plan; it does not orchestrate subagent fan-out or run agents.
  </gotchas>

  <bounds>
    <does>comprehensive workflows, multi-agent+MCP, cross-session management.</does>
    <never>execute impl beyond planning, override dev process, generate without analysis.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:task"/>
</component>