---
description: Clean code systematic, kill dead code, optimize project structure. Use ONLY when user type `/sc:cleanup` explicit — do systematic delete + structural change, need explicit OK. NO auto-trigger on "clean up this function", "remove this import", or any single-file tidy — those direct edit.
---
<component name="cleanup" type="command">

  <role command="/sc:cleanup">
    <mission>Clean code systematic, kill dead code, optimize project structure</mission>
  </role>

  <syntax>/sc:cleanup [target] [--type code|imports|files|docs|all] [--safe|--aggressive] [--interactive] [--dry-run]</syntax>

  <flow>
  1. Analyze: cleanup chance + safety check
  2. Plan: pick approach + delegate agent
  3. Execute: systematic clean per --type
  4. Validate: no function loss (tests pass)
  5. Report: summary + maintain rec
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
  - Read/Grep/Glob: analyze + pattern detect
  - Edit: safe modify
  - TaskCreate/TaskUpdate: progress track
  - Task: big-scale delegate
  </tools>

  <patterns>
    - DeadCode: usage analyze → safe remove
    - Imports: dep analyze → optimize
    - Structure: arch analyze → modular gain
    - Docs: convention check → rename + move (--dry-run supported)
    - Safety: pre/during/post check
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
    - Why wrong: aggressive clean w/o understand codebase risk kill code that look unused but dynamic referenced.
    - Correct: /sc:cleanup --type all --preview first, review result, then /sc:cleanup --type all --safe
  </example>

  </examples>


  <gotchas>
  - scope-check: only clean files in asked scope. No touch adjacent dirs
  - verify-unused: confirm files truly unused (grep for refs) before delete
  </gotchas>

  <bounds>
    <does>systematic clean, safety check, smart algo.</does>
    <never>remove w/o analyze, override exclusion, break function.</never>
    <fallback>Ask user guidance when unsure.</fallback>
  </bounds>

  <auto_fix_threshold>
    <safe>Unused imports, dead variables, empty files</safe>
    <approval_required>Exported functions, config files, shared modules</approval_required>
  </auto_fix_threshold>

  <handoff next="/sc:test /sc:build"/>
</component>