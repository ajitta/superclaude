<component name="mode-index" type="routing">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>mode|--brainstorm|--bs|--research|--orchestrate|--task-manage|--uc|--ultracompressed|--introspect|business|panel|persona|arch|fe|be|sec|qa|ops|pm|perf</triggers>

  <role>
    <mission>Mode routing index - triggers to detailed file mapping</mission>
    <note>Detailed behaviors loaded dynamically via context_loader.py hook</note>
  </role>

  <mode_index>
| Mode | Triggers | File |
|------|----------|------|
| Brainstorming | brainstorm, ideate, explore, explore ideas, maybe, thinking about, discuss, not sure, --brainstorm, --bs | MODE_Brainstorming.md |
| DeepResearch | deep research, /sc:research, investigate, investigate thoroughly, discover, deep-research, --research | MODE_DeepResearch.md |
| Orchestration | orchestrate, coordinate, parallel, multi-tool, resource, efficiency, batch, --orchestrate | MODE_Orchestration.md |
| TaskManagement | task, manage, task manage, delegate, phase, milestone, --task-manage | MODE_Task_Management.md |
| TokenEfficiency | compress, efficient, token, token efficient, brevity, --uc, --ultracompressed | MODE_Token_Efficiency.md |
| Introspection | introspect, reflect, analyze reasoning, meta-cognitive, self-analysis, --introspect | MODE_Introspection.md |
| BusinessPanel | business, panel, expert, strategy, business panel, expert panel, strategy panel, christensen, porter, drucker, godin, taleb | MODE_Business_Panel.md |
  </mode_index>

  <tool_index note="Quick MCP selection with fallbacks">
| Task | Tool | Fallback |
|------|------|----------|
| UI components | Magic MCP | Write (native) |
| Deep analysis | Sequential MCP | Native reasoning |
| Symbol ops | Serena MCP | Native search |
| Pattern edits | Morphllm MCP | Edit (native) |
| Docs lookup | Context7 MCP | Tavily/WebSearch |
| Browser test | Playwright MCP | Native browser |
| Web search | Tavily MCP | WebSearch (native) |
| Perf metrics | DevTools MCP | Playwright |
  </tool_index>

  <sequential_priority note="When multiple modes trigger Sequential MCP">
    DeepResearch > TaskManagement > Orchestration
  </sequential_priority>

  <conflict_resolution note="Multi-mode trigger handling">
| Scenario | Resolution | Example |
|----------|------------|---------|
| 2+ modes trigger | Higher priority wins | research + task → DeepResearch |
| Same priority | User intent determines | Explicit flag takes precedence |
| Context pressure (>85%) | TokenEfficiency overrides | Any mode + Red context → --uc first |
| Explicit flag | Always wins | --brainstorm overrides auto-detection |

    <rules>
      1. Explicit user flag > auto-detected mode
      2. Safety modes (--safe-mode, --validate) > all other modes
      3. TokenEfficiency activates as overlay, not replacement
      4. Sequential MCP: Only highest-priority mode gets budget
      5. Tie-break: Ask user via AskUserQuestion
    </rules>

    <examples>
      - `--research --task-manage` → DeepResearch (higher priority)
      - `--brainstorm` at 90% context → Brainstorming + auto --uc overlay
      - `--effort high --no-mcp` → --no-mcp wins (explicit override)
      - Ambiguous intent → Prompt: "Multiple approaches possible. Prefer research or task management?"
    </examples>
  </conflict_resolution>

  <context_thresholds>
| Level | Tokens | Action |
|-------|--------|--------|
| Green | 0-75% | Full capabilities |
| Yellow | 75-85% | Efficiency mode |
| Red | 85%+ | Auto --uc |
  </context_thresholds>

  <persona_index note="Agent abbreviations for <personas p='...'/>">
| Abbr | Agent | Domain |
|------|-------|--------|
| arch | system-architect | Architecture, scalability |
| fe | frontend-architect | UI, accessibility, React/Vue |
| be | backend-architect | API, database, security |
| sec | security-engineer | OWASP, vulnerabilities |
| qa | quality-engineer | Testing, coverage |
| ops | devops-architect | CI/CD, Kubernetes |
| pm | pm-agent | Orchestration, docs |
| perf | performance-engineer | Optimization, profiling |
| refactor | refactoring-expert | Tech debt, SOLID |
| root | root-cause-analyst | Debug, hypothesis |
  </persona_index>
</component>
