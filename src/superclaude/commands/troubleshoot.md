---
description: Diagnose + resolve issues in code, builds, deployments, system behavior. Use when user types `/sc:troubleshoot` or describes intermittent failure, recurring symptom, or cross-system issue needing hypothesis-driven investigation. Do NOT auto-trigger on clear error with obvious fix, syntax errors, or single-file bugs — those get direct fix.
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
  5. Test: Write failing test reproducing exact bug (required before any fix)
  6. Fix: Apply single change addressing root cause — no "while I'm here" fixes
  7. Verify: Failing test passes, all existing tests pass, no regressions
  </flow>

  <tools>
  - Read: Log analysis + state examination
  - Bash: Diagnostic command execution
  - Grep: Error pattern detection
  - Write: Diagnostic reports + documentation
  </tools>

  <patterns>
    - Bug: Error → stack trace → code inspection → fix validation
    - Build: Log analysis → dependency check → config validation
    - Performance: Metrics → bottleneck ID → optimization recs
    - Deployment: Environment → config verification → service validation
  </patterns>


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
  - seq-loop: If sequential thinking reaches same conclusion twice on same question, terminate that analysis branch, move to next topic.
  </gotchas>

  <bounds>
    <does>systematic diagnosis, validated solutions, safe fixes.</does>
    <never>risky fixes without confirm, modify production without permission, arch changes without impact.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <auto_fix_threshold>
    <safe>Typos, missing imports, simple config errors</safe>
    <approval_required>Schema changes, dependency updates, architecture modifications</approval_required>
  </auto_fix_threshold>

  <handoff next="/sc:improve /sc:implement"/>
</component>