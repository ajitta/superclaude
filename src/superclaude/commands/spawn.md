---
description: Meta-system task orchestration with intelligent breakdown and delegation
---
<component name="spawn" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:spawn
    <mission>Meta-system task orchestration with intelligent breakdown and delegation</mission>
  </role>

  <syntax>/sc:spawn [complex-task] [--strategy sequential|parallel|adaptive] [--depth normal|deep]</syntax>

  <triggers>complex multi-domain ops|large-scale system ops|parallel coordination|meta-orchestration</triggers>

  <flow>
    1. Analyze: Complex op requirements + scope
    2. Decompose: Epic → Story → Task → Subtask
    3. Orchestrate: Execute via --strategy
    4. Monitor: Progress + dependency management
    5. Integrate: Aggregate results + summary
  </flow>

  <outputs note="Per execution">
| Artifact | Purpose |
|----------|---------|
| TaskCreate/TaskUpdate hierarchy | Task breakdown tracking |
| SPAWN_PLAN.md | Execution strategy doc |
| SPAWN_RESULT.md | Aggregated results |
  </outputs>

  <checklist note="Completion criteria">
    - [ ] Task decomposition complete (Epic→Subtask)
    - [ ] Dependencies mapped correctly (show dependency graph)
    - [ ] All subtasks executed or delegated (status per subtask)
    - [ ] Results aggregated and summarized (pass/fail counts)
  </checklist>

  <tools>
    - TaskCreate/TaskUpdate: Hierarchical breakdown (Epic→Story→Task)
    - Read/Grep/Glob: Dependency mapping
    - Edit/Write: Coordinated file ops
    - Bash: System-level coordination
  </tools>

  <patterns>
    - Hierarchy: Epic → Story → Task → Subtask granularity
    - Strategy: Sequential (deps) | Parallel (independent) | Adaptive (dynamic)
    - Meta: Cross-domain → resource opt → result integration
    - Enhancement: Systematic → quality gates → validation
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `'implement user auth system'` | DB→API→UI→Testing coordination |
| `'migrate monolith to microservices' --strategy adaptive --depth deep` | Enterprise orchestration |
| `'CI/CD pipeline with security scanning'` | DevOps+Security+Quality parallel |

  </examples>

  <token_note>Very high consumption — spawns multiple subagents; one major spawn per session recommended</token_note>

  <bounds will="multi-domain decomposition|intelligent orchestration|meta-system ops" wont="replace domain commands|override user strategy|execute without analysis" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only" critical="true">
    <rule>Produce task hierarchy document, then complete</rule>
    <rule>Defer implementation to /sc:task or /sc:implement</rule>
    <rule>Orchestration planning only</rule>
    <output>SPAWN_PLAN.md with task breakdown and dependencies</output>
  </boundaries>

  <handoff>
    <next command="/sc:task">For executing decomposed tasks</next>
    <next command="/sc:implement">For implementing individual components</next>
    <format>Provide task hierarchy for sequential execution</format>
  </handoff>
</component>
