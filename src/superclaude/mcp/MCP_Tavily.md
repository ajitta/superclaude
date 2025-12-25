<component name="tavily" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>search|research|news|current|web|fact-check|/sc:research|tavily</triggers>

  <role>
    <mission>Web search and real-time information retrieval for research and current events</mission>
  </role>

  <choose>
    <use context="structured search">Advanced filtering over WebSearch</use>
    <use context="multi-source">Search, not single page extraction (use WebFetch)</use>
    <use context="research">Comprehensive multi-source investigations</use>
    <use context="current info">Post-knowledge-cutoff events</use>
    <avoid context="training knowledge">Simple questions from training</avoid>
    <avoid context="code generation">Writing code, local file ops</avoid>
  </choose>

  <config_req>TAVILY_API_KEY from https://app.tavily.com</config_req>

  <capabilities>
    <c n="Web">General searches with ranking</c>
    <c n="News">Time-filtered current events</c>
    <c n="Academic">Scholarly articles, research papers</c>
    <c n="Domains">Include/exclude specific domains</c>
    <c n="Extract">Full-text from results</c>
    <c n="Freshness">Prioritize recent content</c>
    <c n="Multi-Round">Iterative refinement</c>
  </capabilities>

  <synergy>
    <with n="Sequential">Tavily provides info → Sequential analyzes/synthesizes</with>
    <with n="Playwright">Tavily discovers URLs → Playwright extracts complex content</with>
    <with n="Context7">Tavily searches updates → Context7 provides stable docs</with>
    <with n="Serena">Tavily searches → Serena stores sessions</with>
  </synergy>

  <search_patterns>
    <p n="Basic">query → ranked results + snippets</p>
    <p n="Domain">query + domains:[arxiv,github] → filtered results</p>
    <p n="Time">query + recency:week|month|year → recent results</p>
    <p n="Deep">query + extract:true → full content extraction</p>
  </search_patterns>

  <quality>Refine queries | Source diversity | Credibility filter | Dedupe | Relevance scoring</quality>

  <flows>
    <flow n="Research">Tavily:broad → Sequential:gaps → Tavily:targeted → Sequential:synthesize → Serena:store</flow>
    <flow n="Fact-Check">Tavily:verify → Tavily:contradictions → Sequential:evidence → Report:balanced</flow>
    <flow n="Competitive">Tavily:competitors → Tavily:trends → Sequential:compare → Context7:tech → Report:insights</flow>
    <flow n="Deep-Research">Plan:decompose → Tavily:search → Analyze:URLs → Route:simple→Tavily|complex→Playwright → Synthesize → Iterate</flow>
  </flows>

  <strategies>
    <s n="Multi-Hop">Initial:broad → Follow1:entities → Follow2:relationships → Synthesize:resolve contradictions</s>
    <s n="Adaptive">Simple:direct terms | Complex:variations+boolean+domain+time | Iterative:broad→refine→gaps</s>
    <s n="Credibility">High:academic,gov,established,official | Medium:industry,expert,community | Low:forums,social,unverified</s>
  </strategies>

  <perf>Batch similar | Cache results | Prioritize high-value | Limit depth by confidence</perf>

  <dr_integration>
    <planning>Planning-Only:direct | Intent:clarify→focus | Unified:present→adjust</planning>
    <multi_hop>Track genealogy | Build on previous | Detect circular | Maintain context</multi_hop>
    <reflection>Assess relevance | ID gaps | Trigger searches | Calc confidence</reflection>
    <learning>Query formulations | Search strategies | Domain prefs | Time patterns</learning>
  </dr_integration>

  <errors>
    <e issue="API key missing" fix="Check TAVILY_API_KEY env var"/>
    <e issue="Rate limit" fix="Wait + exponential backoff"/>
    <e issue="Timeout" fix="Increase timeout or skip"/>
    <e issue="No results" fix="Expand/modify search terms"/>
    <fallbacks>Native WebSearch | Alternative queries | Expand scope | Use cached | Simplify terms</fallbacks>
  </errors>

  <examples>
    <ex i="latest TypeScript 2024" o="Tavily" r="current tech info"/>
    <ex i="OpenAI updates this week" o="Tavily" r="recent news"/>
    <ex i="quantum computing 2024" o="Tavily" r="recent research"/>
    <ex i="explain recursion" o="Native Claude" r="general concept"/>
    <ex i="write Python function" o="Native Claude" r="code generation"/>
  </examples>
</component>
