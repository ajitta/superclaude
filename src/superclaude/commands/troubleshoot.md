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
    1. Analyze: Issue description + system state
    2. Investigate: Root causes via pattern analysis
    3. Debug: Structured procedures + log examination (max 3 hypothesis-test cycles)
    4. Escalate: If no root cause after 3 rounds → summarize hypotheses + evidence → ask user for guidance
    5. Propose: Solution + impact assessment
    6. Resolve: Apply fixes + verify effectiveness
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

  <mcp servers="seq"/>
  <personas p="root|devops"/>


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

  <bounds will="systematic diagnosis|validated solutions|safe fixes" wont="risky fixes without confirm|modify production without permission|arch changes without impact" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="conditional">Without --fix: produce diagnostic report, then complete | With --fix: Apply safe fixes only (execution) | Risky fixes require explicit user approval → Output: Diagnostic report; fixes only with --fix flag</boundaries>


  <auto_fix_threshold>
    <safe>Typos, missing imports, simple config errors</safe>
    <approval_required>Schema changes, dependency updates, architecture modifications</approval_required>
  </auto_fix_threshold>

  <handoff next="/sc:improve /sc:implement"/>
</component>
