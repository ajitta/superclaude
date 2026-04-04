<component name="tavily" type="mcp">
  <role>
    <mission>Web search and real-time information retrieval for research and current events</mission>
    <config_req>TAVILY_API_KEY from https://app.tavily.com</config_req>
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
  </choose>

  <capabilities>
Web: General searches | News: Time-filtered | Academic: Scholarly articles | Domains: Include/exclude | Extract: Full-text | Freshness: Recent priority | Multi-Round: Iterative | Research: Multi-source synthesis | Crawl: Site-wide content extraction | Map: URL structure discovery
  </capabilities>


  <tools>
| Tool | Purpose | When |
|------|---------|------|
| `tavily_search` | Web search with filtering | General queries, news, domain-specific |
| `tavily_extract` | Extract content from URLs | Full-text from known URLs |
| `tavily_research` | Multi-source synthesis | Comprehensive research tasks |
| `tavily_crawl` | Site-wide extraction | Crawl from root URL with depth/breadth |
| `tavily_map` | URL structure discovery | Map site structure before targeted extraction |
  </tools>

  ## Search Parameters (tavily_search)
  - `search_depth`: "basic" | "advanced" | "fast" | "ultra-fast"
  - `time_range`: "day" | "week" | "month" | "year"
  - `start_date` / `end_date`: YYYY-MM-DD format for precise date ranges
  - `include_domains` / `exclude_domains`: domain filtering arrays
  - `country`: boost results from specific country (full name, e.g., "Japan")
  - `max_results`: 5-20 (default: 5)
  - `include_raw_content`: get cleaned HTML of each result
  - `DEFAULT_PARAMETERS` env var: set default search behavior

  ## Search Patterns
  Basic: query → ranked results | Domain: query + include_domains:[arxiv,github] | Time: query + time_range:week | Date: query + start_date/end_date | Deep: query + include_raw_content:true | Research: input → multi-source synthesis | Crawl: url + depth + instructions → pages

  ## Workflows
  - Research: Tavily:broad → Sequential:gaps → Tavily:targeted → Sequential:synthesize → Serena:store
  - Fact-Check: Tavily:verify → Tavily:contradictions → Sequential:evidence → Report
  - Deep-Research: Plan:decompose → Tavily:search → Route:simple→Tavily|complex→Playwright → Synthesize

  ## Strategies
  Multi-Hop: broad → entities → relationships → synthesize | Adaptive: Simple:direct|Complex:variations+boolean+domain|Iterative:refine→gaps
  Credibility: High=academic,gov,official | Medium=industry,expert | Low=forums,social

  ## Error Handling
| Issue | Fix |
|-------|-----|
| API key missing | Check TAVILY_API_KEY env var |
| Rate limit | Wait + exponential backoff |
| Timeout | Increase timeout or skip |
| No results | Expand/modify search terms |
  Fallback: Native WebSearch → Alt queries → Expand scope → Use cached

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| latest TypeScript 2024 | Tavily | current tech info |
| OpenAI updates this week | Tavily | recent news |
| explain recursion | Native Claude | general concept |
  </examples>

  <bounds will="web search|multi-source synthesis|current information retrieval" wont="code generation|local file operations|training knowledge questions" fallback="Use native WebSearch for simple queries, WebFetch for single pages"/>

  <handoff next="/sc:research /sc:analyze"/>
</component>
