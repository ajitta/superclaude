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

  <checklist note="SHOULD complete all">
    - [ ] Pre-cleanup snapshot/backup noted
    - [ ] Cleanup actions executed per --type
    - [ ] Tests still passing (no functionality loss)
    - [ ] Cleanup report generated
  </checklist>

  <mcp servers="seq:analysis|c7:patterns"/>
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

  <bounds will="systematic cleanup|safety validation|intelligent algorithms" wont="remove without analysis|override exclusions|compromise functionality"/>

  <boundaries type="execution" critical="true">
    <rule>Implement cleanup actions as requested</rule>
    <rule>Safe mode (--safe): Only low-risk removals</rule>
    <rule>Interactive mode (--interactive): Confirm each removal</rule>
  </boundaries>

  <auto_fix_threshold>
    <safe>Unused imports, dead variables, empty files</safe>
    <approval_required>Exported functions, config files, shared modules</approval_required>
  </auto_fix_threshold>

  <completion_criteria>
    - [ ] All identified cleanup actions applied
    - [ ] No functionality loss verified (tests pass)
    - [ ] Cleanup report generated
  </completion_criteria>

  <handoff>
    <next command="/sc:test">For verifying no regressions</next>
    <next command="/sc:git">For committing cleanup changes</next>
    <format>Summarize removals for review</format>
  </handoff>
</component>
