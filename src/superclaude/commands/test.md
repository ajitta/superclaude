---
description: Execute tests with coverage analysis and automated quality reporting. Use ONLY when user explicitly types `/sc:test` — runs full test orchestration with coverage. Do NOT auto-trigger on "run the tests", "run pytest", or executing single test file — invoke pytest/jest/etc. directly via Bash.
---
<component name="test" type="command">

  <role command="/sc:test">
    <mission>Execute tests with coverage analysis and automated quality reporting</mission>
  </role>

  <syntax>/sc:test [target] [--type unit|integration|e2e|all] [--tdd] [--coverage] [--watch] [--fix]</syntax>

  <flow>
  1. Discover: Categorize tests via runner patterns
  2. Configure: Environment + execution params
  3. Execute: Run + real-time progress
  4. Analyze: Coverage reports + failure diagnostics
  5. Report: Generate outputs per flags
  6. Verify: when the user asks for independent evidence, dispatch the verifier (the Agent entry in the tools section) and attach its report to the output
  </flow>

  <flags>
  - --type unit|integration|e2e|all: which suite runs; e2e runs Playwright browser tests; all runs every suite.
  - --tdd: cycle in the TDD pattern.
  - --coverage: collect coverage and report it against the thresholds (line ≥80%, branch ≥70%).
  - --watch: run the project's watch mode, re-running affected tests on change.
  - --fix: on failure, find the root cause as /sc:troubleshoot --type bug would and fix the code, then re-run; never edit a test just to make it pass.
  </flags>

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
  - Agent: dispatch the `verifier` agent for a fresh-context run-and-report pass — it runs the project's commands, exercises the changed behavior, compares with the plan doc (05-plan.md Proof section and task list) and reports every mismatch without fixing; its description limits it to explicit requests for run-and-report evidence
  </tools>

  <patterns>
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
    - Why wrong: Retrying failing tests without root cause investigation unproductive.
    - Correct: Analyze failure output → /sc:troubleshoot --type bug → fix root cause → /sc:test
  </example>

  </examples>


  <gotchas>
  - baseline-first: Run existing tests, record baseline before changes
  </gotchas>

  <bounds>
    <does>execute existing tests, coverage reports, failure analysis, root-cause fixes when --fix is given.</does>
    <never>generate test cases outside an explicit --tdd request, modify framework config, destructive changes.</never>
  </bounds>

  <handoff next="/sc:troubleshoot /sc:implement"/>
</component>