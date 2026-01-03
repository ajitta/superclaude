---
name: mode-index
type: mode
cache: pinned
triggers: [mode, --brainstorm, --research, --orchestrate, --task-manage, --uc, --introspect, business]
---
<component name="mode-index" type="routing">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>mode|--brainstorm|--research|--orchestrate|--task-manage|--uc|--introspect|business|panel</triggers>

  <role>
    <mission>Mode routing index - triggers to detailed file mapping</mission>
    <note>Detailed behaviors loaded dynamically via context_loader.py hook</note>
  </role>

  <mode_index>
| Mode | Triggers | File |
|------|----------|------|
| Brainstorming | maybe, thinking about, explore, --brainstorm | MODE_Brainstorming.md |
| DeepResearch | investigate, research, analyze, --research | MODE_DeepResearch.md |
| Orchestration | parallel, multi-tool, efficiency, --orchestrate | MODE_Orchestration.md |
| TaskManagement | task, delegate, milestone, --task-manage | MODE_TaskManagement.md |
| TokenEfficiency | --uc, compress, efficient, context >75% | MODE_TokenEfficiency.md |
| Introspection | reflect, meta, self-analysis, --introspect | MODE_Introspection.md |
| BusinessPanel | business, strategy, expert, panel | MODE_BusinessPanel.md |
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
