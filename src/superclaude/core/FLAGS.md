<component name="flags" type="core" priority="high">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>flag|--|mode|mcp|think|effort|delegate|--chrome|native</triggers>

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
| `--perf\|--devtools` | perf audit, CLS, LCP, metrics | Chrome DevTools: performance analysis |
| `--tavily` | web search, real-time info | Tavily: web search |
| `--frontend-verify` | UI testing, frontend debug | Playwright + DevTools + Serena |
| `--all-mcp` | max complexity | Enable all MCP servers |
| `--no-mcp` | native-only, perf priority | Disable all MCP, use native + WebSearch + Chrome |
  </mcp>

  <native>
| Flag | Trigger | Effect |
|------|---------|--------|
| `--chrome` | live browser, auth sessions, interactive | Native Chrome automation |
| WebSearch | fact-check, current info | Native web search (no flag needed) |
  </native>

  <effort note="Reasoning depth control (Opus 4.5)">
| Flag | Effect | MCP | budget_tokens |
|------|--------|-----|---------------|
| `--effort low` | Minimal (~76% fewer tokens) | None | 1024 |
| `--effort medium` | Balanced (default) | Sequential on demand | 4096 |
| `--effort high` | Maximum depth, comprehensive | Sequential + Context7 | 10240-32768 |

Legacy: `--think`→medium, `--think-hard`→high, `--ultrathink`→high+all-mcp
Note: temperature incompatible with thinking; budget auto-scaled when alwaysThinkingEnabled=true
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
- Legacy Think: --ultrathink → --effort high + --all-mcp
- MCP: --no-mcp overrides individual flags
- Scope: system > project > module > file
  </priority_rules>

  <cc_features note="Claude Code 2.1.x">
| Name | Type | Purpose | Ver |
|------|------|---------|-----|
| `IS_DEMO` | env | Hide email/org from UI | 2.1.0 |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | env | Override file read token limit | 2.1.0 |
| `FORCE_AUTOUPDATE_PLUGINS` | env | Force plugin autoupdate | 2.1.2 |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | env | Disable Ctrl+B backgrounding | 2.1.4 |
| `CLAUDE_CODE_TMPDIR` | env | Override temp directory | 2.1.5 |
| `CLAUDE_CODE_ENABLE_TASKS` | env | Enable Task tools (replaces TodoWrite) | 2.1.19 |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | env | Disable beta headers (Bedrock/Vertex) | 2.1.25 |
| `CLAUDE_ENV_FILE` | env | Custom env file path (SessionStart hooks) | 2.1.25 |
| `CLAUDE_CODE_REMOTE` | env | Remote session indicator | 2.1.26 |
| `language` | set | Response language (e.g., "japanese") | 2.1.0 |
| `respectGitignore` | set | Per-project @-mention file picker | 2.1.0 |
| `showTurnDuration` | set | Hide "Cooked for Xm Xs" messages | 2.1.7 |
| `plansDirectory` | set | Custom plan file storage location | 2.1.9 |
| `keybindings` | set | Custom keyboard shortcut mappings | 2.1.18 |
| `reducedMotion` | set | Reduced motion mode | 2.1.30 |
| `context_window.used_percentage` | set | Status line: context usage % | 2.1.6 |
| `context_window.remaining_percentage` | set | Status line: context remaining % | 2.1.6 |
| `--from-pr` | flag | Resume session linked to PR number/URL | 2.1.27 |
| `--client-id/--client-secret` | flag | Pre-configured OAuth for MCP servers | 2.1.30 |
| `/debug` | cmd | Troubleshoot current session | 2.1.30 |
| `pages` (Read tool) | param | PDF page range (e.g., "1-5") | 2.1.30 |
| Task metrics | status | Token count, tool uses, duration in Task results | 2.1.30 |
| Permission precedence | rule | `ask` overrides `allow` at content level | 2.1.27 |
  </cc_features>

  <permission_patterns note="v2.1.0+ wildcard syntax">
| Pattern | Example | Matches |
|---------|---------|---------|
| Prefix wildcard | `Bash(* install)` | Any command ending with "install" |
| Suffix wildcard | `Bash(npm *)` | npm followed by anything |
| Middle wildcard | `Bash(git * main)` | git commands targeting main |
| Agent disable | `Task(AgentName)` | Disable specific agent in disallowedTools |
| MCP wildcard | `mcp__server__*` | All tools from an MCP server |
  </permission_patterns>

  <argument_syntax note="v2.1.19+ skill args">
| Syntax | Description | Example: `/skill hello world` |
|--------|-------------|-------------------------------|
| `$ARGUMENTS` | Full string | "hello world" |
| `$ARGUMENTS[0]`, `$0` | First arg | "hello" |
| `$ARGUMENTS[1]`, `$1` | Second arg | "world" |

Frontmatter usage: `Deploy $0 to $1 environment.`
  </argument_syntax>
</component>
