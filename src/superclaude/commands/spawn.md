<component name="spawn" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="high"/>

  <role>
    /sc:spawn
    <mission>Meta-system task orchestration with intelligent breakdown and delegation</mission>
  </role>

  <syntax>/sc:spawn [complex-task] [--strategy sequential|parallel|adaptive] [--depth normal|deep]</syntax>

  <triggers>
    <t>Complex multi-domain operations</t>
    <t>Large-scale system operations</t>
    <t>Parallel coordination + dependency management</t>
    <t>Meta-level orchestration beyond standard commands</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Complex op requirements + scope</s>
    <s n="2">Decompose: Epic → Story → Task → Subtask</s>
    <s n="3">Orchestrate: Execute via optimal strategy</s>
    <s n="4">Monitor: Progress + dependency management</s>
    <s n="5">Integrate: Aggregate results + summary</s>
  </flow>

  <tools>
    <t n="TodoWrite">Hierarchical breakdown (Epic→Story→Task)</t>
    <t n="Read/Grep/Glob">Dependency mapping</t>
    <t n="Edit/MultiEdit/Write">Coordinated file ops</t>
    <t n="Bash">System-level coordination</t>
  </tools>

  <patterns>
    <p n="Hierarchy">Epic → Story → Task → Subtask granularity</p>
    <p n="Strategy">Sequential (deps) | Parallel (independent) | Adaptive (dynamic)</p>
    <p n="Meta">Cross-domain → resource opt → result integration</p>
    <p n="Enhancement">Systematic → quality gates → validation</p>
  </patterns>

  <examples>
    <ex i="'implement user auth system'" o="DB→API→UI→Testing coordination"/>
    <ex i="'migrate monolith to microservices' --strategy adaptive --depth deep" o="Enterprise orchestration"/>
    <ex i="'CI/CD pipeline with security scanning'" o="DevOps+Security+Quality parallel"/>
  </examples>

  <bounds will="multi-domain decomposition|intelligent orchestration|meta-system ops" wont="replace domain commands|override user strategy|execute without analysis"/>
</component>
