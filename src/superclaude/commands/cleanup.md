---
description: Systematically clean up code, remove dead code, and optimize project structure
---
<component name="cleanup" type="command">

  <role command="/sc:cleanup">
    <mission>Systematically clean up code, remove dead code, and optimize project structure</mission>
  </role>

  <syntax>/sc:cleanup [target] [--type code|imports|files|docs|all] [--safe|--aggressive] [--interactive] [--dry-run]</syntax>

  <flow>
  1. Analyze: Cleanup opportunities + safety assessment
  2. Plan: Choose approach + delegate to agents
  3. Execute: Systematic cleanup per --type
  4. Validate: Ensure no functionality loss (tests pass)
  5. Report: Summary + maintenance recs
  </flow>

  <outputs note="Per --type flag">
| Type | Actions | Report |
|---|---|---|
| code | Remove dead code | Console: removed items + line count |
| imports | Remove unused imports | Console: removed imports per file |
| files | Remove orphan files | Console: deleted file list |
| docs | Validate + transform doc naming convention | Console: renamed/moved files |
| all | All above | Console: combined summary |
  </outputs>


  <tools>
  - Read/Grep/Glob: Analysis + pattern detection
  - Edit: Safe modification
  - TaskCreate/TaskUpdate: Progress tracking
  - Task: Large-scale delegation
  </tools>

  <patterns>
    - DeadCode: Usage analysis → safe removal
    - Imports: Dependency analysis → optimization
    - Structure: Architecture analysis → modular improvements
    - Docs: Convention validation → rename + move (--dry-run supported)
    - Safety: Pre/during/post checks
  </patterns>

  <examples>

| Input | Output |
|---|---|
| `src/ --type code --safe` | Conservative cleanup |
| `--type imports --safe` | Unused import analysis |
| `--type all --interactive` | Multi-domain with guidance |
| `components/ --aggressive` | Thorough cleanup |
| `--type docs --dry-run` | Preview doc naming fixes |
| `--type docs` | Auto-fix doc naming convention |

  <example name="aggressive-without-review" type="error-path">
    - Input: /sc:cleanup --type all --aggressive (on unfamiliar codebase)
    - Why wrong: Aggressive cleanup without understanding the codebase risks removing code that appears unused but is dynamically referenced.
    - Correct: /sc:cleanup --type all --preview first, review results, then /sc:cleanup --type all --safe
  </example>

  </examples>


  <gotchas>
  - scope-check: Only clean up files in the requested scope. Do not touch adjacent directories
  - verify-unused: Confirm files are truly unused (grep for references) before deleting
  </gotchas>

  <bounds>
    <does>systematic cleanup, safety validation, and intelligent algorithms.</does>
    <never>remove without analysis, override exclusions, and compromise functionality.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <auto_fix_threshold>
    <safe>Unused imports, dead variables, empty files</safe>
    <approval_required>Exported functions, config files, shared modules</approval_required>
  </auto_fix_threshold>

  <handoff next="/sc:test /sc:build"/>
</component>
