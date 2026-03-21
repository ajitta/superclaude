<component name="flags" type="core" priority="high">
  <role>
    <mission>Behavioral flags for Claude Code execution modes and tool selection</mission>
  </role>

  <modes note="Behavioral hints — model reads these directly, no extended docs injected">
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
--serena: symbol ops, project memory → Serena semantic understanding + Serena-first exploration directive
--play|--playwright: browser testing, E2E, visual → Playwright browser automation
--perf|--devtools: perf audit, CLS, LCP, metrics → DevTools performance analysis
--tavily: web search, real-time info → Tavily MCP (in-conversation search, parallel queries, agent workflows)
--tvly: web search, file output → Tavily CLI via Bash (domain/time filtering, pipeline composition, --json structured output)
--frontend-verify: UI testing, frontend debug → Playwright + DevTools + Serena
--all-mcp: max complexity → enable all MCP servers
--no-mcp: native-only, perf priority → disable all MCP, use native + WebSearch
  </mcp>

  <native>
WebSearch: fact-check, current info → native web search (no flag needed)
  </native>

  <execution>
--delegate [auto|files|folders]: >7 dirs, >50 files, complexity >0.8 → sub-agent parallel
  Direct work for: single-file edits, sequential ops, <3 steps, simple searches (grep/glob)
  Sub-agents for: parallel-capable, isolated context, independent work streams, >5 files
  Default: sub-agents inherit parent model unless explicit model field in agent frontmatter
  Heuristic: opus for all specialist agents | sonnet for repo-index (scanning) | haiku for future lightweight tasks
  Override: user can set explicit model in Task() calls
--concurrency [n]: 1-15 → batch independent tool calls into single message (e.g. 5 parallel Grep calls)
--loop: iterative improvement — execute task → self-evaluate output → identify gaps → re-execute → repeat until no meaningful improvement found. Report iteration count when done.
--iterations [n]: fixed iteration count — execute the improvement cycle exactly N times. After each iteration, briefly state what changed. Do not stop early even if output seems good.
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

  <aliases note="v3.2: auto-corrected by context_loader.py">
--ultrathink → --seq | --think → --seq | --think-hard → --seq
--parallel|--parellel → --delegate | --agent → --delegate
--conccurrency → --concurrency | --iteration → --iterations | --loo → --loop
--sea → --serena | --confidenc-check|--confidence-check → --validate
Typos: fuzzy-matched (Levenshtein ≤ 2) → suggestion in HTML comment
  </aliases>

<priority_rules>

- Safety First: --safe-mode > --validate > optimization
- Explicit Override: user flags > auto-detection
- MCP: --no-mcp overrides individual flags; notify on first use → auto fallback
- Scope: system > project > module > file
  </priority_rules>

  <persona_index note="Agent abbreviations for p='...'">
  arch=system-architect(architecture) | fe=frontend-architect(UI,a11y) | be=backend-architect(API,db,security) | sec=security-engineer(OWASP) | qa=quality-engineer(testing) | qual=quality-engineer(alias) | ops=devops-architect(CI/CD,K8s) | devops=devops-architect(alias) | pm=project-manager(orchestration) | perf=performance-engineer(profiling) | refactor=refactoring-expert(tech-debt) | root=root-cause-analyst(debug) | anal=requirements-analyst(strategy) | educator=learning-guide(education) | mentor=socratic-mentor(guidance) | scribe=technical-writer(docs) | py=python-expert(python) | panel=business-panel-experts(business) | research=deep-researcher(web) | review=self-review(validation) | index=repo-index(indexing) | simple=simplicity-guide(OSL,YAGNI) | git=git-workflow(git,commits,PR)
  </persona_index>

  <mcp_auto_mode note="v2.1.7+">
  MCP tool descriptions >10% context → defer to MCPSearch; custom: auto:N (v2.1.9+); disable: add MCPSearch to disallowedTools
  Tool Search Tool: defer_loading=true for 85% token reduction in large tool libraries
  </mcp_auto_mode>
  </component>
