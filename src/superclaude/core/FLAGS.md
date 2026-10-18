<component name="flags" type="core">
  <role>
    <mission>Behavioral flags for Claude Code exec modes + tool selection</mission>
  </role>

  <modes>
Mode flags are typed by the user; the hook injects the matching modes/MODE_*.md when the flag or one of its keywords appears in the prompt. The text after each colon describes the mode; it is not a trigger for Claude. Without the flag or keyword, at most suggest the flag in one line. When the flag was typed but its MODE text is not in context (e.g. after compaction), Read it from `modes/` in the superclaude directory that holds this `core/`: MODE_Brainstorming, MODE_Business_Panel, MODE_DeepResearch (--research), MODE_Introspection, MODE_Token_Efficiency (--uc), MODE_Verbalized_Sampling (--vs).
--brainstorm: vague requirements, 'maybe' → collaborative discovery, probing questions
--business-panel: multi-expert biz analysis, strategy synth
--research: systematic investigation, evidence-based reasoning
--introspect: self-analysis, error recovery → surface decision logic + assumptions + alternatives (🎯⚡📊💡)
--token-efficient: same mode as --uc (see <output>)
--vs [standard|cot|multi]: "multiple perspectives", diverse responses → verbalized sampling (prob-weighted candidates; ideation/landscape queries, not factual QA). Bracket sub-params: [k:3-7], [tau:0.01-0.20], [turns:2-5], [no-synthesis]
  </modes>

  <mcp>
--c7|--context7: force Context7 lookup — resolve + query before writing or changing library-facing code, incl. refactoring/debugging that the connector's own instructions exclude. Its server instructions and tool descriptions cover when-to-use, resolve-then-query order and call limits
--play|--playwright: browser test, E2E, visual → Playwright browser automation
--perf|--devtools: perf audit, CLS, LCP, metrics → DevTools perf analysis
--tavily: web search, real-time info → Tavily Agent Skills (tavily-search/extract/crawl/map/research); Tavily MCP optional in-conv alternative
--frontend-verify: UI test, frontend debug → Playwright + DevTools
--all-mcp: max complexity → enable all MCP servers
--no-mcp: native-only, perf priority → disable all MCP, use native + WebSearch
  </mcp>

  <execution>
Execution flags take effect when the user types them; the condition text says when to suggest one.
--delegate [auto|files|folders]: sub-agent parallel delegation. Triggers + direct-vs-sub-agent decision matrix + Agent-tool-vs-Workflow boundary: core/rules/RULES_DELEGATION.md `<sub_agent_decision>` (SSOT; context_loader injects it on delegation contexts).
--concurrency [n]: 1-15 (advisory) → batch up to n independent tool calls into one message (e.g. 5 parallel Grep calls). It sets tool calls per message, not processes, and does not change the harness's own limits on parallel subagents.
--loop: iterative improvement — (1) state verifiable success criteria up-front ([R20 Success Criteria]); (2) exec → self-eval vs criteria → find gaps → re-exec; (3) brief 1-line delta per iter ("iter N: <what changed>"); (4) stop when criteria met OR no meaningful improve OR 5-iter safety cap hit. Report total iter count + final criteria-met status when done.
--iterations [n]: fixed iter count — exec improve cycle exactly N times. After each iter, briefly state what changed. Do not stop early even if output seems good.
--plan: lightweight pre-impl planning → 5-line plan (goal, approach, files, risks, verification), wait for user approval before executing
--validate: production targets, irreversible or destructive commands, migrations, shared infrastructure → pre-exec risk assessment
--safe-mode: production or critical systems → max validation, conservative changes, and --uc output
--verbose-context: inject the full .md for every triggered context instead of the one-line summaries normally used for MCP docs and the business-symbol reference. Use when a short summary leads to wrong MCP use.
Note: match flags to session type — analysis/discussion sessions rarely need --delegate/--loop (exec flags); use --tavily --c7 instead
  </execution>

  <output>
--uc|--ultracompressed: selective omission — drop content that does not change the reader's next action, never compress the prose that stays. Use when the user asks, or proactively when the harness reports context use at or above 60% (never estimate the figure); --safe-mode turns it on too. The 60% point applies at every effort level: it guards the context window, not token cost.
--scope [file|module|project|system]: analysis boundary
--focus [perf|security|quality|arch|a11y|testing]: target domain
  </output>

  <priority_rules>
  - Safety First: --safe-mode > --validate > optimization
  - Explicit Override: user flags > auto-detection
  - MCP: --no-mcp overrides individual MCP flags; when a requested MCP server is unavailable, say so once and fall back to native tools
  </priority_rules>

</component>