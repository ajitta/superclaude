---
description: Diagnose and resolve issues in code, builds, deployments, and system behavior
---
<component name="troubleshoot" type="command">

  <role>
    /sc:troubleshoot
    <mission>Diagnose and resolve issues in code, builds, deployments, and system behavior</mission>
  </role>

  <syntax>/sc:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]</syntax>

  <flow>
    1. Reproduce: Confirm failure — read full error, identify exact trigger, verify it's consistent
    2. Investigate: Check git log/diff, trace data flow, find working examples
    3. Hypothesize: Form specific hypothesis ("X causes Y because Z") — max 3 cycles before escalating to user
    4. Confirm: Test hypothesis by changing one variable at a time; check environment before code
    5. Test: Write failing test that reproduces the exact bug (required before any fix)
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
|-------|--------|
| `'Null pointer in user service' --type bug --trace` | Root cause + targeted fix |
| `'TypeScript compilation errors' --type build --fix` | Auto-apply safe fixes |
| `'API response times degraded' --type performance` | Bottleneck + optimization |
| `'Service not starting' --type deployment --trace` | Environment analysis |

  <example name="symptom-only-fix" type="error-path">
    <input>/sc:troubleshoot 'users report slow page' --fix (applies caching without profiling)</input>
    <why_wrong>Fixing symptoms without diagnosis. Slow page could be N+1 queries, not a caching issue.</why_wrong>
    <correct>/sc:troubleshoot 'users report slow page' --trace first → identify bottleneck → then targeted fix</correct>
  </example>

  </examples>

  <token_note>Medium-high consumption — diagnostic cycles use significant context; limit with --type for focused diagnosis</token_note>

  <bounds will="systematic diagnosis|validated solutions|safe fixes" wont="risky fixes without confirm|modify production without permission|arch changes without impact" fallback="Ask user for guidance when uncertain" type="conditional">

    Without --fix: produce diagnostic report, then complete | With --fix: Apply safe fixes only (execution) | Risky fixes require explicit user approval → Output: Diagnostic report; fixes only with --fix flag

  </bounds>

  <auto_fix_threshold>
    <safe>Typos, missing imports, simple config errors</safe>
    <approval_required>Schema changes, dependency updates, architecture modifications</approval_required>
  </auto_fix_threshold>

  <handoff next="/sc:improve /sc:implement"/>
</component>
