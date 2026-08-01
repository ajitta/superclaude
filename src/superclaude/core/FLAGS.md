<component name="flags" type="core">
  <role>
    <mission>Behavioral flags for Claude Code exec modes + tool selection</mission>
  </role>

  <modes>
--brainstorm: vague reqs, 'maybe' → collab discovery, probing Qs
--business-panel: multi-expert biz analysis, strategy synth
--research: systematic investigation, evidence-based reasoning
--introspect: self-analysis, error recovery → surface decision logic + assumptions + alternatives (🎯⚡📊💡)
--task-manage: >3 steps, >2 dirs, >3 files → hierarchical task org, persistent memory, phase checkpoints
--orchestrate: multi-tool, perf constraints, parallel → tool matrix opt
--token-efficient: ctx >75%, large ops → selective omission (see <output> --uc)
--vs [standard|cot|multi]: "multiple perspectives", diverse responses → verbalized sampling (prob-weighted candidates). Bracket sub-params: [k:3-7], [tau:0.01-0.20], [turns:2-5], [no-synthesis]
  </modes>

  <mcp>
--c7|--context7: imports, frameworks, official docs → Context7 curated docs
--seq|--sequential: complex debug, sys design → Sequential multi-step reasoning
--serena: symbol ops, project mem → Serena semantic understanding + Serena-first exploration directive
--play|--playwright: browser test, E2E, visual → Playwright browser automation
--perf|--devtools: perf audit, CLS, LCP, metrics → DevTools perf analysis
--tavily: web search, real-time info → Tavily Agent Skills (tavily-search/extract/crawl/map/research); Tavily MCP optional in-conv alternative
--frontend-verify: UI test, frontend debug → Playwright + DevTools + Serena
--all-mcp: max complexity → enable all MCP servers
--no-mcp: native-only, perf priority → disable all MCP, use native + WebSearch
  </mcp>

  <execution>
--delegate [auto|files|folders]: sub-agent parallel delegation. Triggers + direct-vs-sub-agent decision matrix + Agent-tool-vs-Workflow boundary: core/rules/RULES_DELEGATION.md `<sub_agent_decision>` (SSOT; context_loader injects it on delegation contexts).
--concurrency [n]: 1-15 (advisory; loader no clamp) → batch independent tool calls into single msg (e.g. 5 parallel Grep calls). Batches tool-calls-per-message, NOT processes — buys no process parallelism; Workflow fan-out process cap min(16, cpu-2) is harness-fixed and wins on process count.
--loop: iter improve — (1) state verifiable success criteria up-front (R20); (2) exec → self-eval vs criteria → find gaps → re-exec; (3) brief 1-line delta per iter ("iter N: <what changed>"); (4) stop when criteria met OR no meaningful improve OR 5-iter safety cap hit. Report total iter count + final criteria-met status when done.
--iterations [n]: fixed iter count — exec improve cycle exactly N times. After each iter, briefly state what changed. Do not stop early even if output seems good.
--plan: lightweight pre-impl planning → 5-line plan (goal, approach, files, risks, verification), wait user approval before exec
--validate: risk >0.7, usage >75%, prod → pre-exec risk assessment
--safe-mode: usage >85%, prod, critical → max validation, conservative, auto --uc
--verbose-context: force full .md injection for all triggered contexts, bypassing INSTRUCTION_MAP short instructions. Use when short instructions cause wrong MCP behavior.
Note: match flags to session type — analysis/discussion sessions rarely need --delegate/--loop (exec flags); use --seq --tavily --c7 instead
  </execution>

  <output>
--uc|--ultracompressed: selective omission — drop content that does not change the reader's next action, never compress the prose that stays. Manual/proactive trigger >=60% ctx; auto via --safe-mode at >=85%. The >=60% band fires under token-unbounded effort modes (e.g. ultracode) too — it guards context-window overflow (transport), not token cost.
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