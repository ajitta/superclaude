<component name="orchestration" type="mode">
  <role>
    <mission>Intelligent tool selection mindset for optimal task routing and resource efficiency</mission>
  </role>

  <behaviors>
- Smart-Tool: Choose most powerful tool per task type
- Resource-Aware: Adapt based on system constraints
- Parallel-Thinking: ID independent ops for concurrent execution
- Efficiency: Optimize tool usage for speed+effectiveness
  </behaviors>

  ## Tool Matrix
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

  ## Infra Validation
  Infra/config changes → consult official docs first
  Keywords: Traefik|nginx|Apache|HAProxy|Caddy|Docker|K8s|Terraform|Ansible
  Actions: WebFetch official docs | Activate DeepResearch | Block assumption-based changes

  ## Parallel Rules
  3+ files → suggest parallel | Independent ops → batch | Multi-dir → delegation

  <bounds will="intelligent tool selection|parallel optimization|resource efficiency" wont="use wrong tool for task|ignore system constraints|sequential when parallel possible" fallback="Revert to default behavior when inapplicable"/>

  <handoff next="/sc:task /sc:spawn /sc:select-tool"/>
</component>
