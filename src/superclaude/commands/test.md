---
description: Execute tests with coverage analysis and automated quality reporting
---
<component name="test" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:test
    <mission>Execute tests with coverage analysis and automated quality reporting</mission>
  </role>

  <syntax>/sc:test [target] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]</syntax>

  <triggers>
    <t>Test execution requests</t>
    <t>Coverage analysis needs</t>
    <t>Continuous testing + watch mode</t>
    <t>Test failure analysis</t>
  </triggers>

  <flow>
    <s n="1">Discover: Categorize tests via runner patterns</s>
    <s n="2">Configure: Environment + execution params</s>
    <s n="3">Execute: Run + real-time progress</s>
    <s n="4">Analyze: Coverage reports + failure diagnostics</s>
    <s n="5">Report: Actionable recs + quality metrics</s>
  </flow>

  <mcp servers="play:e2e"/>
  <personas p="qa-specialist"/>

  <tools>
    <t n="Bash">Test runner execution</t>
    <t n="Glob">Test discovery + patterns</t>
    <t n="Grep">Result parsing + failure analysis</t>
    <t n="Write">Coverage reports + summaries</t>
  </tools>

  <patterns>
    <p n="Discovery">Pattern categorization → runner selection</p>
    <p n="Coverage">Metrics → comprehensive reporting</p>
    <p n="E2E">Browser automation → cross-platform validation</p>
    <p n="Watch">File monitoring → continuous execution</p>
  </patterns>

  <examples>
    <ex i="/sc:test" o="All tests + basic coverage"/>
    <ex i="src/components --type unit --coverage" o="Targeted coverage"/>
    <ex i="--type e2e" o="Playwright browser testing"/>
    <ex i="--watch --fix" o="Continuous + auto-fix"/>
  </examples>

  <bounds will="execute existing tests|coverage reports|failure analysis" wont="generate test cases|modify framework config|destructive changes"/>
</component>
