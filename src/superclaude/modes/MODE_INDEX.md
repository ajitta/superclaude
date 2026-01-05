<component name="mode-index" type="routing">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>mode|--brainstorm|--bs|--research|--orchestrate|--task-manage|--uc|--ultracompressed|--introspect|business|panel</triggers>

  <role>
    <mission>Mode routing index - triggers to detailed file mapping</mission>
    <note>Detailed behaviors loaded dynamically via context_loader.py hook</note>
  </role>

  <mode_index>
| Mode | Triggers | File |
|------|----------|------|
| Brainstorming | brainstorm, explore, maybe, thinking about, discuss, not sure, --brainstorm, --bs | MODE_Brainstorming.md |
| DeepResearch | /sc:research, investigate, explore, discover, analyze, --research | MODE_DeepResearch.md |
| Orchestration | orchestrate, coordinate, parallel, multi-tool, resource, efficiency, --orchestrate | MODE_Orchestration.md |
| TaskManagement | task, manage, delegate, phase, milestone, --task-manage | MODE_Task_Management.md |
| TokenEfficiency | compress, efficient, --uc, --ultracompressed, token, brevity | MODE_Token_Efficiency.md |
| Introspection | introspect, reflect, analyze reasoning, meta, self-analysis, --introspect | MODE_Introspection.md |
| BusinessPanel | business, panel, expert, strategy, christensen, porter, drucker, godin, taleb | MODE_Business_Panel.md |
  </mode_index>

  <tool_index note="Quick MCP selection">
| Task | Tool |
|------|------|
| UI components | Magic MCP |
| Deep analysis | Sequential MCP |
| Symbol ops | Serena MCP |
| Pattern edits | Morphllm MCP |
| Docs lookup | Context7 MCP |
| Browser test | Playwright MCP |
| Web search | Tavily MCP |
  </tool_index>

  <context_thresholds>
| Level | Tokens | Action |
|-------|--------|--------|
| Green | 0-75% | Full capabilities |
| Yellow | 75-85% | Efficiency mode |
| Red | 85%+ | Auto --uc |
  </context_thresholds>
</component>
