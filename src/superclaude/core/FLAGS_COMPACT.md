<component name="flags" type="core" priority="high">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <modes>
| Flag | Effect |
|------|--------|
| `--brainstorm` | Collaborative discovery, probing questions |
| `--introspect` | Expose thinking (🤔🎯⚡📊💡) |
| `--task-manage` | Delegation, progressive enhancement |
| `--orchestrate` | Tool matrix optimization, parallel thinking |
| `--token-efficient` | Symbol communication, 30-50% reduction |
| `--research` | Systematic investigation, evidence-based reasoning |
| `--business-panel` | Multi-expert business analysis |
  </modes>

  <mcp note="Auto-loaded by hooks on flag trigger">
| Flag | Effect |
|------|--------|
| `--c7\|--context7` | Context7: library docs, patterns |
| `--seq\|--sequential` | Sequential: multi-step reasoning |
| `--magic` | Magic: 21st.dev UI components |
| `--morph\|--morphllm` | Morphllm: bulk pattern edits |
| `--serena` | Serena: semantic code, memory |
| `--play\|--playwright` | Playwright: browser E2E |
| `--perf\|--devtools` | DevTools: performance metrics |
| `--tavily` | Tavily: web search, research |
| `--frontend-verify` | Playwright + DevTools + Serena |
| `--all-mcp` | Enable all MCP servers |
| `--no-mcp` | Native only, no MCP |
  </mcp>

  <effort note="Reasoning depth (Opus 4.5)">
| Flag | MCP | budget_tokens |
|------|-----|---------------|
| `--effort low` | None | 1024 |
| `--effort medium` | Sequential on demand | 4096 |
| `--effort high` | Sequential + Context7 | 10240-32768 |
Legacy: --think→medium, --think-hard→high, --ultrathink→high+all-mcp
  </effort>

  <execution>
| Flag | Effect |
|------|--------|
| `--delegate [auto\|files\|folders]` | Sub-agent parallel processing |
| `--concurrency [n]` (1-15) | Max concurrent operations |
| `--loop` | Iterative improvement cycles |
| `--iterations [n]` (1-10) | Improvement cycle count |
| `--validate` | Pre-execution risk assessment |
| `--safe-mode` | Max validation, auto --uc |
  </execution>

  <output>
- `--uc|--ultracompressed`: Symbol system, 30-50% reduction
- `--scope [file|module|project|system]`: Analysis boundary
- `--focus [perf|security|quality|arch|a11y|testing]`: Target domain
  </output>

  <priority_rules>
Safety: --safe-mode > --validate > optimization
Override: User flags > auto-detection
Effort: high > medium > low
MCP: --no-mcp overrides individual flags
  </priority_rules>

  <permission_patterns note="v2.1.0+">
| Pattern | Example |
|---------|---------|
| Prefix wildcard | `Bash(* install)` |
| Suffix wildcard | `Bash(npm *)` |
| Agent disable | `Task(AgentName)` |
| MCP wildcard | `mcp__server__*` |
  </permission_patterns>

  <argument_syntax note="v2.1.19+">
`$ARGUMENTS` (full) | `$0` (first arg) | `$1` (second arg)
  </argument_syntax>
</component>
