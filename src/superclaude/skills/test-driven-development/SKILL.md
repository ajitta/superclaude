---
name: test-driven-development
description: |
  RED-GREEN-REFACTOR cycle for feature and bugfix implementation.
  Write failing test first, then minimal code to pass.
  Triggers: new feature, bug fix, refactoring, behavior change.
---
<component name="test-driven-development" type="skill">

  <role>
    <mission>Drive implementation through the RED-GREEN-REFACTOR cycle: write a failing test, make it pass with minimal code, then clean up under green tests</mission>
  </role>

  <when>
  - All feature work and bug fixes
  - Refactoring (test existing behavior first, then restructure)
  - Behavior changes
  - Use judgment for: configuration files, static assets, generated code, throwaway prototypes
  </when>

  <flow>
    1. RED — Write one failing test for one specific behavior. Run it and confirm it fails for the expected reason (missing feature, not a typo or import error). If it passes immediately, the behavior already exists — adjust the test
    2. GREEN — Write the simplest code that passes. No speculative features, no extras beyond what the test requires. Run the full test suite to confirm the new test passes and nothing else broke
    3. REFACTOR — Clean up under green tests. Remove duplication, improve names, extract helpers. Run tests after each change. If a refactor breaks a test, undo it. Refactoring changes structure, not behavior
    4. Repeat — Pick the next behavior and write the next failing test
    5. Bug fixes follow the same cycle. Write a test that reproduces the bug (RED), fix it (GREEN), clean up (REFACTOR). The test proves the fix and prevents regression
  </flow>

  <exceptions>
  - Refactoring existing code: Write tests for current behavior first, then restructure under green tests. Always TDD
  - Legacy code without tests: Add tests at the boundaries before modifying internals. Test what exists, then apply TDD for changes
  - Config and static files: Use judgment — TDD applies to logic, not to declarative content
  </exceptions>

  <constraints>
  - Write a failing test before writing implementation code. If code was written first, consider starting over test-first rather than backfilling tests
  - One behavior per test. If the test name contains "and", split it
  - In the GREEN step, write only enough code to pass the failing test — no anticipated features
  - Refactor only when all tests are green. Never add new behavior during refactoring
  - Prefer real objects over mocks. If something is hard to test, that signals a design issue worth addressing
  </constraints>

  <bounds will="TDD cycle enforcement|test-first development|minimal implementation|refactoring under green" wont="write code before tests|add speculative features|refactor with failing tests"/>

  <handoff next="/sc:test /sc:review"/>
</component>
