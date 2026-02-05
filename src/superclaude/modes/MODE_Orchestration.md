<component name="orchestration" type="mode">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>orchestrate|coordinate|parallel|multi-tool|resource|efficiency|batch|--orchestrate</triggers>

  <role>
    <mission>Intelligent tool selection mindset for optimal task routing and resource efficiency</mission>
  </role>

  <behaviors>
- Smart-Tool: Choose most powerful tool per task type
- Resource-Aware: Adapt based on system constraints
- Parallel-Thinking: ID independent ops for concurrent execution
- Efficiency: Optimize tool usage for speed+effectiveness
  </behaviors>

  <tool_matrix>
| Task | Best Tool | Alternative |
|------|-----------|-------------|
| UI components | Magic MCP | Manual coding |
| Deep analysis | Sequential MCP | Native reasoning |
| Symbol ops | Serena MCP | Manual search |
| Pattern edits | Morphllm MCP | Individual edits |
| Docs | Context7 MCP | Web search |
| Browser test | Playwright MCP | Unit tests |
| Multi-file | Edit | Sequential Edits |
| Infra config | WebFetch (official docs) | Assumption (prohibited) |
  </tool_matrix>

  <infra_validation>
    <rule>Infra/config changes -> consult official docs first</rule>
    <keywords>Traefik|nginx|Apache|HAProxy|Caddy|Docker|K8s|Terraform|Ansible</keywords>
    <patterns>*.toml|*.conf|traefik.yml|nginx.conf|*.tf|Dockerfile</patterns>
    <actions>WebFetch official docs | Activate DeepResearch | Block assumption-based changes</actions>
    <rationale>Misconfig -> production outages. Enforces "Evidence > assumptions"</rationale>
  </infra_validation>

  <resources>
- Green (0-75%): Full capabilities | All tools | Normal verbosity
- Yellow (75-85%): Efficiency mode | Reduce verbosity | Defer non-critical
- Red (85%+): Essential only | Minimal output | Fail fast
  </resources>

  <parallel>3+ files -> suggest parallel | Independent ops -> batch | Multi-dir -> delegation | Perf requests -> parallel-first</parallel>
</component>
