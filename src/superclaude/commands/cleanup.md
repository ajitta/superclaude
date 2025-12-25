<component name="cleanup" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:cleanup
    <mission>Systematically clean up code, remove dead code, and optimize project structure</mission>
  </role>

  <syntax>/sc:cleanup [target] [--type code|imports|files|all] [--safe|--aggressive] [--interactive]</syntax>

  <triggers>
    <t>Code maintenance + tech debt</t>
    <t>Dead code removal</t>
    <t>Project structure improvement</t>
    <t>Codebase hygiene</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Cleanup opportunities + safety</s>
    <s n="2">Plan: Choose approach + activate personas</s>
    <s n="3">Execute: Systematic dead code detection</s>
    <s n="4">Validate: Ensure no functionality loss</s>
    <s n="5">Report: Summary + maintenance recs</s>
  </flow>

  <mcp servers="seq:analysis|c7:patterns"/>
  <personas p="arch|qual|sec"/>

  <tools>
    <t n="Read/Grep/Glob">Analysis + pattern detection</t>
    <t n="Edit/MultiEdit">Safe modification</t>
    <t n="TodoWrite">Progress tracking</t>
    <t n="Task">Large-scale delegation</t>
  </tools>

  <patterns>
    <p n="DeadCode">Usage analysis → safe removal</p>
    <p n="Imports">Dependency analysis → optimization</p>
    <p n="Structure">Arch analysis → modular improvements</p>
    <p n="Safety">Pre/during/post checks</p>
  </patterns>

  <examples>
    <ex i="src/ --type code --safe" o="Conservative cleanup"/>
    <ex i="--type imports --preview" o="Unused import analysis"/>
    <ex i="--type all --interactive" o="Multi-domain with guidance"/>
    <ex i="components/ --aggressive" o="Thorough cleanup"/>
  </examples>

  <bounds will="systematic cleanup|safety validation|intelligent algorithms" wont="remove without analysis|override exclusions|compromise functionality"/>
</component>
