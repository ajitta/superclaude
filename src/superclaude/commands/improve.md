---
description: Apply systematic improvements to code quality, performance, and maintainability
---
<component name="improve" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:improve
    <mission>Apply systematic improvements to code quality, performance, and maintainability</mission>
  </role>

  <syntax>/sc:improve [target] [--type quality|performance|maintainability|style] [--safe] [--interactive]</syntax>

  <triggers>
    <t>Code quality enhancement requests</t>
    <t>Performance optimization needs</t>
    <t>Maintainability + tech debt reduction</t>
    <t>Best practices enforcement</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Improvement opportunities + quality issues</s>
    <s n="2">Plan: Approach + persona activation</s>
    <s n="3">Execute: Systematic improvements + best practices</s>
    <s n="4">Validate: Functionality preservation + quality</s>
    <s n="5">Document: Summary + future recommendations</s>
  </flow>

  <mcp servers="seq:analysis|c7:patterns"/>
  <personas p="arch|perf|qual|sec"/>

  <tools>
    <t n="Read/Grep/Glob">Code analysis + opportunity ID</t>
    <t n="Edit/MultiEdit">Safe modification + refactoring</t>
    <t n="TodoWrite">Multi-file progress tracking</t>
    <t n="Task">Large-scale improvement delegation</t>
  </tools>

  <patterns>
    <p n="Quality">Analysis → tech debt ID → refactoring</p>
    <p n="Performance">Profiling → bottleneck ID → optimization</p>
    <p n="Maintainability">Structure → complexity reduction → docs</p>
    <p n="Security">Vulnerability → pattern application → validation</p>
  </patterns>

  <examples>
    <ex i="src/ --type quality --safe" o="Systematic quality + safe refactor"/>
    <ex i="api-endpoints --type performance --interactive" o="Bottleneck analysis"/>
    <ex i="legacy-modules --type maintainability --preview" o="Structure improvement"/>
    <ex i="auth-service --type security --validate" o="Security hardening"/>
  </examples>

  <bounds will="systematic improvements|multi-persona|safe refactoring" wont="risky changes without confirm|arch changes without impact analysis|override standards"/>
</component>
