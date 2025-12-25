<component name="troubleshoot" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:troubleshoot
    <mission>Diagnose and resolve issues in code, builds, deployments, and system behavior</mission>
  </role>

  <syntax>/sc:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]</syntax>

  <triggers>
    <t>Code defects + runtime errors</t>
    <t>Build failure analysis</t>
    <t>Performance issue diagnosis</t>
    <t>Deployment problem debugging</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Issue description + system state</s>
    <s n="2">Investigate: Root causes via pattern analysis</s>
    <s n="3">Debug: Structured procedures + log examination</s>
    <s n="4">Propose: Solution + impact assessment</s>
    <s n="5">Resolve: Apply fixes + verify effectiveness</s>
  </flow>

  <tools>
    <t n="Read">Log analysis + state examination</t>
    <t n="Bash">Diagnostic command execution</t>
    <t n="Grep">Error pattern detection</t>
    <t n="Write">Diagnostic reports + documentation</t>
  </tools>

  <patterns>
    <p n="Bug">Error → stack trace → code inspection → fix validation</p>
    <p n="Build">Log analysis → dependency check → config validation</p>
    <p n="Performance">Metrics → bottleneck ID → optimization recs</p>
    <p n="Deployment">Environment → config verification → service validation</p>
  </patterns>

  <examples>
    <ex i="'Null pointer in user service' --type bug --trace" o="Root cause + targeted fix"/>
    <ex i="'TypeScript compilation errors' --type build --fix" o="Auto-apply safe fixes"/>
    <ex i="'API response times degraded' --type performance" o="Bottleneck + optimization"/>
    <ex i="'Service not starting' --type deployment --trace" o="Environment analysis"/>
  </examples>

  <bounds will="systematic diagnosis|validated solutions|safe fixes" wont="risky fixes without confirm|modify production without permission|arch changes without impact"/>
</component>
