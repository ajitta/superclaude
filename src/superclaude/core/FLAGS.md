<component name="flags" type="core" priority="high">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>flag|--|mode|mcp|think|effort|delegate|native</triggers>

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
--token-efficient: context >75%, large ops, --uc → symbol communication, 30-50% reduction
  </modes>

  <mcp>
--c7|--context7: imports, frameworks, official docs → Context7 curated docs
--seq|--sequential: complex debug, system design → Sequential multi-step reasoning
--magic: /ui, /21, design systems → Magic 21st.dev UI components
--morph|--morphllm: bulk transforms, pattern edits → Morphllm multi-file patterns
--serena: symbol ops, project memory → Serena semantic understanding
--play|--playwright: browser testing, E2E, visual → Playwright browser automation
--perf|--devtools: perf audit, CLS, LCP, metrics → DevTools performance analysis
--tavily: web search, real-time info → Tavily web search
--frontend-verify: UI testing, frontend debug → Playwright + DevTools + Serena
--all-mcp: max complexity → enable all MCP servers
--no-mcp: native-only, perf priority → disable all MCP, use native + WebSearch
Deprecated: --mindbase, --airis-agent → use airis-mcp-gateway instead
  </mcp>

  <native>
WebSearch: fact-check, current info → native web search (no flag needed)
  </native>

  <effort note="Adaptive thinking (Opus 4.6)">
--effort low: may skip thinking for simple tasks | MCP: none
--effort medium: selective thinking, balanced | MCP: Sequential on demand
--effort high: default — almost always thinks | MCP: Sequential + Context7
--effort max: unconstrained depth (Opus 4.6 exclusive) | MCP: all available

Thinking: {type: "adaptive"} — Claude decides when/how much to think
Deprecated: budget_tokens (removed for long-context >200K in Claude 4.6 migration)
Legacy: --think→medium, --think-hard→high, --ultrathink→max+all-mcp
Note: temperature incompatible with thinking; interleaved thinking automatic
  </effort>

  <execution>
--delegate [auto|files|folders]: >7 dirs, >50 files, complexity >0.8 → sub-agent parallel
--concurrency [n]: 1-15 → max concurrent operations
--loop: polish, refine, enhance → iterative improvement cycles
--iterations [n]: 1-10 → improvement cycle count
--validate: risk >0.7, usage >75%, production → pre-execution risk assessment
--safe-mode: usage >85%, production, critical → max validation, conservative, auto --uc
--fast: same Opus 4.6 model, faster output (v2.1.36+)
Agent Teams: experimental (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1) — parallel coordination
Note: Opus 4.6 overengineers by default — see RULES.md anti_over_engineering for guardrails
Note: Opus 4.6 uses 25-50% more tokens than 4.5 — monitor context usage
  </execution>

  <output>
--uc|--ultracompressed: symbol system, 30-50% reduction (trigger: context pressure)
--scope [file|module|project|system]: analysis boundary
--focus [perf|security|quality|arch|a11y|testing]: target domain
  </output>

  <priority_rules>
- Safety First: --safe-mode > --validate > optimization
- Explicit Override: user flags > auto-detection
- Effort: high > medium > low
- Legacy Think: --ultrathink → --effort max + --all-mcp
- MCP: --no-mcp overrides individual flags; notify on first use → auto fallback
- Scope: system > project > module > file
  </priority_rules>

  <persona_index note="Agent abbreviations for p='...'">
arch=system-architect(architecture) | fe=frontend-architect(UI,a11y) | be=backend-architect(API,db,security) | sec=security-engineer(OWASP) | qa=quality-engineer(testing) | qual=quality-engineer(alias) | ops=devops-architect(CI/CD,K8s) | devops=devops-architect(alias) | pm=pm-agent(orchestration) | perf=performance-engineer(profiling) | refactor=refactoring-expert(tech-debt) | root=root-cause-analyst(debug) | anal=requirements-analyst(strategy) | educator=learning-guide(education) | mentor=socratic-mentor(guidance) | scribe=technical-writer(docs) | py=python-expert(python) | panel=business-panel-experts(business) | research=deep-research-agent(web) | review=self-review(validation) | index=repo-index(indexing) | simple=simplicity-guide(OSL,YAGNI)
  </persona_index>

  <mcp_auto_mode note="v2.1.7+">
MCP tool descriptions >10% context → defer to MCPSearch; custom: auto:N (v2.1.9+); disable: add MCPSearch to disallowedTools
Tool Search Tool: defer_loading=true for 85% token reduction in large tool libraries
  </mcp_auto_mode>
</component>
