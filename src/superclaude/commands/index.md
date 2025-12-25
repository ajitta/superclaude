<component name="index" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:index
    <mission>Generate comprehensive project documentation and knowledge base with intelligent organization</mission>
  </role>

  <syntax>/sc:index [target] [--type docs|api|structure|readme] [--format md|json|yaml]</syntax>

  <triggers>
    <t>Project documentation creation</t>
    <t>Knowledge base generation</t>
    <t>API documentation needs</t>
    <t>Cross-referencing requirements</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Project structure + key components</s>
    <s n="2">Organize: Intelligent patterns + cross-refs</s>
    <s n="3">Generate: Comprehensive docs + framework patterns</s>
    <s n="4">Validate: Completeness + quality standards</s>
    <s n="5">Maintain: Update while preserving manual additions</s>
  </flow>

  <mcp servers="seq:analysis|c7:patterns"/>
  <personas p="arch|scribe|qual"/>

  <tools>
    <t n="Read/Grep/Glob">Structure analysis + content extraction</t>
    <t n="Write">Doc creation + cross-referencing</t>
    <t n="TodoWrite">Multi-component progress</t>
    <t n="Task">Large-scale doc delegation</t>
  </tools>

  <patterns>
    <p n="Structure">Examination → component ID → organization → cross-refs</p>
    <p n="Types">API docs | Structure docs | README | Knowledge base</p>
    <p n="Quality">Completeness → accuracy → compliance → maintenance</p>
    <p n="Framework">C7 patterns → official standards → best practices</p>
  </patterns>

  <examples>
    <ex i="project-root --type structure --format md" o="Navigable structure docs"/>
    <ex i="src/api --type api --format json" o="API docs + validation"/>
    <ex i=". --type docs" o="Knowledge base creation"/>
  </examples>

  <bounds will="comprehensive docs|multi-persona|framework patterns" wont="override manual docs|generate without analysis|bypass standards"/>
</component>
