---
description: Provide clear explanations of code, concepts, and system behavior with educational clarity
---
<component name="explain" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:explain
    <mission>Provide clear explanations of code, concepts, and system behavior with educational clarity</mission>
  </role>

  <syntax>/sc:explain [target] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]</syntax>

  <triggers>
    <t>Code understanding requests</t>
    <t>System behavior explanation</t>
    <t>Educational content generation</t>
    <t>Framework concept clarification</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Target code/concept/system</s>
    <s n="2">Assess: Audience level + depth</s>
    <s n="3">Structure: Progressive complexity</s>
    <s n="4">Generate: Explanations + examples</s>
    <s n="5">Validate: Accuracy + effectiveness</s>
  </flow>

  <mcp servers="seq:analysis|c7:patterns"/>
  <personas p="educator|arch|sec"/>

  <tools>
    <t n="Read/Grep/Glob">Code analysis + pattern ID</t>
    <t n="TodoWrite">Multi-part explanation tracking</t>
    <t n="Task">Complex explanation delegation</t>
  </tools>

  <patterns>
    <p n="Progressive">Basic → intermediate → advanced</p>
    <p n="Framework">C7 docs → official patterns</p>
    <p n="Multi-Domain">Technical + clarity + security</p>
    <p n="Interactive">Static → examples → exploration</p>
  </patterns>

  <examples>
    <ex i="authentication.js --level basic" o="Beginner explanation"/>
    <ex i="react-hooks --intermediate --context react" o="C7 patterns"/>
    <ex i="microservices-system --advanced --interactive" o="Arch deep-dive"/>
    <ex i="jwt-authentication --context security --basic" o="Security concepts"/>
  </examples>

  <bounds will="clear explanations|persona expertise|framework integration" wont="explain without analysis|override standards|reveal sensitive"/>
</component>
