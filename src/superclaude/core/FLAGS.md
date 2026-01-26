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

  <native note="Built-in Claude Code features">
| Flag | Trigger | Effect |
|------|---------|--------|
| `--chrome` | live browser, auth sessions, interactive | Native Chrome automation |
| WebSearch | fact-check, current info | Native web search (no flag needed) |
  </native>

  <effort note="Opus 4.5 - Primary reasoning depth control">
| Flag | Effect | MCP Integration |
|------|--------|-----------------|
| `--effort low` | Minimal reasoning (~76% fewer tokens), fastest | None |
| `--effort medium` | Balanced analysis (default) | Sequential on demand |
| `--effort high` | Maximum reasoning depth, comprehensive analysis | Sequential + Context7 |
  </effort>

  <think_flags note="Legacy compatibility - maps to --effort when alwaysThinkingEnabled=true">
| Legacy Flag | Maps To | Behavior |
|-------------|---------|----------|
| `--think` | `--effort medium` | Standard analysis depth |
| `--think-hard` | `--effort high` | Deep analysis with MCP |
| `--ultrathink` | `--effort high` + all MCP | Maximum complexity handling |

When `alwaysThinkingEnabled: true` (default for Opus 4.5):
- Extended thinking is always active
- Think flags serve as **complexity hints** rather than thinking toggles
- Use `--effort` directly for explicit control
  </think_flags>

  <extended_thinking note="API budget_tokens - auto-managed when alwaysThinkingEnabled=true">
| Parameter | Value | Notes |
|-----------|-------|-------|
| budget_tokens | 1024-32768 | Auto-scaled based on complexity |
| minimum | 1024 | Hard minimum enforced by API |
| default | 4096 | Standard tasks |
| max_practical | 32768 | Complex multi-domain analysis |
| temperature | INCOMPATIBLE | Do not set when thinking enabled |

Legacy mapping (deprecated when alwaysThinkingEnabled=true):
- `--think`: budget_tokens=4096 → now use `--effort medium`
- `--think-hard`: budget_tokens=10240 → now use `--effort high`
- `--ultrathink`: budget_tokens=32768 → now use `--effort high` + `--all-mcp`
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
- Effort: --effort high > --effort medium > --effort low
- Legacy Think: --ultrathink → --effort high + --all-mcp
- MCP: --no-mcp overrides individual flags
- Scope: system > project > module > file
  </priority_rules>

  <environment_variables note="Claude Code 2.1.x additions">
| Variable | Purpose | Version |
|----------|---------|---------|
| `IS_DEMO` | Hide email/org from UI (streaming) | 2.1.0 |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | Override file read token limit | 2.1.0 |
| `FORCE_AUTOUPDATE_PLUGINS` | Force plugin autoupdate | 2.1.2 |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | Disable Ctrl+B backgrounding | 2.1.4 |
| `CLAUDE_CODE_TMPDIR` | Override temp directory | 2.1.5 |
| `CLAUDE_CODE_ENABLE_TASKS` | Enable TaskCreate/TaskUpdate/TaskList/TaskGet (replaces TodoWrite) | 2.1.19 |
  </environment_variables>

  <settings note="Claude Code 2.1.x additions">
| Setting | Purpose | Version |
|---------|---------|---------|
| `language` | Response language (e.g., "japanese") | 2.1.0 |
| `respectGitignore` | Per-project @-mention file picker control | 2.1.0 |
| `showTurnDuration` | Hide "Cooked for Xm Xs" messages | 2.1.7 |
| `plansDirectory` | Custom plan file storage location | 2.1.9 |
| `keybindings` | Custom keyboard shortcut mappings | 2.1.18 |
| `context_window.used_percentage` | Status line: context usage % | 2.1.6 |
| `context_window.remaining_percentage` | Status line: context remaining % | 2.1.6 |
  </settings>

  <permission_patterns note="v2.1.0+ wildcard syntax">
| Pattern | Example | Matches |
|---------|---------|---------|
| Prefix wildcard | `Bash(* install)` | Any command ending with "install" |
| Suffix wildcard | `Bash(npm *)` | npm followed by anything |
| Middle wildcard | `Bash(git * main)` | git commands targeting main |
| Agent disable | `Task(AgentName)` | Disable specific agent in disallowedTools |
| MCP wildcard | `mcp__server__*` | All tools from an MCP server |
  </permission_patterns>

  <argument_syntax note="v2.1.19+ skill argument passing">
| Syntax | Description | Example |
|--------|-------------|---------|
| `$ARGUMENTS` | Full argument string | `/skill hello world` → `"hello world"` |
| `$ARGUMENTS[0]` | First argument (bracket syntax) | `/skill hello world` → `"hello"` |
| `$ARGUMENTS[1]` | Second argument | `/skill hello world` → `"world"` |
| `$0` | Shorthand for `$ARGUMENTS[0]` | Same as bracket syntax |
| `$1` | Shorthand for `$ARGUMENTS[1]` | Same as bracket syntax |

Usage in skill frontmatter:
```yaml
---
name: deploy
description: Deploy to environment
---
Deploy $ARGUMENTS[0] to $ARGUMENTS[1] environment.
```
  </argument_syntax>
</component>
