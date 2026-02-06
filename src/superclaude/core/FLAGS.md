<component name="flags" type="core" priority="high">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>flag|--|mode|mcp|think|effort|delegate|native</triggers>

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
| `--perf\|--devtools` | perf audit, CLS, LCP, metrics | DevTools: performance analysis |
| `--tavily` | web search, real-time info | Tavily: web search |
| `--frontend-verify` | UI testing, frontend debug | Playwright + DevTools + Serena |
| `--all-mcp` | max complexity | Enable all MCP servers |
| `--no-mcp` | native-only, perf priority | Disable all MCP, use native + WebSearch |
  </mcp>

  <native>
| Tool | Trigger | Effect |
|------|---------|--------|
| WebSearch | fact-check, current info | Native web search (no flag needed) |
  </native>

  <effort note="Adaptive thinking (Opus 4.6)">
| Flag | Behavior | MCP |
|------|----------|-----|
| `--effort low` | May skip thinking for simple tasks | None |
| `--effort medium` | Selective thinking, balanced | Sequential on demand |
| `--effort high` | Default — almost always thinks | Sequential + Context7 |
| `--effort max` | Unconstrained depth (Claude 4 models) | All available |

Thinking: `{type: "adaptive"}` — Claude decides when/how much to think
Deprecated: `budget_tokens` (removed for long-context >200K in Claude 4.6 migration)
Legacy: `--think`→medium, `--think-hard`→high, `--ultrathink`→max+all-mcp
Note: temperature incompatible with thinking; interleaved thinking automatic
  </effort>

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
- Effort: --effort high > --effort medium > --effort low
- Legacy Think: --ultrathink → --effort max + --all-mcp
- MCP: --no-mcp overrides individual flags
- MCP Fallback: Notify on first use → auto fallback to native equivalent
- Scope: system > project > module > file
  </priority_rules>

  <cc_features note="Claude Code v2.0.32+">
| Name | Type | Purpose |
|------|------|---------|
| `CLAUDE_CODE_ENABLE_TASKS` | env | Enable Task tools (replaces TodoWrite) |
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | env | Load CLAUDE.md from `--add-dir` paths (v2.1.20) |
| `CLAUDE_CODE_TMPDIR` | env | Override temp directory location (v2.1.23) |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | env | Disable background tasks and Ctrl+B (v2.1.4) |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | env | Experimental multi-agent team orchestration (v2.1.32) |
| `CLAUDE_CODE_SHELL` | env | Override automatic shell detection (v2.0.65) |
| `context_window.used_percentage` | set | Status line: context usage % |
| `context_window.remaining_percentage` | set | Status line: context remaining % |
| `current_usage` | set | Status line: accurate context window calculations (v2.0.70) |
| `keybindings` | set | Custom keyboard shortcut mappings |
| `plansDirectory` | set | Custom plan file storage location |
| `respectGitignore` | set | Per-project @-mention file picker |
| `language` | set | Response language (e.g., "korean") |
| `showTurnDuration` | set | Show/hide turn duration messages (v2.1.7) |
| `spinnerVerbs` | set | Customize spinner text during tool execution (v2.1.23) |
| `companyAnnouncements` | set | Display announcements on startup (v2.0.32) |
| `--from-pr` | flag | Resume session linked to PR number/URL; auto-links via `gh pr create` |
| `/debug` | cmd | Troubleshoot current session |
| Auto memory | feature | Claude auto-records/recalls memories as it works (v2.1.32) |
| Agent memory | feature | `memory: user\|project\|local` frontmatter for persistent agent memory (v2.1.33) |
| Task metrics | feature | Task tool returns token count, tool uses, duration in results (v2.1.30) |
| `status: "deleted"` | feature | TaskUpdate supports permanent task deletion (v2.1.20) |
| Read `pages` param | feature | PDF page-range reading, e.g. `pages: "1-5"` (v2.1.30) |
| Skill 2% budget | feature | Skill character budget scales with context window (v2.1.32) |
| Permission precedence | rule | `ask` overrides `allow` at content level |
  </cc_features>

  <permission_patterns note="v2.1.0+ wildcard syntax">
| Pattern | Example | Matches |
|---------|---------|---------|
| Prefix wildcard | `Bash(* install)` | Any command ending with "install" |
| Suffix wildcard | `Bash(npm *)` | npm followed by anything |
| Middle wildcard | `Bash(git * main)` | git commands targeting main |
| Agent disable | `Task(AgentName)` | Disable specific agent in disallowedTools |
| Agent allowlist | `Task(agent-name)` in tools | Restrict which sub-agents an agent can spawn (v2.1.33) |
| MCP wildcard | `mcp__server__*` | All tools from an MCP server |
  </permission_patterns>

  <argument_syntax note="v2.1.19+ skill args">
| Syntax | Description | Example: `/skill hello world` |
|--------|-------------|-------------------------------|
| `$ARGUMENTS` | Full string | "hello world" |
| `$ARGUMENTS[0]`, `$0` | First arg | "hello" |
| `$ARGUMENTS[1]`, `$1` | Second arg | "world" |

Frontmatter usage: `Deploy $0 to $1 environment.`

Skill variables:
| Variable | Description |
|----------|-------------|
| `${CLAUDE_SESSION_ID}` | Current session ID (v2.1.9+) |
| `${CLAUDE_PLUGIN_ROOT}` | Plugin root directory (plugins only) |
  </argument_syntax>

  <persona_index note="Agent abbreviations for personas p='...'">
| Abbr | Agent | Domain |
|------|-------|--------|
| arch | system-architect | Architecture, scalability |
| fe | frontend-architect | UI, accessibility, React/Vue |
| be | backend-architect | API, database, security |
| sec | security-engineer | OWASP, vulnerabilities |
| qa | quality-engineer | Testing, coverage |
| qual | quality-engineer | Code quality (alias) |
| ops | devops-architect | CI/CD, Kubernetes |
| devops | devops-architect | DevOps (alias) |
| pm | pm-agent | Orchestration, docs |
| perf | performance-engineer | Optimization, profiling |
| refactor | refactoring-expert | Tech debt, SOLID |
| root | root-cause-analyst | Debug, hypothesis |
| anal | requirements-analyst | Analysis, strategy |
| educator | learning-guide | Code/concept education |
| mentor | socratic-mentor | Guidance, Socratic method |
| scribe | technical-writer | Documentation |
| py | python-expert | Python best practices |
| panel | business-panel-experts | Business strategy |
| research | deep-research | Web research |
| review | self-review | Post-impl validation |
| index | repo-index | Codebase indexing |
  </persona_index>

  <mcp_auto_mode note="v2.1.7+">
When MCP tool descriptions exceed 10% of context → defer to MCPSearch tool
Custom threshold: `auto:N` syntax where N is context % (e.g., `auto:15`) (v2.1.9+)
Disable: Add MCPSearch to disallowedTools
  </mcp_auto_mode>
</component>
