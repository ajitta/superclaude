---
description: Interactive project environment setup — select and run initialization tasks for first-session onboarding
---
<component name="init" type="command">

  <role>
    /sc:init
    <mission>Interactive project environment setup with selectable initialization tasks for first-session onboarding</mission>
  </role>

  <syntax>/sc:init [tasks] [--quick] [--full]</syntax>

  <flow>
    1. Detect: Scan project root for language/framework indicators (pyproject.toml, package.json, Cargo.toml, go.mod)
    2. Present: Show interactive task menu with descriptions, dependencies, and detected project context
    3. Select: Accept user choice — individual tasks (a,b,c...), presets (--quick, --full), or custom combination
    4. Validate: Check dependency graph, surface missing prerequisites, confirm execution plan
    5. Execute: Run selected tasks in dependency-aware parallel batches with progress reporting
    6. Report: Final summary table — task status, artifacts created, memory entries stored
  </flow>

  <menu note="Interactive task selection">
  ```
  Project Initializer

  Detected: [language] / [framework] / [package manager]

  Select initialization tasks:

    [a] Project structure analysis     — language, framework, directory mapping
    [b] CLAUDE.md generation/enhance   — build, test, architecture docs         (requires a)
    [c] Dependency installation check  — package manager detection + install
    [d] Test baseline capture          — run tests, record pass/fail counts     (requires c)
    [e] Code conventions learning      — lint config, commit style, naming
    [f] MCP server recommendation      — project-appropriate MCP suggestions
    [g] Project memory initialization  — key decisions, architecture notes      (requires a)

  Presets: --quick (a,b) | --full (a,b,c,d,e,f,g)

  Enter selection (e.g., a,b,e or --full):
  ```
  </menu>

  <dependency_graph note="Execution order constraints">
  ```
  Batch 1 (parallel):  [a] [c] [e] [f]     — no dependencies
  Batch 2 (parallel):  [b←a] [d←c] [g←a]   — wait for prerequisites
  ```
  Dynamic batching: only schedule selected tasks. If prerequisite missing, prompt user to add it.
  </dependency_graph>

  <task_outputs>
  | Task | Artifact | Location |
  |------|----------|----------|
  | a | PROJECT_INDEX.md | project root |
  | b | CLAUDE.md | project root |
  | c | Install status report | console |
  | d | Test baseline | auto memory |
  | e | Convention summary | auto memory |
  | f | MCP recommendations | console |
  | g | MEMORY.md + topic files | .claude/memory/ |
  </task_outputs>

  <safety_rules>
  - Dependency install (c): show command, require user confirmation before executing
  - CLAUDE.md edit (b): if file exists, show proposed additions as diff before applying
  - Test execution (d): warn if test suite is large (>500 tests), offer --quick test flag
  - Memory init (g): merge with existing MEMORY.md, never replace
  - All tasks: idempotent — safe to re-run, updates rather than duplicates
  </safety_rules>

  <outputs note="Per execution">
  | Artifact | Purpose |
  |----------|---------|
  | Summary table | Task completion status + artifacts list |
  | PROJECT_INDEX.md | Project structure map (task a) |
  | CLAUDE.md | Project configuration for Claude Code (task b) |
  | Memory entries | Test baseline, conventions, project context (tasks d,e,g) |
  </outputs>

  <personas p="arch|be|fe|py"/>

  <tools>
    - Read/Grep/Glob: Project detection and analysis
    - Write/Edit: CLAUDE.md, PROJECT_INDEX.md, MEMORY.md generation
    - Bash: Dependency installation, test execution, git history analysis
    - Agent(repo-index): Delegate structure analysis for task (a)
  </tools>

  <examples>
  | Input | Output |
  |-------|--------|
  | `/sc:init` | Show interactive menu → await selection |
  | `/sc:init --quick` | Run tasks a,b (structure + CLAUDE.md) |
  | `/sc:init --full` | Run all tasks a-g in parallel batches |
  | `/sc:init a,c,d,e` | Run selected tasks with dependency validation |
  | `/sc:init b` | Detect that (a) is required → "Add structure analysis first?" |

  <example name="missing-prerequisite" type="error-path">
    <input>/sc:init d (without selecting c)</input>
    <why_wrong>Test baseline (d) requires dependencies installed (c). Running tests without deps will fail.</why_wrong>
    <correct>Detect missing prerequisite → prompt: "Task (d) requires (c). Add dependency check?" → user confirms → run c then d.</correct>
  </example>
  </examples>

  <token_note>Medium-high consumption — task (a) delegates to repo-index for efficiency. Use --quick for minimal context usage.</token_note>

  <bounds will="interactive task menu|dependency-aware execution|parallel batching|idempotent setup|safe environment init" wont="auto-execute without selection|overwrite existing files|install without confirmation|skip dependency validation" fallback="Ask user when project type undetectable or when existing config conflicts with proposed setup">
    Present menu and execute selected tasks | Validate dependencies before execution | Report results with artifact locations
  </bounds>

  <handoff next="/sc:load /sc:implement /sc:test"/>
</component>
