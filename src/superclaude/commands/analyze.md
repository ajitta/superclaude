---
description: Comprehensive code analysis across quality, security, performance, and architecture domains
---
<component name="analyze" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:analyze
    <mission>Comprehensive code analysis across quality, security, performance, and architecture domains</mission>
  </role>

  <syntax>/sc:analyze [target] [--focus quality|security|performance|architecture] [--depth quick|deep] [--format text|json|report]</syntax>

  <triggers>
    <t>Code quality assessment</t>
    <t>Security vulnerability scanning</t>
    <t>Performance bottleneck identification</t>
    <t>Architecture review + tech debt</t>
  </triggers>

  <flow>
    <s n="1">Discover: Categorize files by language</s>
    <s n="2">Scan: Domain-specific analysis</s>
    <s n="3">Evaluate: Prioritized findings + severity</s>
    <s n="4">Recommend: Actionable guidance</s>
    <s n="5">Report: Metrics + roadmap</s>
  </flow>

  <tools>
    <t n="Glob">File discovery</t>
    <t n="Grep">Pattern analysis</t>
    <t n="Read">Source inspection</t>
    <t n="Bash">External tools</t>
    <t n="Write">Report generation</t>
  </tools>

  <patterns>
    <p n="Domain">Quality|Security|Perf|Arch → specialized assessment</p>
    <p n="Recognition">Language detect → appropriate techniques</p>
    <p n="Severity">Issue classification → prioritized recs</p>
  </patterns>

  <examples>
    <ex i="/sc:analyze" o="Multi-domain project report"/>
    <ex i="src/auth --focus security --deep" o="Vulnerability assessment"/>
    <ex i="--focus performance --format report" o="Bottleneck analysis"/>
    <ex i="src/components --focus quality --quick" o="Code smell detection"/>
  </examples>

  <bounds will="static analysis|severity-rated findings|detailed reports" wont="dynamic/runtime analysis|modify code|analyze external deps"/>
</component>
