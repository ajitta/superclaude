---
description: Diagnose issues in code, builds, deployments and system behavior and propose how to resolve them; `--fix` writes a failing test and applies the change. On request only — the user's /sc:troubleshoot or a workflow step that names it. Not for a clear error with an obvious fix — fix it directly.
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
  5. Test: Write failing test reproducing exact bug (required before any fix) and commit it, so the proof outlives a reset
  6. Fix: Apply single change addressing root cause — no "while I'm here" fixes
  7. Verify: Failing test passes, all existing tests pass, no regressions
  </flow>

  <flags>
  - --type bug|build|performance|deployment: problem class: bug starts from reproduction and stack trace, build from compiler and dependency output, performance from a measurement, deployment from environment and config.
  - --trace: trace the data flow and execution path up to the failure before naming a cause.
  - --fix: run the Test, Fix and Verify steps; without it, stop after the Confirm step and propose the fix. A fix in the approval-required tier of the auto-fix threshold still waits for confirmation.
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
  - fix-not-test: between the Test and Verify steps the failing test is read-only for the fix — a widened assertion, a skip marker or a deleted case makes the fix look done without the bug being gone. A test that is itself wrong (level 2 of three-failure-levels) is re-examined with a stated reason before any edit to it, never edited around a red run.
  - three-failure-levels: a failure sits at one of three levels — (1) bug in the code → fix it; (2) bug in expectations, i.e. the test or the requirement is itself wrong → re-examine it before "fixing" working code; (3) bug in the process → structural cause, the most valuable to record. Level 2 is the one most often skipped, and skipping it turns a wrong requirement into a wrong fix.
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