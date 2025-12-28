<component name="tavily" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>search|research|news|current|web|fact-check|/sc:research|tavily</triggers>

  <role>
    <mission>Web search and real-time information retrieval for research and current events</mission>
  </role>

  <choose>
**Use for:**
- Structured search: Advanced filtering over WebSearch
- Multi-source: Search, not single page extraction (use WebFetch)
- Research: Comprehensive multi-source investigations
- Current info: Post-knowledge-cutoff events

**Avoid for:**
- Training knowledge: Simple questions from training
- Code generation: Writing code, local file ops
  </choose>

  <config_req>TAVILY_API_KEY from https://app.tavily.com</config_req>

  <capabilities>
- **Web**: General searches with ranking
- **News**: Time-filtered current events
- **Academic**: Scholarly articles, research papers
- **Domains**: Include/exclude specific domains
- **Extract**: Full-text from results
- **Freshness**: Prioritize recent content
- **Multi-Round**: Iterative refinement
  </capabilities>

  <synergy>
- **Sequential**: Tavily provides info → Sequential analyzes/synthesizes
- **Playwright**: Tavily discovers URLs → Playwright extracts complex content
- **Context7**: Tavily searches updates → Context7 provides stable docs
- **Serena**: Tavily searches → Serena stores sessions
  </synergy>

  <search_patterns>
- **Basic**: query → ranked results + snippets
- **Domain**: query + domains:[arxiv,github] → filtered results
- **Time**: query + recency:week|month|year → recent results
- **Deep**: query + extract:true → full content extraction
  </search_patterns>

  <quality>Refine queries | Source diversity | Credibility filter | Dedupe | Relevance scoring</quality>

  <flows>
- **Research**: Tavily:broad → Sequential:gaps → Tavily:targeted → Sequential:synthesize → Serena:store
- **Fact-Check**: Tavily:verify → Tavily:contradictions → Sequential:evidence → Report:balanced
- **Competitive**: Tavily:competitors → Tavily:trends → Sequential:compare → Context7:tech → Report:insights
- **Deep-Research**: Plan:decompose → Tavily:search → Analyze:URLs → Route:simple→Tavily|complex→Playwright → Synthesize → Iterate
  </flows>

  <strategies>
- **Multi-Hop**: Initial:broad → Follow1:entities → Follow2:relationships → Synthesize:resolve contradictions
- **Adaptive**: Simple:direct terms | Complex:variations+boolean+domain+time | Iterative:broad→refine→gaps
- **Credibility**: High:academic,gov,established,official | Medium:industry,expert,community | Low:forums,social,unverified
  </strategies>

  <perf>Batch similar | Cache results | Prioritize high-value | Limit depth by confidence</perf>

  <dr_integration>
- **Planning**: Planning-Only:direct | Intent:clarify→focus | Unified:present→adjust
- **Multi-hop**: Track genealogy | Build on previous | Detect circular | Maintain context
- **Reflection**: Assess relevance | ID gaps | Trigger searches | Calc confidence
- **Learning**: Query formulations | Search strategies | Domain prefs | Time patterns
  </dr_integration>

  <errors>
| Issue | Fix |
|-------|-----|
| API key missing | Check TAVILY_API_KEY env var |
| Rate limit | Wait + exponential backoff |
| Timeout | Increase timeout or skip |
| No results | Expand/modify search terms |

**Fallbacks**: Native WebSearch | Alternative queries | Expand scope | Use cached | Simplify terms
  </errors>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| latest TypeScript 2024 | Tavily | current tech info |
| OpenAI updates this week | Tavily | recent news |
| quantum computing 2024 | Tavily | recent research |
| explain recursion | Native Claude | general concept |
| write Python function | Native Claude | code generation |
  </examples>
</component>
