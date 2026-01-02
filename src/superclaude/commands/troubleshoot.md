---
description: Diagnose and resolve issues in code, builds, deployments, and system behavior
---
<component name="troubleshoot" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5"/>

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

  <examples>

| Input | Output |
|-------|--------|
| `'Null pointer in user service' --type bug --trace` | Root cause + targeted fix |
| `'TypeScript compilation errors' --type build --fix` | Auto-apply safe fixes |
| `'API response times degraded' --type performance` | Bottleneck + optimization |
| `'Service not starting' --type deployment --trace` | Environment analysis |

  </examples>

  <bounds will="systematic diagnosis|validated solutions|safe fixes" wont="risky fixes without confirm|modify production without permission|arch changes without impact"/>
</component>
