<component name="flags" type="core" priority="high">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>flag|--|mode|mcp|think|effort|delegate</triggers>

  <role>
    <mission>Behavioral flags for Claude Code execution modes and tool selection</mission>
  </role>

  <modes>
| Flag | Trigger | Effect |
|------|---------|--------|
| `--brainstorm` | vague requests, 'maybe', 'thinking about' | Collaborative discovery, probing questions |
| `--introspect` | self-analysis, error recovery, meta-cognition | Expose thinking (🤔🎯⚡📊💡) |
| `--task-manage` | >3 steps, >2 dirs, >3 files | Delegation, progressive enhancement |
| `--orchestrate` | multi-tool, perf constraints, parallel ops | Tool matrix optimization, parallel thinking |
| `--token-efficient` | context >75%, large ops, --uc | Symbol communication, 30-50% reduction |
  </modes>

  <mcp>
| Flag | Trigger | Effect |
|------|---------|--------|
| `--c7\|--context7` | imports, frameworks, official docs | Context7: curated docs, patterns |
| `--seq\|--sequential` | complex debug, system design | Sequential: multi-step reasoning |
| `--magic` | /ui, /21, design systems | Magic: 21st.dev UI components |
| `--morph\|--morphllm` | bulk transforms, pattern edits | Morphllm: multi-file patterns |
| `--serena` | symbol ops, project memory | Serena: semantic understanding |
| `--play\|--playwright` | browser testing, E2E, visual | Playwright: browser automation |
| `--chrome\|--devtools` | perf audit, debug, layout | Chrome DevTools: real-time inspection |
| `--tavily` | web search, real-time info | Tavily: web search |
| `--frontend-verify` | UI testing, frontend debug | Playwright + DevTools + Serena |
| `--all-mcp` | max complexity | Enable all MCP servers |
| `--no-mcp` | native-only, perf priority | Disable all MCP, use native + WebSearch |
  </mcp>

  <analysis>
| Flag | Trigger | Effect |
|------|---------|--------|
| `--think` | moderate complexity | ~4K tokens, enables Sequential |
| `--think-hard` | architecture, system-wide | ~10K tokens, Sequential + Context7 |
| `--ultrathink` | critical redesign, legacy, complex debug | ~32K tokens, all MCP |
  </analysis>

  <effort note="Opus 4.5 specific">
- `--effort low`: Minimal reasoning (~76% fewer tokens), fastest
- `--effort medium`: Balanced (default)
- `--effort high`: Maximum reasoning depth
  </effort>

  <extended_thinking note="API budget_tokens config">
| Parameter | Value | Notes |
|-----------|-------|-------|
| budget_tokens | 1024-32768 | Start low, increase incrementally |
| minimum | 1024 | Hard minimum enforced by API |
| recommended_start | 2048 | Good balance for most tasks |
| max_practical | 32768 | >32K requires batch processing |
| temperature | INCOMPATIBLE | Do not set when thinking enabled |

Mapping to flags:
- `--think`: budget_tokens=4096
- `--think-hard`: budget_tokens=10240
- `--ultrathink`: budget_tokens=32768
  </extended_thinking>

  <execution>
| Flag | Trigger/Range | Effect |
|------|---------------|--------|
| `--delegate [auto\|files\|folders]` | >7 dirs, >50 files, complexity >0.8 | Sub-agent parallel processing |
| `--concurrency [n]` | range: 1-15 | Max concurrent operations |
| `--loop` | polish, refine, enhance | Iterative improvement cycles |
| `--iterations [n]` | range: 1-10 | Improvement cycle count |
| `--validate` | risk >0.7, usage >75%, production | Pre-execution risk assessment |
| `--safe-mode` | usage >85%, production, critical | Max validation, conservative, auto --uc |
  </execution>

  <output>
- `--uc|--ultracompressed`: Symbol system, 30-50% reduction (trigger: context pressure, efficiency)
- `--scope [file|module|project|system]`: Analysis boundary
- `--focus [perf|security|quality|arch|a11y|testing]`: Target domain
  </output>

  <priority_rules>
- Safety First: --safe-mode > --validate > optimization
- Explicit Override: User flags > auto-detection
- Depth: --ultrathink > --think-hard > --think
- MCP: --no-mcp overrides individual flags
- Scope: system > project > module > file
  </priority_rules>
</component>
