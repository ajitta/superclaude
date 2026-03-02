---
name: sc-cleanup
description: >-
  This skill should be used when the user asks to
  "clean up this code",
  "remove dead code",
  "remove unused imports",
  "clean up project structure",
  "find and remove orphan files",
  "optimize imports",
  "code cleanup",
  "remove unused variables",
  "tidy up the codebase".
version: 1.0.0
metadata:
  context: inline
  agent: refactoring-expert
  mcp: seq
  allowed-tools:
    - Read
    - Grep
    - Glob
    - Edit
---
<component name="sc-cleanup" type="skill">

  <role>
    <mission>Systematically clean up code, remove dead code, and optimize project structure</mission>
  </role>

  <syntax>/sc:cleanup [target] [--type code|imports|files|all] [--safe|--aggressive] [--interactive]</syntax>

  <flow>
    1. Analyze: Scan target for cleanup opportunities, assess safety of each removal
    2. Plan: Generate before/after diff preview, categorize changes by risk level (safe/needs-review)
    3. Execute: Apply changes per --type flag, respecting --safe/--aggressive mode
    4. Validate: Run existing tests to confirm no functionality loss
    5. Report: Output summary with items removed, bytes saved, and maintenance recommendations
  </flow>

  <cleanup_types>
| Type | Actions | Safety |
|------|---------|--------|
| code | Remove dead code, unused functions, unreachable branches | Verify no dynamic references |
| imports | Remove unused imports, sort remaining | Safe — static analysis |
| files | Remove orphan files, empty modules, stale configs | Verify no dynamic loading |
| all | All above in sequence | Each step validated independently |
  </cleanup_types>

  <safety_modes>
    - --safe (default): Only remove items confirmed unreferenced by static analysis. Skip any ambiguous cases.
    - --aggressive: Include items that appear unused but may have dynamic references. Requires user confirmation for each removal.
    - --interactive: Present each removal candidate for user approval before applying.
  </safety_modes>

  <patterns>
    - DeadCode: Cross-reference all symbols → identify unreferenced → confirm with grep/glob → safe removal
    - Imports: Parse import statements → check usage in file → remove unused → sort remaining
    - Structure: Find empty __init__.py, orphan configs, stale generated files → validate → remove
    - Safety: Pre-cleanup test run → apply changes → post-cleanup test run → revert if tests fail
  </patterns>

  <auto_fix_threshold>
    <safe>Unused imports, dead variables, empty files, commented-out code blocks</safe>
    <approval_required>Exported functions, config files, shared modules, files with dynamic imports</approval_required>
  </auto_fix_threshold>

  <examples>
| Input | Output |
|-------|--------|
| `src/ --type code --safe` | Conservative dead code removal |
| `--type imports --safe` | Unused import cleanup across project |
| `--type all --interactive` | Full cleanup with per-item approval |
| `components/ --aggressive` | Thorough cleanup with confirmations |
| (auto-trigger) "clean up this code" | Skill activates, runs code cleanup in safe mode |
| (auto-trigger) "remove unused imports" | Skill activates, runs import cleanup |

  <example name="aggressive-without-review" type="error-path">
    <input>/sc:cleanup --type all --aggressive (on unfamiliar codebase)</input>
    <why_wrong>Aggressive cleanup without understanding the codebase risks removing code that appears unused but is dynamically referenced.</why_wrong>
    <correct>/sc:cleanup --type all --safe first, review results, then selectively use --aggressive on confirmed areas</correct>
  </example>
  </examples>

  <bounds will="systematic cleanup|safety validation|before/after diff|test verification" wont="remove without analysis|override exclusions|compromise functionality|skip test validation" fallback="Ask user for guidance when removal safety is uncertain"/>

  <handoff next="/sc:test /sc:git"/>
</component>
