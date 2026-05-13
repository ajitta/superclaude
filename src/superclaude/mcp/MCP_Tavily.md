<component name="tavily" type="mcp">
  <role>
    <mission>Web search + real-time info retrieval for research + current events</mission>
  </role>

  <choose>
  <use>structured multi-source web search w/ advanced filter (domain include/exclude, time/date range, raw-content depth) beyond native `WebSearch`; multi-source research w/ synthesized output; post-knowledge-cutoff current-info lookup.</use>
  <never>questions answerable from training; single-page extract (use native `WebFetch`); code gen or local file ops.</never>
  </choose>

  <search_patterns>
  - Basic: query → ranked results.
  - Domain: query + `include_domains:[arxiv,github]`.
  - Time: query + `time_range:week`.
  - Date: query + `start_date` / `end_date`.
  - Deep: query + `include_raw_content:true`.
  - Research: input → multi-source synthesis.
  - Crawl: url + depth + instructions → pages.
  </search_patterns>

  <integration_patterns>
  - Research: Tavily:broad → Sequential:gaps → Tavily:targeted → Sequential:synthesize → Serena:store.
  - Fact-Check: Tavily:verify → Tavily:contradictions → Sequential:evidence → report.
  - Deep-Research: Plan:decompose → Tavily:search → Route (simple → Tavily, complex → Playwright) → synthesize.
  </integration_patterns>

  <strategies>
  - Multi-Hop: broad → entities → relationships → synthesize.
  - Adaptive: simple → direct; complex → variations + boolean + domain; iterative → refine → gaps.
  - Credibility: high = academic / gov / official; medium = industry / expert; low = forums / social.
  </strategies>

  <examples>
| Input | Output | Reason |
|---|---|---|
| latest TypeScript 2024 | Tavily | current tech info |
| OpenAI updates this week | Tavily | recent news |
| explain recursion | Native Claude | general concept |
  </examples>

  <bounds>
    <does>web search, multi-source synthesis, current info retrieval.</does>
    <never>code gen, local file ops, training knowledge questions.</never>
    <fallback>MCP server down → invoke /tavily-cli skill for full CLI access — includes tvly map (URL discovery) + tvly research (multi-source deep research) not in MCP. Native WebSearch for simple queries, WebFetch for single pages.</fallback>
  </bounds>

  <handoff next="/sc:research /sc:analyze"/>
</component>