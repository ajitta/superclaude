<component name="tavily" type="mcp">
  <triggers>search|research|news|current|web|fact-check|/sc:research|tavily</triggers>

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

  <search_patterns>
Basic: query → ranked results | Domain: query + domains:[arxiv,github] | Time: query + recency:week|month|year | Deep: query + extract:true | Research: input → multi-source synthesis | Crawl: url + depth + instructions → pages
  </search_patterns>

  <quality>Refine queries | Source diversity | Credibility filter | Dedupe | Relevance scoring</quality>

  <flows>
- Research: Tavily:broad → Sequential:gaps → Tavily:targeted → Sequential:synthesize → Serena:store
- Fact-Check: Tavily:verify → Tavily:contradictions → Sequential:evidence → Report
- Deep-Research: Plan:decompose → Tavily:search → Route:simple→Tavily|complex→Playwright → Synthesize
  </flows>

  <strategies>
Multi-Hop: broad → entities → relationships → synthesize | Adaptive: Simple:direct|Complex:variations+boolean+domain|Iterative:refine→gaps
Credibility: High=academic,gov,official | Medium=industry,expert | Low=forums,social
  </strategies>

  <perf>Batch similar | Cache results | Prioritize high-value | Limit depth by confidence</perf>

  <dr_integration>
Planning: Planning-Only:direct | Intent:clarify→focus | Unified:present→adjust
Multi-hop: Track genealogy | Detect circular | Maintain context
Reflection: Assess relevance | ID gaps | Calc confidence
  </dr_integration>

  <errors>
| Issue | Fix |
|-------|-----|
| API key missing | Check TAVILY_API_KEY env var |
| Rate limit | Wait + exponential backoff |
| Timeout | Increase timeout or skip |
| No results | Expand/modify search terms |

Fallback: Native WebSearch → Alt queries → Expand scope → Use cached
  </errors>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| latest TypeScript 2024 | Tavily | current tech info |
| OpenAI updates this week | Tavily | recent news |
| explain recursion | Native Claude | general concept |
  </examples>

</component>
