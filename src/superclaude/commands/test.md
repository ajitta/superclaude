---
description: Execute tests with coverage analysis and automated quality reporting
---
<component name="test" type="command">

  <role>
    /sc:test
    <mission>Execute tests with coverage analysis and automated quality reporting</mission>
  </role>

  <syntax>/sc:test [target] [--type unit|integration|e2e|all] [--tdd] [--coverage] [--watch] [--fix]</syntax>

  <flow>
  1. Discover: Categorize tests via runner patterns
  2. Configure: Environment + execution params
  3. Execute: Run + real-time progress
  4. Analyze: Coverage reports + failure diagnostics
  5. Report: Generate outputs per flags
  </flow>

  <outputs>
| Flag | Output | Metrics |
|---|---|---|
| --coverage | `coverage/` (tool-generated) | line ≥80%, branch ≥70% |
| --type unit | Console: pass/fail summary | pass rate + failure details |
| --type e2e | Console: flow results | screenshots if fail (Playwright) |
| default | Console: test summary | pass count, failures, duration |
  </outputs>


  <tools>
  - Bash: Test runner execution
  - Glob: Test discovery + patterns
  - Grep: Result parsing + failure analysis
  - Write: Coverage reports + summaries
  </tools>

  <patterns>
    - Discovery: Pattern categorization → runner selection
    - Coverage: Metrics → comprehensive reporting
    - E2E: Browser automation → cross-platform validation
    - Watch: File monitoring → continuous execution
    - TDD (--tdd): RED (write one failing test) → GREEN (simplest code to pass) → REFACTOR (clean up under green) → repeat per behavior
  </patterns>

  <examples>

| Input | Output |
|---|---|
| `/sc:test` | All tests + basic coverage |
| `src/components --type unit --coverage` | Targeted coverage |
| `--type e2e` | Playwright browser testing |
| `--watch --fix` | Continuous + auto-fix |
| `--tdd src/auth/` | RED-GREEN-REFACTOR cycle for auth module |

  <example name="retry-without-diagnosis" type="error-path">
    - Input: /sc:test (after 3 test failures, re-running same tests hoping they pass)
    - Why wrong: Retrying failing tests without investigating root cause is not productive.
    - Correct: Analyze failure output → /sc:troubleshoot --type bug → fix root cause → /sc:test
  </example>

  </examples>


  <gotchas>
  - baseline-first: Run existing tests and record baseline before making changes
  - uv-run: Use `uv run pytest` for this project, never `python -m pytest` or bare `pytest`
  </gotchas>

  <bounds>
    <does>execute existing tests, coverage reports, and failure analysis.</does>
    <never>generate test cases, modify framework config, and destructive changes.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:troubleshoot /sc:implement"/>
</component>
