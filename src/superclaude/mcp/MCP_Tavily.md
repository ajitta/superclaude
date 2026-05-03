<component name="tavily" type="mcp">
  <role>
    <mission>Web search and real-time information retrieval for research and current events</mission>
  </role>

  <choose>
Use:
- Structured search: Advanced filtering over WebSearch
- Multi-source: Search, not single page extraction (use WebFetch)
- Research: Comprehensive multi-source investigations
- Current info: Post-knowledge-cutoff events

Avoid:
- Training knowledge: Simple questions from training
- Code generation: Writing code, local file ops

Channel selection (3-way):
| Channel | Trigger |
|---------|---------|
| **MCP** (default, `tavily_*`) | <5 queries · in-conversation answers · structured parallel calls · fact-check · `/sc:research --depth quick\|standard` |
| **`tavily-cli` skill** | ≥5 chained queries · `/sc:research --depth deep\|exhaustive` (≥20 sources) · file output (`--output-dir`) · advanced filters (`--include-domains`, `--time-range`) · shell pipeline composition |
| **Native WebSearch / WebFetch** | MCP+CLI both unavailable (fallback only) |
  </choose>

  ## Search Patterns
  Basic: query → ranked results | Domain: query + include_domains:[arxiv,github] | Time: query + time_range:week | Date: query + start_date/end_date | Deep: query + include_raw_content:true | Research: input → multi-source synthesis | Crawl: url + depth + instructions → pages

  ## Workflows
  - Research: Tavily:broad → Sequential:gaps → Tavily:targeted → Sequential:synthesize → Serena:store
  - Fact-Check: Tavily:verify → Tavily:contradictions → Sequential:evidence → Report
  - Deep-Research: Plan:decompose → Tavily:search → Route:simple→Tavily|complex→Playwright → Synthesize

  ## Strategies
  Multi-Hop: broad → entities → relationships → synthesize | Adaptive: Simple:direct|Complex:variations+boolean+domain|Iterative:refine→gaps
  Credibility: High=academic,gov,official | Medium=industry,expert | Low=forums,social

  <examples>
| Input | Output | Reason |
|---|---|---|
| latest TypeScript 2024 | Tavily | current tech info |
| OpenAI updates this week | Tavily | recent news |
| explain recursion | Native Claude | general concept |
  </examples>

  <bounds>
    <should>web search, multi-source synthesis, and current information retrieval.</should>
    <avoid>code generation, local file operations, and training knowledge questions.</avoid>
    <fallback>Use native WebSearch for simple queries, WebFetch for single pages.</fallback>
  </bounds>

  <handoff next="/sc:research /sc:analyze"/>
</component>
