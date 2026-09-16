<component name="tavily" type="mcp">
  <role>
    <mission>Web search + real-time info retrieval for research + current events</mission>
  </role>

  <choose>
  <use>structured multi-source web search with advanced filter (domain include/exclude, time/date range, raw-content depth) beyond native `WebSearch`; multi-source research with synthesized output; post-knowledge-cutoff current-info lookup.</use>
  <never>questions answerable from training; single-page extract (use native `WebFetch`); code gen or local file ops.</never>
  </choose>

  <search_patterns>
  This doc covers the optional in-conversation MCP path. `tavily-mcp` exposes `tavily_search`, `tavily_extract`, `tavily_crawl`, `tavily_map` and `tavily_research`; the Tavily Agent Skills (install per `mcp/README.md`) cover the same operations plus `tavily-dynamic-search` for filtering large results outside the context window. Pattern set below applies to `tavily_search`.

  - Basic: query → ranked results.
  - Domain: query + `include_domains:[arxiv,github]`.
  - Time: query + `time_range:week`.
  - Date: query + `start_date` / `end_date`.
  - Deep: query + `include_raw_content:true`.
  </search_patterns>

  <integration_patterns>
  - Research: Tavily:broad → identify gaps → Tavily:targeted → synthesize → Serena:store.
  - Fact-Check: Tavily:verify → Tavily:contradictions → weigh evidence → report.
  - Deep-Research: Plan:decompose → Tavily:search → Route (simple → Tavily, complex → Playwright) → synthesize.
  </integration_patterns>

  <examples>
| Input | Output | Reason |
|---|---|---|
| latest TypeScript release notes | Tavily | current tech info |
| OpenAI updates this week | Tavily | recent news |
| explain recursion | Native Claude | general concept |
  </examples>

  <bounds>
    <does>web search, multi-source synthesis, current info retrieval.</does>
    <never>code gen, local file ops, training knowledge questions.</never>
    <fallback>Prefer the Tavily Agent Skills — the six operation skills (`tavily-search`, `tavily-extract`, `tavily-crawl`, `tavily-map`, `tavily-research`, `tavily-dynamic-search`; `tavily-cli` and `tavily-best-practices` are setup and reference) — the primary integration: results are filtered before they enter context and crawl output can be saved as local markdown. MCP unavailable and skills not installed → native WebSearch for simple queries, WebFetch for single pages.</fallback>
  </bounds>

  <handoff next="/sc:research /sc:analyze"/>
</component>