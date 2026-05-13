---
description: Interactive project env setup — pick + run init tasks for first-session onboarding. Use ONLY when user explicit type `/sc:init` — show interactive task picker for first-time project setup. NO auto-trigger on enter new repo or "set this up".
---
<component name="init" type="command">

  <role command="/sc:init">
    <mission>Interactive project env setup w/ selectable init tasks for first-session onboarding</mission>
  </role>

  <syntax>/sc:init [tasks] [--quick] [--full]</syntax>

  <flow>
  1. Detect: scan project root for lang/framework markers (pyproject.toml, package.json, Cargo.toml, go.mod)
  2. Present: show interactive task menu w/ descriptions, deps, detected project context
  3. Select: take user choice — individual tasks (a,b,c...), presets (--quick, --full), or custom combo
  4. Validate: check dep graph, surface missing prereqs, confirm exec plan
  5. Execute: run picked tasks in dep-aware parallel batches w/ progress reporting
  6. Report: final summary table — task status, artifacts made, memory entries stored
  </flow>

  <menu>
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
    [h] Project gotchas setup          — .claude/rules/gotchas/general.md       (no deps)
    [i] docs/ project brain scaffold   — PRD + ARCHITECTURE + ADR + UI-GUIDE    (no deps)

  Presets: --quick (a,b) | --full (a,b,c,d,e,f,g,h,i)

  Enter selection (e.g., a,b,e or --full):
  ```
  </menu>

  <dependency_graph>
  - Batch 1 (no deps, parallel): a, c, e, f, h, i
  - Batch 2 (wait for prereq): b←a, d←c, g←a
  - Schedule only selected tasks; prompt to add missing prerequisites.
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
  | h | general.md | .claude/rules/gotchas/ |
  | i | PRD.md, ARCHITECTURE.md, ADR/0001-*.md, UI-GUIDE.md | docs/ (project root) |
  </task_outputs>

  <safety_rules>
  - Dependency install (c): show command, require user confirmation before executing
  - CLAUDE.md edit (b): if file exists, show proposed additions as diff before applying
  - Test execution (d): warn if test suite is large (>500 tests), offer --quick test flag
  - Memory init (g): merge with existing MEMORY.md, never replace
  - Gotchas init (h): create .claude/rules/gotchas/ directory + general.md only if not exists. Idempotent — skip if gotchas/ already present. Template: 4-line comment header, no frontmatter.
  - Docs scaffold (i): create docs/ directory and copy PRD.md, ARCHITECTURE.md, UI-GUIDE.md, plus docs/ADR/0001-example.md from ~/.claude/superclaude/templates/docs-scaffold/ (project-scope installs: .claude/superclaude/templates/docs-scaffold/). Idempotent — skip per-file if it already exists; never overwrite user content. UI-GUIDE.md is optional (note this and let user delete for headless projects).
  - All tasks: idempotent — safe to re-run, updates rather than duplicates
  </safety_rules>

  <outputs>
  | Artifact | Purpose |
  |---|---|
  | Summary table | Task completion status + artifacts list |
  | PROJECT_INDEX.md | Project structure map (task a) |
  | CLAUDE.md | Project configuration for Claude Code (task b) |
  | Memory entries | Test baseline, conventions, project context (tasks d,e,g) |
  </outputs>


  <tools>
  - Read/Grep/Glob: Project detection and analysis
  - Write/Edit: CLAUDE.md, PROJECT_INDEX.md, MEMORY.md generation
  - Bash: Dependency installation, test execution, git history analysis
  - Agent(repo-index): Delegate structure analysis for task (a)
  </tools>

  <examples>
  | Input | Output |
  |---|---|
  | `/sc:init` | Show interactive menu → await selection |
  | `/sc:init --quick` | Run tasks a,b (structure + CLAUDE.md) |
  | `/sc:init --full` | Run all tasks a-i in parallel batches |
  | `/sc:init a,c,d,e` | Run selected tasks with dependency validation |
  | `/sc:init b` | Detect that (a) is required → "Add structure analysis first?" |
  | `/sc:init i` | Scaffold docs/ with PRD, ARCHITECTURE, ADR, UI-GUIDE templates (idempotent) |

  <example name="missing-prerequisite" type="error-path">
    - Input: /sc:init d (without selecting c)
    - Why wrong: Test baseline (d) requires dependencies installed (c). Running tests without deps will fail.
    - Correct: Detect missing prerequisite → prompt: "Task (d) requires (c). Add dependency check?" → user confirms → run c then d.
  </example>
  </examples>


  <gotchas>
  - check-existing: Verify files do not already exist before creating. Do not overwrite user configuration
  - uv-not-pip: Use `uv` for Python ops in this project
  </gotchas>

  <bounds>
    <does>interactive task menu, dep-aware exec, parallel batching, idempotent setup, safe env init.</does>
    <never>auto-exec w/o selection, overwrite existing files, install w/o confirm, skip dep validation.</never>
    <fallback>Ask user when project type undetectable or existing config clash w/ proposed setup.</fallback>
  </bounds>

  <handoff next="/sc:load /sc:implement /sc:test"/>
</component>