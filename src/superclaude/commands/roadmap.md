---
description: Generate a phased implementation workflow from PRDs and feature requirements. On request only — the user's /sc:roadmap or a workflow step that names it. Not for a TDD plan from a spec (use /sc:plan) or a short task list — answer inline.
---
<component name="roadmap" type="command">

  <role command="/sc:roadmap">
    <mission>Generate structured implementation workflows from PRDs + feature requirements</mission>
  </role>

  <syntax>/sc:roadmap [prd-file|feature] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--delegate]</syntax>

  <flow>
  1. Analyze: Read the source: the PRD or doc passed in; else, for a feature, its folder's `04-design.md` (fallback `01-discovery.md`); else the user's description. Parse it and understand the requirements. Whatever the source, a discovery spec that is still `status: draft` (the source doc, or the feature folder's `01-discovery.md`, even when `04-design.md` exists) → stop and point to `/sc:review --scope spec <path>`, the same review gate /sc:plan applies. A design doc (`04-design.md`, or a `docs/specs/*-design-*.md`) does not stop it for being `draft`; one with unresolved "Areas of concern" → say so and ask whether to build the workflow anyway
  2. Plan: Workflow structure + dependency mapping
  3. Consult: independent analysis streams may go to `general-purpose` delegates with the domain checks in the prompt; they return findings, and the main loop writes the doc
  4. Sequence: Order the workflow steps and their task dependencies; nothing is executed
  5. Validate: Quality gates + workflow completeness. Write each feature as an unchecked box with an empty `Evidence:` line; the implementing session checks the box only when Evidence cites the check that passed (test output, exit code, observed user flow). The doc's frontmatter status follows core/rules/RULES_DOCS.md and starts as `status: draft`
  6. Document: feature path `docs/features/<slug>/05-plan.md` (or `05<letter>-plan-workflow.md`, first free letter, if primary plan exists per multi-of-same-phase rule), standalone `docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md` — slug resolution (zero-match default `[f]`), frontmatter, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`. A design doc that is the Analyze step's source moves from `status: draft` to `approved-for-plan` (bump its `revised`) in the same save, since building the workflow on it is its approval; its Areas of concern section keeps any concern the user chose to build past.
  </flow>

  <flags>
  - --strategy systematic|agile|enterprise: systematic works through every requirement area in order; agile splits the work into parallel streams (e.g. frontend, backend, security) and iterates; enterprise adds compliance and validation requirements throughout.
  - --depth shallow|normal|deep: detail per workflow step: shallow brief, normal balanced, deep adds acceptance criteria and risks.
  </flags>

  <outputs>
| Artifact | Purpose |
|---|---|
| Feature path: `docs/features/<slug>/05-plan.md` (or `05<letter>-plan-workflow.md` variant) | Phase doc when slug resolves to existing/new feature folder |
| Standalone path: `docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md` | One-off workflow, no related work expected |
| TaskCreate/TaskUpdate items | Task tracking hierarchy |
  </outputs>


  <tools>
  - Agent: Domain-agent analysis; agents return findings, the main loop writes the doc
  </tools>

  <examples>

| Input | Output |
|---|---|
| `docs/PRD.md --strategy systematic --depth deep` | Comprehensive PRD workflow |
| `'user auth system' --strategy agile --delegate` | Agile + parallel coordination |
| `enterprise-prd.md --strategy enterprise --depth deep` | Enterprise + compliance |
| `project-brief.md --depth normal` | Cross-session via /sc:save |

  <example name="workflow-no-prd" type="error-path">
    - Input: /sc:roadmap --strategy enterprise --delegate (no PRD or feature doc)
    - Why wrong: Workflow generation needs PRD or feature doc as input. No input = no tasks to generate.
    - Correct: Make PRD first: /sc:brainstorm → /sc:design → save to file → /sc:roadmap PRD.md
  </example>

  </examples>


  <gotchas>
  - scope-match: Workflow scope must match PRD or feature request exactly
  - step-granularity: Each workflow step independently verifiable
  - name-vs-harness-tool: /sc:roadmap (superclaude command — authors a PRD→task plan document) is distinct from the harness Workflow tool (deterministic multi-subagent execution). This command writes a plan; agents it consults return analysis only, and it never runs a fan-out that executes the work.
  </gotchas>

  <bounds>
    <does>comprehensive workflows, domain-agent analysis with MCP, cross-session management.</does>
    <never>executes implementation beyond planning, overrides the development process, or generates without analysis.</never>
  </bounds>

  <handoff next="/sc:implement /sc:task"/>
</component>