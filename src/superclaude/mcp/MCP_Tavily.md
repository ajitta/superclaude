<component name="tavily" type="mcp">
  <role>
    <mission>Web search and real-time information retrieval for research and current events</mission>
  </role>

  <choose>
  Use:
  - Structured search: advanced filtering over WebSearch.
  - Multi-source: search, not single-page extraction (use WebFetch).
  - Research: comprehensive multi-source investigations.
  - Current info: post-knowledge-cutoff events.

  Avoid:
  - Training knowledge: simple questions from training.
  - Code generation: writing code, local file ops.
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

  <workflows>
  - Research: Tavily:broad → Sequential:gaps → Tavily:targeted → Sequential:synthesize → Serena:store.
  - Fact-Check: Tavily:verify → Tavily:contradictions → Sequential:evidence → report.
  - Deep-Research: Plan:decompose → Tavily:search → Route (simple → Tavily, complex → Playwright) → synthesize.
  </workflows>

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
    <does>web search, multi-source synthesis, and current information retrieval.</does>
    <never>code generation, local file operations, and training knowledge questions.</never>
    <fallback>Use native WebSearch for simple queries, WebFetch for single pages.</fallback>
  </bounds>

  <handoff next="/sc:research /sc:analyze"/>
</component>
