---
description: Task reflection and validation using Serena MCP analysis capabilities
---
<component name="reflect" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:reflect
    <mission>Task reflection and validation using Serena MCP analysis capabilities</mission>
  </role>

  <syntax>/sc:reflect [--type task|session|completion] [--analyze] [--validate]</syntax>

  <triggers>
    <t>Task completion validation</t>
    <t>Session progress analysis</t>
    <t>Cross-session learning capture</t>
    <t>Quality gate verification</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Task state + session progress (Serena)</s>
    <s n="2">Validate: Adherence + completion quality</s>
    <s n="3">Reflect: Deep analysis + session insights</s>
    <s n="4">Document: Update metadata + capture learnings</s>
    <s n="5">Optimize: Process improvement recs</s>
  </flow>

  <mcp servers="serena:reflection|serena:memory"/>

  <tools>
    <t n="think_about_task_adherence">Goal alignment + deviation ID</t>
    <t n="think_about_collected_information">Completeness assessment</t>
    <t n="think_about_whether_you_are_done">Completion criteria eval</t>
    <t n="write_memory/read_memory">Cross-session persistence</t>
  </tools>

  <patterns>
    <p n="Task">Approach → goal alignment → deviation → correction</p>
    <p n="Session">Info gathering → completeness → quality → insights</p>
    <p n="Completion">Progress → criteria → remaining work → decision</p>
    <p n="Learning">Insights → persistence → enhanced understanding</p>
  </patterns>

  <examples>
    <ex i="--type task --analyze" o="Goal alignment validation"/>
    <ex i="--type session --validate" o="Session work quality"/>
    <ex i="--type completion" o="Completion readiness eval"/>
  </examples>

  <bounds will="comprehensive reflection|TodoWrite bridge|cross-session learning" wont="operate without Serena|override completion|bypass integrity"/>
</component>
