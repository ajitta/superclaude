---
description: Systematically clean up code, remove dead code, and optimize project structure
---
<component name="cleanup" type="command">

  <role>
    /sc:cleanup
    <mission>Systematically clean up code, remove dead code, and optimize project structure</mission>
  </role>

  <syntax>/sc:cleanup [target] [--type code|imports|files|docs|all] [--safe|--aggressive] [--interactive] [--dry-run]</syntax>

  <flow>
    1. Analyze: Cleanup opportunities + safety assessment
    2. Plan: Choose approach + activate personas
    3. Execute: Systematic cleanup per --type
    4. Validate: Ensure no functionality loss (tests pass)
    5. Report: Summary + maintenance recs
  </flow>

  <outputs note="Per --type flag">
| Type | Actions | Report |
|------|---------|--------|
| code | Remove dead code | docs/reports/CLEANUP_CODE.md |
| imports | Remove unused imports | docs/reports/CLEANUP_IMPORTS.md |
| files | Remove orphan files | docs/reports/CLEANUP_FILES.md |
| docs | Validate + transform doc naming convention | docs/reports/CLEANUP_DOCS.md |
| all | All above | docs/reports/CLEANUP_REPORT.md |
  </outputs>

  <mcp servers="seq|c7"/>
  <personas p="arch|qual|sec|refactor"/>

  <tools>
    - Read/Grep/Glob: Analysis + pattern detection
    - Edit: Safe modification
    - TaskCreate/TaskUpdate: Progress tracking
    - Task: Large-scale delegation
  </tools>

  <patterns>
    - DeadCode: Usage analysis → safe removal
    - Imports: Dependency analysis → optimization
    - Structure: Arch analysis → modular improvements
    - Docs: Convention validation → rename + move (--dry-run supported)
    - Safety: Pre/during/post checks
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `src/ --type code --safe` | Conservative cleanup |
| `--type imports --safe` | Unused import analysis |
| `--type all --interactive` | Multi-domain with guidance |
| `components/ --aggressive` | Thorough cleanup |
| `--type docs --dry-run` | Preview doc naming fixes |
| `--type docs` | Auto-fix doc naming convention |

  <example name="aggressive-without-review" type="error-path">
    <input>/sc:cleanup --type all --aggressive (on unfamiliar codebase)</input>
    <why_wrong>Aggressive cleanup without understanding the codebase risks removing code that appears unused but is dynamically referenced.</why_wrong>
    <correct>/sc:cleanup --type all --preview first, review results, then /sc:cleanup --type all --safe</correct>
  </example>

  </examples>

  <token_note>Medium consumption — scales with target scope; use --safe for conservative cleanup</token_note>

  <bounds will="systematic cleanup|safety validation|intelligent algorithms" wont="remove without analysis|override exclusions|compromise functionality" fallback="Ask user for guidance when uncertain" type="execution">

    Implement cleanup actions as requested | Safe mode (--safe): Only low-risk removals | Interactive mode (--interactive): Confirm each removal

  </bounds>

  <auto_fix_threshold>
    <safe>Unused imports, dead variables, empty files</safe>
    <approval_required>Exported functions, config files, shared modules</approval_required>
  </auto_fix_threshold>

  <handoff next="/sc:test /sc:build"/>
</component>
