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

  <triggers>
    - Complex multi-domain operations
    - Large-scale system operations
    - Parallel coordination + dependency management
    - Meta-level orchestration beyond standard commands
  </triggers>

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
| TodoWrite hierarchy | Task breakdown tracking |
| SPAWN_PLAN.md | Execution strategy doc |
| SPAWN_RESULT.md | Aggregated results |
  </outputs>

  <checklist note="MUST complete all">
    - [ ] Task decomposition complete (Epic→Subtask)
    - [ ] Dependencies mapped correctly
    - [ ] All subtasks executed or delegated
    - [ ] Results aggregated and summarized
  </checklist>

  <tools>
    - TodoWrite: Hierarchical breakdown (Epic→Story→Task)
    - Read/Grep/Glob: Dependency mapping
    - Edit/MultiEdit/Write: Coordinated file ops
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

  <bounds will="multi-domain decomposition|intelligent orchestration|meta-system ops" wont="replace domain commands|override user strategy|execute without analysis"/>
</component>
