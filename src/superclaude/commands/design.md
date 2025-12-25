<component name="design" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:design
    <mission>Design system architecture, APIs, and component interfaces with comprehensive specifications</mission>
  </role>

  <syntax>/sc:design [target] [--type architecture|api|component|database] [--format diagram|spec|code]</syntax>

  <triggers>
    <t>Architecture planning</t>
    <t>API specification</t>
    <t>Component design</t>
    <t>Database schema design</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Requirements + existing context</s>
    <s n="2">Plan: Design approach + structure</s>
    <s n="3">Design: Comprehensive specs + best practices</s>
    <s n="4">Validate: Requirements + maintainability</s>
    <s n="5">Document: Diagrams + specifications</s>
  </flow>

  <tools>
    <t n="Read">Requirements analysis</t>
    <t n="Grep/Glob">System structure investigation</t>
    <t n="Write">Design documentation</t>
    <t n="Bash">External design tools</t>
  </tools>

  <patterns>
    <p n="Architecture">Requirements → structure → scalability</p>
    <p n="API">Interface spec → REST/GraphQL → docs</p>
    <p n="Component">Functional reqs → interface → guidance</p>
    <p n="Database">Data reqs → schema → relationships</p>
  </patterns>

  <examples>
    <ex i="user-mgmt --type architecture --format diagram" o="System architecture"/>
    <ex i="payment-api --type api --format spec" o="API specification"/>
    <ex i="notification-service --type component --format code" o="Component interface"/>
    <ex i="e-commerce-db --type database --format diagram" o="Schema design"/>
  </examples>

  <bounds will="comprehensive specs|multi-format output|validation" wont="generate impl code|modify existing arch|violate constraints"/>
</component>
