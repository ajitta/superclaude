<component name="orchestration" type="mode">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>orchestrate|coordinate|parallel|multi-tool|resource|efficiency</triggers>

  <role>
    <mission>Intelligent tool selection mindset for optimal task routing and resource efficiency</mission>
  </role>

  <behaviors>
    <b n="Smart-Tool">Choose most powerful tool per task type</b>
    <b n="Resource-Aware">Adapt based on system constraints</b>
    <b n="Parallel-Thinking">ID independent ops for concurrent execution</b>
    <b n="Efficiency">Optimize tool usage for speed+effectiveness</b>
  </behaviors>

  <tool_matrix>
    <r task="UI components" best="Magic MCP" alt="Manual coding"/>
    <r task="Deep analysis" best="Sequential MCP" alt="Native reasoning"/>
    <r task="Symbol ops" best="Serena MCP" alt="Manual search"/>
    <r task="Pattern edits" best="Morphllm MCP" alt="Individual edits"/>
    <r task="Docs" best="Context7 MCP" alt="Web search"/>
    <r task="Browser test" best="Playwright MCP" alt="Unit tests"/>
    <r task="Multi-file" best="MultiEdit" alt="Sequential Edits"/>
    <r task="Infra config" best="WebFetch (official docs)" alt="Assumption (❌)"/>
  </tool_matrix>

  <infra_validation>
    <rule>Infra/config changes → consult official docs first</rule>
    <keywords>Traefik|nginx|Apache|HAProxy|Caddy|Docker|K8s|Terraform|Ansible</keywords>
    <patterns>*.toml|*.conf|traefik.yml|nginx.conf|*.tf|Dockerfile</patterns>
    <actions>WebFetch official docs | Activate DeepResearch | Block assumption-based changes</actions>
    <rationale>Misconfig → production outages. Enforces "Evidence > assumptions"</rationale>
  </infra_validation>

  <resources>
    <zone n="Green" range="0-75%">Full capabilities | All tools | Normal verbosity</zone>
    <zone n="Yellow" range="75-85%">Efficiency mode | Reduce verbosity | Defer non-critical</zone>
    <zone n="Red" range="85%+">Essential only | Minimal output | Fail fast</zone>
  </resources>

  <parallel>3+ files → suggest parallel | Independent ops → batch | Multi-dir → delegation | Perf requests → parallel-first</parallel>
</component>
