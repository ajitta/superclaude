<component name="build" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:build
    <mission>Build, compile, and package projects with intelligent error handling and optimization</mission>
  </role>

  <syntax>/sc:build [target] [--type dev|prod|test] [--clean] [--optimize] [--verbose]</syntax>

  <triggers>
    <t>Project compilation + packaging</t>
    <t>Build optimization needs</t>
    <t>Build error debugging</t>
    <t>Deployment artifact preparation</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Structure, configs, deps</s>
    <s n="2">Validate: Environment + toolchain</s>
    <s n="3">Execute: Build + real-time monitoring</s>
    <s n="4">Optimize: Artifacts + bundle size</s>
    <s n="5">Package: Artifacts + reports</s>
  </flow>

  <mcp servers="play:validation"/>
  <personas p="devops"/>

  <tools>
    <t n="Bash">Build execution</t>
    <t n="Read">Config analysis</t>
    <t n="Grep">Error parsing</t>
    <t n="Glob">Artifact discovery</t>
    <t n="Write">Build reports</t>
  </tools>

  <patterns>
    <p n="Environment">dev|prod|test → appropriate config</p>
    <p n="Error">Build failures → diagnostic + resolution</p>
    <p n="Optimize">Artifact analysis → size reduction</p>
  </patterns>

  <examples>
    <ex i="/sc:build" o="Default build + report"/>
    <ex i="--type prod --clean --optimize" o="Production artifacts"/>
    <ex i="frontend --verbose" o="Detailed component build"/>
    <ex i="--type dev --validate" o="Dev build + Playwright validation"/>
  </examples>

  <bounds will="execute build|error analysis|optimization recs" wont="modify build config|install deps|deploy"/>
</component>
