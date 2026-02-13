---
description: Systematically clean up code, remove dead code, and optimize project structure
---
<component name="cleanup" type="command">

  <role>
    /sc:cleanup
    <mission>Systematically clean up code, remove dead code, and optimize project structure</mission>
  </role>

  <syntax>/sc:cleanup [target] [--type code|imports|files|all] [--safe|--aggressive] [--interactive]</syntax>

  <triggers>code maintenance|dead code removal|project structure|codebase hygiene</triggers>

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
| code | Remove dead code | CLEANUP_CODE.md |
| imports | Remove unused imports | CLEANUP_IMPORTS.md |
| files | Remove orphan files | CLEANUP_FILES.md |
| all | All above | CLEANUP_REPORT.md |
  </outputs>


  <mcp servers="seq|c7"/>
  <personas p="arch|qual|sec"/>

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
    - Safety: Pre/during/post checks
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `src/ --type code --safe` | Conservative cleanup |
| `--type imports --preview` | Unused import analysis |
| `--type all --interactive` | Multi-domain with guidance |
| `components/ --aggressive` | Thorough cleanup |

  </examples>

  <bounds will="systematic cleanup|safety validation|intelligent algorithms" wont="remove without analysis|override exclusions|compromise functionality" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="execution">Implement cleanup actions as requested | Safe mode (--safe): Only low-risk removals | Interactive mode (--interactive): Confirm each removal</boundaries>


  <auto_fix_threshold>
    <safe>Unused imports, dead variables, empty files</safe>
    <approval_required>Exported functions, config files, shared modules</approval_required>
  </auto_fix_threshold>


  <handoff next="/sc:test /sc:git"/>
</component>
