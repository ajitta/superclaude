---
description: Diagnose + resolve issues in code, builds, deployments, system behavior. Use ONLY when user explicitly types `/sc:troubleshoot` — diagnose + propose; write a failing test and apply the fix only with `--fix`, and risky fixes still need confirm. Do NOT auto-trigger on clear error with obvious fix, syntax errors, or single-file bugs — those get direct fix.
---
<component name="troubleshoot" type="command">

  <role command="/sc:troubleshoot">
    <mission>Diagnose + resolve issues in code, builds, deployments, system behavior</mission>
  </role>

  <syntax>/sc:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]</syntax>

  <flow>
  1. Reproduce: Confirm failure — read full error, identify exact trigger, verify consistent
  2. Investigate: Check git log/diff, trace data flow, find working examples
  3. Hypothesize: Form specific hypothesis ("X causes Y because Z") — max 3 cycles before escalate to user
  4. Confirm: Test hypothesis by changing one variable at a time; check environment before code
  5. Test: Write failing test reproducing exact bug (required before any fix), commit it, then lock test files: `superclaude hook test_file_guard lock`
  6. Fix: Apply single change addressing root cause — no "while I'm here" fixes
  7. Verify: Failing test passes, all existing tests pass, no regressions; then `superclaude hook test_file_guard unlock`
  </flow>

  <flags>
  - --type bug|build|performance|deployment: problem class: bug starts from reproduction and stack trace, build from compiler and dependency output, performance from a measurement, deployment from environment and config.
  - --trace: trace the data flow and execution path up to the failure before naming a cause.
  - --fix: run the Test, Fix and Verify steps, committing the failing test before the lock so a `git checkout --` cannot erase it; without it, stop after the Confirm step and propose the fix. A fix in the approval-required tier of the auto-fix threshold still waits for confirmation.
  </flags>

  <tools>
  - Read: Log analysis + state examination
  - Bash: Diagnostic command execution
  - Grep: Error pattern detection
  - Write: Diagnostic reports + documentation
  </tools>


  <examples>

| Input | Output |
|---|---|
| `'Null pointer in user service' --type bug --trace` | Root cause + targeted fix |
| `'TypeScript compilation errors' --type build --fix` | Auto-apply safe fixes |
| `'API response times degraded' --type performance` | Bottleneck + optimization |
| `'Service not starting' --type deployment --trace` | Environment analysis |

  <example name="symptom-only-fix" type="error-path">
    - Input: /sc:troubleshoot 'users report slow page' --fix (applies caching without profiling)
    - Why wrong: Fix symptoms without diagnosis. Slow page could be N+1 queries, not caching issue.
    - Correct: /sc:troubleshoot 'users report slow page' --trace first → identify bottleneck → targeted fix
  </example>

  </examples>

  <gotchas>
  - evidence-fabrication: Do not construct hypothetical failure scenarios to justify pre-existing recommendation. Evidence (code, config, measurements) must precede proposals.
  - analysis-loop: If reasoning reaches same conclusion twice on same question, terminate that line of analysis, move to next topic.
  - three-failure-levels: a failure sits at one of three levels — (1) bug in the code → fix it; (2) bug in expectations, i.e. the test or the requirement is itself wrong → re-examine it before "fixing" working code; (3) bug in the process → structural cause, the most valuable to record. Level 2 is the one most often skipped, and skipping it turns a wrong requirement into a wrong fix.
  - test-lock: between the Test and Verify steps `test_file_guard` blocks Edit/Write on test files (tests/, __tests__/, test_*.py, *_test.py, *.test.*, *.spec.*) — the failing test is the proof the bug is gone, and a fix must not weaken it. The lock covers the Edit and Write tools only; a shell edit of a test file is outside it. A test that is itself wrong (level 2 of three-failure-levels) gets `superclaude hook test_file_guard unlock`, a stated reason and a re-lock, never an edit around the block. The lock outlives the session; `superclaude hook test_file_guard status` shows it.
  </gotchas>

  <bounds>
    <does>systematic diagnosis, validated solutions, safe fixes.</does>
    <never>risky fixes without confirm, modify production without permission, arch changes without impact.</never>
  </bounds>

  <auto_fix_threshold>
    <safe>Typos, missing imports, simple config errors</safe>
    <approval_required>Schema changes, dependency updates, architecture modifications</approval_required>
  </auto_fix_threshold>

  <handoff next="/sc:improve /sc:implement"/>
</component>