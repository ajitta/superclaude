<component name="spec-panel" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="high"/>

  <role>
    /sc:spec-panel
    <mission>Multi-expert specification review and improvement using renowned software engineering experts</mission>
  </role>

  <syntax>/sc:spec-panel [spec|@file] [--mode discussion|critique|socratic] [--experts "name1,name2"] [--focus requirements|architecture|testing|compliance] [--iterations N]</syntax>

  <triggers>
    <t>Specification review requests</t>
    <t>Expert panel analysis</t>
    <t>Requirements quality assessment</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Parse spec content</s>
    <s n="2">Assemble: Select relevant experts</s>
    <s n="3">Review: Multi-expert analysis</s>
    <s n="4">Collaborate: Expert dialogue</s>
    <s n="5">Synthesize: Improvement roadmap</s>
  </flow>

  <mcp servers="seq:coordination|c7:patterns"/>
  <personas p="tech-writer|sys-arch|qual-eng"/>

  <experts>
    <e n="Wiegers" domain="Requirements quality, SMART" q="How would you validate this?"/>
    <e n="Adzic" domain="BDD, Given/When/Then" q="Concrete examples?"/>
    <e n="Cockburn" domain="Use cases, goals" q="Primary stakeholder?"/>
    <e n="Fowler" domain="API design, patterns" q="Separation of concerns?"/>
    <e n="Nygard" domain="Production reliability" q="What happens when this fails?"/>
    <e n="Newman" domain="Microservices" q="Service evolution?"/>
    <e n="Crispin" domain="Testing strategies" q="How to validate?"/>
    <e n="Hightower" domain="Cloud native, K8s" q="Cloud deployment?"/>
  </experts>

  <modes>
    <m n="discussion">Sequential expert dialogue building insights</m>
    <m n="critique">Issue → Severity → Recommendation → Priority</m>
    <m n="socratic">Deep questioning to surface assumptions</m>
  </modes>

  <focus_areas>
    <f n="requirements" experts="Wiegers,Adzic,Cockburn">Clarity, testability, acceptance</f>
    <f n="architecture" experts="Fowler,Newman,Nygard">Interfaces, boundaries, patterns</f>
    <f n="testing" experts="Crispin,Adzic">Strategy, edge cases, validation</f>
    <f n="compliance" experts="Wiegers,Nygard">Security, regulatory, audit</f>
  </focus_areas>

  <examples>
    <ex i="@auth_api.yml --mode critique --focus requirements,architecture" o="Multi-focus review"/>
    <ex i="'user story' --mode discussion --experts 'wiegers,adzic'" o="Expert dialogue"/>
    <ex i="@system.yml --mode socratic --iterations 3" o="Deep questioning"/>
  </examples>

  <bounds will="expert-level review|actionable recs|multi-mode analysis" wont="replace human judgment|modify without consent|legal guarantees"/>
</component>
