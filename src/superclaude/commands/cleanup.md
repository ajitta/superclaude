---
description: Systematically clean up code, remove dead code, and optimize project structure
---
<component name="cleanup" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:cleanup
    <mission>Systematically clean up code, remove dead code, and optimize project structure</mission>
  </role>

  <syntax>/sc:cleanup [target] [--type code|imports|files|all] [--safe|--aggressive] [--interactive]</syntax>

  <triggers>
    - Code maintenance + tech debt
    - Dead code removal
    - Project structure improvement
    - Codebase hygiene
  </triggers>

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

  <checklist note="MUST complete all">
    - [ ] Pre-cleanup snapshot/backup noted
    - [ ] Cleanup actions executed per --type
    - [ ] Tests still passing (no functionality loss)
    - [ ] Cleanup report generated
  </checklist>

  <mcp servers="seq:analysis|c7:patterns"/>
  <personas p="arch|qual|sec"/>

  <tools>
    - Read/Grep/Glob: Analysis + pattern detection
    - Edit/MultiEdit: Safe modification
    - TodoWrite: Progress tracking
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

  <bounds will="systematic cleanup|safety validation|intelligent algorithms" wont="remove without analysis|override exclusions|compromise functionality"/>
</component>
