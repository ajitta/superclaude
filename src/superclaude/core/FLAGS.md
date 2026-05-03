<component name="flags" type="core">
  <role>
    <mission>Behavioral flags for Claude Code execution modes and tool selection</mission>
  </role>

  <modes>
--brainstorm: vague requests, 'maybe' → collaborative discovery, probing questions
--business-panel: multi-expert business analysis, strategy synthesis
--research: systematic investigation, evidence-based reasoning
--introspect: self-analysis, error recovery → expose thinking (🤔🎯⚡📊💡)
--task-manage: >3 steps, >2 dirs, >3 files → delegation, progressive enhancement
--orchestrate: multi-tool, perf constraints, parallel → tool matrix optimization
--token-efficient: context >75%, large ops → symbol communication (see <output> --uc)
--vs [standard|cot|multi]: "multiple perspectives", diverse responses → verbalized sampling (probability-weighted candidates). Bracket sub-params: [k:3-7], [tau:0.01-0.20], [turns:2-5], [no-synthesis]
  </modes>

  <mcp>
--c7|--context7: imports, frameworks, official docs → Context7 curated docs
--seq|--sequential: complex debug, system design → Sequential multi-step reasoning
--magic: /ui, /21, design systems → Magic 21st.dev UI components
--serena: symbol ops, project memory → Serena semantic understanding + Serena-first exploration directive
--play|--playwright: browser testing, E2E, visual → Playwright browser automation
--perf|--devtools: perf audit, CLS, LCP, metrics → DevTools performance analysis
--tavily: web search, real-time info → Tavily MCP (in-conversation search, parallel queries, agent workflows)
--sg|--ast-grep: structural patterns, AST search, anti-patterns → ast-grep tree-sitter code analysis
--frontend-verify: UI testing, frontend debug → Playwright + DevTools + Serena
--all-mcp: max complexity → enable all MCP servers
--no-mcp: native-only, perf priority → disable all MCP, use native + WebSearch
  </mcp>

  <execution>
--delegate [auto|files|folders]: sub-agent parallel delegation. Auto-trigger: >7 dirs, >50 files, complexity >0.8. Decision matrix (when to sub-agent vs direct): RULES.md `<sub_agent_decision>` (SSOT)
--concurrency [n]: 1-15 → batch independent tool calls into single message (e.g. 5 parallel Grep calls)
--loop: iterative improvement — execute task → self-evaluate output → identify gaps → re-execute → repeat until no meaningful improvement found. Report iteration count when done.
--iterations [n]: fixed iteration count — execute the improvement cycle exactly N times. After each iteration, briefly state what changed. Do not stop early even if output seems good.
--plan: lightweight pre-implementation planning → 5-line plan (goal, approach, files, risks, verification) before execution
--validate: risk >0.7, usage >75%, production → pre-execution risk assessment
--safe-mode: usage >85%, production, critical → max validation, conservative, auto --uc
--fast: same model, faster output (v2.1.36+)
--p [abbr,...]: agent preference — bias sub-agent delegation toward specific agents. Multi-select: --p=sec,perf,qa
  Abbrevs: arch(system-architect) fe(frontend) be(backend) sec(security) qa(quality) ops(devops) pm(project-manager) perf(performance) refactor(refactoring) root(root-cause) req(requirements) py(python) panel(business) research(deep-researcher) review(self-review) simple(simplicity) git(git-workflow) scribe(technical-writer) educator(learning) mentor(socratic) index(repo-index) init(project-initializer) insight(insight-analyst)
--verbose-context: force full .md injection for all triggered contexts, bypassing INSTRUCTION_MAP short instructions. Use when short instructions cause incorrect MCP behavior.
Note: Agent Teams experimental (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1) — parallel coordination
Note: see RULES.md anti_over_engineering for scope discipline guardrails
Note: token consumption varies by model — monitor context usage, use --uc at 60%+
Note: match flags to session type — analysis/discussion sessions rarely need --delegate/--loop (execution flags); use --seq --tavily --c7 instead
  </execution>

  <output>
--uc|--ultracompressed: symbol system, 30-50% reduction (trigger: context pressure)
--scope [file|module|project|system]: analysis boundary
--focus [perf|security|quality|arch|a11y|testing]: target domain
  </output>

  <aliases note="Auto-corrected by context_loader.py — listed for user reference">
Remaps: --ultrathink/--think* → --seq | --parallel/--agent → --delegate | --sampling/--verbalized → --vs | --sea → --serena | --confidence-check → --validate
Typo fuzzy-match: Levenshtein ≤ 2 → suggestion in HTML comment
  </aliases>

  <priority_rules>
  - Safety First: --safe-mode > --validate > optimization
  - Explicit Override: user flags > auto-detection
  - MCP: --no-mcp overrides individual flags; notify on first use → auto fallback
  - Scope: system > project > module > file
  </priority_rules>

  <mcp_auto_mode>
  When MCP tool descriptions exceed 10% of context, CC defers loading via MCPSearch. Override threshold with `auto:N` | disable by adding `MCPSearch` to `disallowedTools` in agent frontmatter.
  </mcp_auto_mode>
</component>
