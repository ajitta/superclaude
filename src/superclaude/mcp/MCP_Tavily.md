<component name="tavily" type="mcp">
  <role>
    <mission>Web search + real-time info retrieval for research + current events</mission>
  </role>

  <choose>
  <use>structured multi-source web search w/ advanced filter (domain include/exclude, time/date range, raw-content depth) beyond native `WebSearch`; multi-source research w/ synthesized output; post-knowledge-cutoff current-info lookup.</use>
  <never>questions answerable from training; single-page extract (use native `WebFetch`); code gen or local file ops.</never>
  </choose>

  <search_patterns>
  This doc covers the optional in-conversation MCP path, which exposes only `tavily-search` + `tavily-extract`; crawl, map, and multi-source research live in the Tavily Agent Skills (install per `mcp/README.md`). Pattern set below applies to `tavily-search`.

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
| latest TypeScript 2024 | Tavily | current tech info |
| OpenAI updates this week | Tavily | recent news |
| explain recursion | Native Claude | general concept |
  </examples>

  <bounds>
    <does>web search, multi-source synthesis, current info retrieval.</does>
    <never>code gen, local file ops, training knowledge questions.</never>
    <fallback>Prefer the Tavily Agent Skills (`tavily-search`, `tavily-extract`, `tavily-crawl`, `tavily-map`, `tavily-research`) — the primary integration, covering map + multi-source research not in MCP. MCP unavailable and skills not installed → native WebSearch for simple queries, WebFetch for single pages.</fallback>
  </bounds>

  <handoff next="/sc:research /sc:analyze"/>
</component>