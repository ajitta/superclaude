---
name: sc-test
description: >-
  This skill should be used when the user asks to
  "run tests",
  "execute test suite",
  "check test coverage",
  "run unit tests",
  "run integration tests",
  "run e2e tests",
  "test coverage report",
  "watch mode tests",
  "fix failing tests".
version: 1.0.0
metadata:
  context: inline
  agent: quality-engineer
  mcp: play
  allowed-tools:
    - Bash
    - Glob
    - Grep
    - Write
---
<component name="sc-test" type="skill">

  <role>
    <mission>Execute tests with coverage analysis and automated quality reporting</mission>
  </role>

  <syntax>/sc:test [target] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]</syntax>

  <flow>
    1. Discover: Detect test runner (pytest/jest/vitest/mocha/cargo test) from config files (pyproject.toml, package.json, Cargo.toml)
    2. Configure: Set environment variables, select test type (unit/integration/e2e), apply target filters
    3. Execute: Run test suite with real-time progress output, capture results
    4. Analyze: Parse results for failures, generate coverage report if --coverage, identify flaky tests
    5. Report: Output summary with pass/fail counts, coverage percentages, failure diagnostics, and next-step recommendations
  </flow>

  <runner_detection note="Auto-detect test framework">
| Config File | Runner | Command |
|-------------|--------|---------|
| pyproject.toml (pytest) | pytest | `uv run pytest` or `python -m pytest` |
| package.json (jest) | jest | `npx jest` or `npm test` |
| package.json (vitest) | vitest | `npx vitest` |
| package.json (mocha) | mocha | `npx mocha` |
| Cargo.toml | cargo | `cargo test` |
| go.mod | go test | `go test ./...` |
  </runner_detection>

  <outputs note="Per flags">
| Flag | Output | Metrics |
|------|--------|---------|
| --coverage | coverage/ | line >=80%, branch >=70% |
| --type unit | TEST_UNIT.log | pass rate |
| --type e2e | TEST_E2E.log | screenshots if fail |
| default | TEST_REPORT.md | summary + failures |
  </outputs>

  <patterns>
    - Discovery: Scan for test config files, detect runner, categorize tests by path convention (tests/unit/, tests/integration/, tests/e2e/)
    - Coverage: Run with coverage flags, parse report, highlight under-threshold modules
    - E2E: Use Playwright MCP for browser automation, capture screenshots on failure
    - Watch: File monitoring with continuous re-execution on changes
    - FailureDiagnosis: Parse stack traces, identify root cause patterns, suggest /sc:troubleshoot for complex failures
  </patterns>

  <examples>
| Input | Output |
|-------|--------|
| `/sc:test` | All tests + basic summary |
| `src/components --type unit --coverage` | Targeted unit tests with coverage |
| `--type e2e` | Playwright browser testing |
| `--watch --fix` | Continuous + auto-fix simple failures |
| (auto-trigger) "run the tests" | Skill activates, discovers runner, executes |
| (auto-trigger) "check coverage" | Skill activates, runs with --coverage flag |

  <example name="retry-without-diagnosis" type="error-path">
    <input>/sc:test (after 3 test failures, re-running same tests hoping they pass)</input>
    <why_wrong>Retrying failing tests without investigating root cause is not productive.</why_wrong>
    <correct>Analyze failure output → /sc:troubleshoot --type bug → fix root cause → /sc:test</correct>
  </example>
  </examples>

  <bounds will="execute existing tests|coverage reports|failure analysis|runner detection" wont="generate test cases|modify framework config|destructive changes" fallback="Ask user for guidance when test framework is ambiguous"/>

  <handoff next="/sc:troubleshoot /sc:implement /sc:git"/>
</component>
