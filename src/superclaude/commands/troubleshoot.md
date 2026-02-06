---
description: Diagnose and resolve issues in code, builds, deployments, and system behavior
---
<component name="troubleshoot" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:troubleshoot
    <mission>Diagnose and resolve issues in code, builds, deployments, and system behavior</mission>
  </role>

  <syntax>/sc:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]</syntax>

  <triggers>
    - Code defects + runtime errors
    - Build failure analysis
    - Performance issue diagnosis
    - Deployment problem debugging
  </triggers>

  <flow>
    1. Analyze: Issue description + system state
    2. Investigate: Root causes via pattern analysis
    3. Debug: Structured procedures + log examination
    4. Propose: Solution + impact assessment
    5. Resolve: Apply fixes + verify effectiveness
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

  <checklist note="SHOULD complete all">
    - [ ] Root cause identified
    - [ ] Diagnostic evidence collected
    - [ ] Solution proposed with impact assessment
    - [ ] Fix validated (if --fix applied)
  </checklist>

  <examples>

| Input | Output |
|-------|--------|
| `'Null pointer in user service' --type bug --trace` | Root cause + targeted fix |
| `'TypeScript compilation errors' --type build --fix` | Auto-apply safe fixes |
| `'API response times degraded' --type performance` | Bottleneck + optimization |
| `'Service not starting' --type deployment --trace` | Environment analysis |

  </examples>

  <bounds will="systematic diagnosis|validated solutions|safe fixes" wont="risky fixes without confirm|modify production without permission|arch changes without impact"/>

  <boundaries type="conditional" critical="true">
    <rule>Without --fix: produce diagnostic report, then complete</rule>
    <rule>With --fix: Apply safe fixes only (execution)</rule>
    <rule>Risky fixes require explicit user approval</rule>
    <output>Diagnostic report; fixes only with --fix flag</output>
  </boundaries>

  <auto_fix_threshold>
    <safe>Typos, missing imports, simple config errors</safe>
    <approval_required>Schema changes, dependency updates, architecture modifications</approval_required>
  </auto_fix_threshold>

  <handoff>
    <next command="/sc:improve">For systematic code quality fixes</next>
    <next command="/sc:implement">For implementing identified solutions</next>
    <format>Include diagnostic context for targeted remediation</format>
  </handoff>
</component>
