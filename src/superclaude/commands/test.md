---
description: Execute tests with coverage analysis and automated quality reporting
---
<component name="test" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <constraints note="Reinforced from RULES.md">Scope: build only what's asked | Read before edit | No adjacent improvements</constraints>

  <role>
    /sc:test
    <mission>Execute tests with coverage analysis and automated quality reporting</mission>
  </role>

  <syntax>/sc:test [target] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]</syntax>

  <triggers>test execution|coverage analysis|continuous testing|test failure analysis</triggers>

  <flow>
    1. Discover: Categorize tests via runner patterns
    2. Configure: Environment + execution params
    3. Execute: Run + real-time progress
    4. Analyze: Coverage reports + failure diagnostics
    5. Report: Generate outputs per flags
  </flow>

  <outputs note="Per flags">
| Flag | Output | Metrics |
|------|--------|---------|
| --coverage | coverage/ | line ≥80%, branch ≥70% |
| --type unit | TEST_UNIT.log | pass rate |
| --type e2e | TEST_E2E.log | screenshots if fail |
| default | TEST_REPORT.md | summary + failures |
  </outputs>

  <checklist note="Completion criteria">
    - [ ] All targeted tests executed (show pass/fail counts)
    - [ ] Coverage meets thresholds (if --coverage)
    - [ ] Failure diagnostics provided (root cause per failure)
    - [ ] Test report generated (confirm file written)
  </checklist>

  <mcp servers="play"/>
  <personas p="qa"/>

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
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `/sc:test` | All tests + basic coverage |
| `src/components --type unit --coverage` | Targeted coverage |
| `--type e2e` | Playwright browser testing |
| `--watch --fix` | Continuous + auto-fix |

  </examples>

  <bounds will="execute existing tests|coverage reports|failure analysis" wont="generate test cases|modify framework config|destructive changes" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="execution" critical="true">
    <rule>Execute tests and report results</rule>
    <rule>Run existing tests; defer new test creation to /sc:implement --with-tests</rule>
    <rule>Preserve test framework configuration</rule>
  </boundaries>

  <completion_criteria>
    - [ ] All targeted tests executed
    - [ ] Coverage report generated (if --coverage)
    - [ ] Failure analysis provided for failed tests
  </completion_criteria>

  <handoff>
    <next command="/sc:troubleshoot">For fixing failed tests</next>
    <next command="/sc:implement --with-tests">For adding new test cases</next>
    <next command="/sc:git">For committing after all tests pass</next>
    <format>Include test results summary for next steps</format>
  </handoff>
</component>
