---
description: Generate focused documentation for components, functions, APIs, and features
---
<component name="document" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:document
    <mission>Generate focused documentation for components, functions, APIs, and features</mission>
  </role>

  <syntax>/sc:document [target] [--type inline|external|api|guide] [--style brief|detailed]</syntax>

  <triggers>
    <t>Component/function documentation</t>
    <t>API reference generation</t>
    <t>Code comments + inline docs</t>
    <t>User guides + technical docs</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Component structure + interfaces</s>
    <s n="2">Identify: Audience + requirements</s>
    <s n="3">Generate: Content by type + style</s>
    <s n="4">Format: Consistent structure</s>
    <s n="5">Integrate: Project doc ecosystem</s>
  </flow>

  <tools>
    <t n="Read">Component + existing docs</t>
    <t n="Grep">Reference extraction</t>
    <t n="Write">Doc file creation</t>
    <t n="Glob">Multi-file organization</t>
  </tools>

  <patterns>
    <p n="Inline">Code analysis → JSDoc/docstring</p>
    <p n="API">Interface extraction → reference + examples</p>
    <p n="Guide">Feature analysis → tutorial content</p>
    <p n="External">Overview → specs → integration</p>
  </patterns>

  <examples>
    <ex i="src/auth/login.js --type inline" o="JSDoc comments"/>
    <ex i="src/api --type api --detailed" o="API reference"/>
    <ex i="payment-module --type guide --brief" o="User docs"/>
    <ex i="components/ --type external" o="Component library docs"/>
  </examples>

  <bounds will="focused docs|multi-format|ecosystem integration" wont="doc without analysis|override standards|expose sensitive details"/>
</component>
