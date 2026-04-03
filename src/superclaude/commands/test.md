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
|------|--------|---------|
| --coverage | coverage/ | line ≥80%, branch ≥70% |
| --type unit | docs/reports/TEST_UNIT.log | pass rate |
| --type e2e | docs/reports/TEST_E2E.log | screenshots if fail |
| default | docs/reports/TEST_REPORT.md | summary + failures |
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
|-------|--------|
| `/sc:test` | All tests + basic coverage |
| `src/components --type unit --coverage` | Targeted coverage |
| `--type e2e` | Playwright browser testing |
| `--watch --fix` | Continuous + auto-fix |
| `--tdd src/auth/` | RED-GREEN-REFACTOR cycle for auth module |

  <example name="retry-without-diagnosis" type="error-path">
    <input>/sc:test (after 3 test failures, re-running same tests hoping they pass)</input>
    <why_wrong>Retrying failing tests without investigating root cause is not productive.</why_wrong>
    <correct>Analyze failure output → /sc:troubleshoot --type bug → fix root cause → /sc:test</correct>
  </example>

  </examples>

  <token_note>Medium consumption — E2E tests with --play use more context than unit tests</token_note>

  <bounds will="execute existing tests|coverage reports|failure analysis" wont="generate test cases|modify framework config|destructive changes" fallback="Ask user for guidance when uncertain">

    Execute tests and report results | Run existing tests; defer new test creation to /sc:implement --with-tests | Preserve test framework configuration

  </bounds>

  <handoff next="/sc:troubleshoot /sc:implement"/>
</component>
