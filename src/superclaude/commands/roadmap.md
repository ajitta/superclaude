---
description: Generate structured implementation workflows from PRDs and feature requirements. Use when user types `/sc:roadmap` or hands over PRD/feature doc and asks for task breakdown to commit under docs/plans/. Do NOT auto-trigger on "what's the order of steps" or short ad-hoc task lists — those get inline 2-3 step answer, not workflow file.
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
  6. Document (routing per core/rules/RULES_DOCS.md `<doc_output_convention>`): on feature path, write workflow to `docs/features/<slug>/05-plan.md` (variant — uses `05a-plan-workflow.md` if a primary plan doc already exists per multi-of-same-phase rule; frontmatter: `status: draft, revised: <today>`) AND update `docs/features/<slug>/README.md` (`updated:` bump + append entry to `## Documents`, advance `phase:` if status enum moved). On standalone path, write to `docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md` — no README update needed.
  </flow>

  <outputs>
Routing: per core/rules/RULES_DOCS.md `<doc_output_convention>` — feature path `docs/features/<slug>/05-plan.md` (variant — `05a-plan-workflow.md` if primary plan doc exists per multi-of-same-phase rule; existing folder OR user picks `[f]`) | standalone path `docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md` (user picks `[s]` or no related work expected). Slug resolution: exact-match silent / multi partial-match prompt / zero match → `[f]/[s]` w/ default `[f]`.

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