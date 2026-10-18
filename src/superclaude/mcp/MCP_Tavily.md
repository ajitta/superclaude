<component name="tavily" type="mcp">
  <role>
    <mission>Web search and real-time information retrieval for research and current events</mission>
  </role>

  <choose>
  <use>the Tavily Agent Skills first when they are installed (the six operation skills `tavily-search`, `tavily-extract`, `tavily-crawl`, `tavily-map`, `tavily-research` and `tavily-dynamic-search`; `tavily-cli` and `tavily-best-practices` cover setup and reference): they filter results before they enter context and can save crawl output as local markdown. This MCP covers the same work when the skills are absent: structured multi-source web search with advanced filters (domain include/exclude, time and date ranges, raw-content depth) beyond native `WebSearch`, multi-source research with synthesized output, and lookups of current information past the knowledge cutoff.</use>
  <never>single-page extraction through the MCP's `tavily_extract` (use native `WebFetch`, or the `tavily-extract` skill where installed), and code generation or local file operations.</never>
  </choose>

  <integration_patterns>
  - Research: Tavily:broad → identify gaps → Tavily:targeted → synthesize → suggest /sc:save.
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
    <does>web search, multi-source synthesis, and current information retrieval.</does>
    <never>code generation and local file operations.</never>
    <fallback>When neither the skills nor the MCP is available, use native WebSearch for simple queries and WebFetch for single pages.</fallback>
  </bounds>

  <handoff next="/sc:research /sc:analyze"/>
</component>