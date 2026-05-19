<component name="flags" type="core">
  <role>
    <mission>Behavioral flags for Claude Code exec modes + tool selection</mission>
  </role>

  <modes>
--brainstorm: vague reqs, 'maybe' → collab discovery, probing Qs
--business-panel: multi-expert biz analysis, strategy synth
--research: systematic investigation, evidence-based reasoning
--introspect: self-analysis, error recovery → expose thinking (🤔🎯⚡📊💡)
--task-manage: >3 steps, >2 dirs, >3 files → delegation, progressive enhance
--orchestrate: multi-tool, perf constraints, parallel → tool matrix opt
--token-efficient: ctx >75%, large ops → symbol comm (see <output> --uc)
--vs [standard|cot|multi]: "multiple perspectives", diverse responses → verbalized sampling (prob-weighted candidates). Bracket sub-params: [k:3-7], [tau:0.01-0.20], [turns:2-5], [no-synthesis]
  </modes>

  <mcp>
--c7|--context7: imports, frameworks, official docs → Context7 curated docs
--seq|--sequential: complex debug, sys design → Sequential multi-step reasoning
--serena: symbol ops, project mem → Serena semantic understanding + Serena-first exploration directive
--play|--playwright: browser test, E2E, visual → Playwright browser automation
--perf|--devtools: perf audit, CLS, LCP, metrics → DevTools perf analysis
--tavily: web search, real-time info → Tavily MCP (in-conv search, parallel queries, agent workflows)
--frontend-verify: UI test, frontend debug → Playwright + DevTools + Serena
--all-mcp: max complexity → enable all MCP servers
--no-mcp: native-only, perf priority → disable all MCP, use native + WebSearch
  </mcp>

  <execution>
--delegate [auto|files|folders]: sub-agent parallel delegation. Triggers + direct-vs-sub-agent decision matrix: RULES.md `<sub_agent_decision>` (SSOT)
--concurrency [n]: 1-15 → batch independent tool calls into single msg (e.g. 5 parallel Grep calls)
--loop: iter improve — (1) state verifiable success criteria up-front (R20); (2) exec → self-eval vs criteria → find gaps → re-exec; (3) brief 1-line delta per iter ("iter N: <what changed>"); (4) stop when criteria met OR no meaningful improve OR 5-iter safety cap hit. Report total iter count + final criteria-met status when done.
--iterations [n]: fixed iter count — exec improve cycle exactly N times. After each iter, briefly state what changed. Do not stop early even if output seems good.
--plan: lightweight pre-impl planning → 5-line plan (goal, approach, files, risks, verification) before exec
--validate: risk >0.7, usage >75%, prod → pre-exec risk assessment
--safe-mode: usage >85%, prod, critical → max validation, conservative, auto --uc
--fast: same model, faster output (v2.1.36+)
--verbose-context: force full .md injection for all triggered contexts, bypassing INSTRUCTION_MAP short instructions. Use when short instructions cause wrong MCP behavior.
Note: match flags to session type — analysis/discussion sessions rarely need --delegate/--loop (exec flags); use --seq --tavily --c7 instead
  </execution>

  <output>
--uc|--ultracompressed: symbol system, 30-50% reduction. Manual/proactive trigger >=60% ctx (per MODE_Token_Efficiency.md); auto via --safe-mode at >=85%
--scope [file|module|project|system]: analysis boundary
--focus [perf|security|quality|arch|a11y|testing]: target domain
  </output>

  <priority_rules>
  - Safety First: --safe-mode > --validate > optimization
  - Explicit Override: user flags > auto-detection
  - MCP: --no-mcp overrides individual flags; notify on first use → auto fallback
  - Scope: system > project > module > file
  </priority_rules>

</component>