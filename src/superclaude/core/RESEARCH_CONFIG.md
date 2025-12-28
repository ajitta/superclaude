<component name="research-config" type="core" priority="medium">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>research|deep-research|planning|hop|confidence|tavily</triggers>

  <role>
    <mission>Deep research configuration and strategy settings</mission>
  </role>

  <defaults>
- **planning**: unified
- **max_hops**: 5
- **confidence**: 0.7
- **memory**: true
- **parallel**: true (DEFAULT_MODE)
  </defaults>

  <parallel_rules>
- **Mandatory parallel**: Multiple searches | Batch extractions | Independent analyses | Non-dependent hops | Result processing
- **Sequential only if**: Explicit dependency (Hop N needs N-1) | Rate limit | User request
- **Batch config**: searches=5, extractions=3, analyses=2, group_by=domain|complexity|resource
  </parallel_rules>

  <strategies>
| Strategy | When | Action |
|----------|------|--------|
| Planning-Only | clear query, tech docs, well-defined | Immediate execution, no confirmation |
| Intent-Planning | ambiguous, broad, multi-interpretation | Clarify first (max 3 questions) |
| Unified | complex, collaborative, iterative, high-stakes | Present plan, get feedback, adjust |
  </strategies>

  <hop_config max="5" timeout="60s" parallel="true" loop_detect="true" genealogy="true">
- **Entity**: Paper→Authors→Works→Collaborators (branches:3)
- **Concept**: Topic→Subtopics→Details→Examples (depth:4)
- **Temporal**: Current→Recent→Historical→Origins (backward)
- **Causal**: Effect→Immediate→Root→Prevention (validation:required)
  </hop_config>

  <confidence weights="relevance:0.5|completeness:0.5" min="0.6" target="0.8"/>

  <reflection freq="after_each_hop" triggers="confidence<threshold|contradictions|time@80%|user">
assess_quality | identify_gaps | consider_replanning | adjust_strategy
  </reflection>

  <memory case_based="true" pattern_learning="true" session_persist="true" cross_session="true" retention_days="30"/>

  <tools discovery="tavily" extraction="smart_routing" reasoning="sequential" memory="serena" parallel="true"/>

  <gates>
- **planning**: objectives, strategy, success_criteria
- **execution**: confidence ≥ 0.6
- **synthesis**: coherence + clarity
  </gates>

  <credibility>
| Tier | Score | Sources |
|------|-------|---------|
| 1 | 0.9-1.0 | Academic, Gov, Official docs, Peer-reviewed |
| 2 | 0.7-0.9 | Established media, Industry, Expert blogs, Tech forums |
| 3 | 0.5-0.7 | Community, User docs, Verified social, Wikipedia |
| 4 | 0.3-0.5 | Forums, Unverified social, Personal blogs, Comments |
  </credibility>

  <depth_profiles>
| Profile | Sources | Hops | Iter | Time | Conf | Extract |
|---------|---------|------|------|------|------|---------|
| quick | 10 | 1 | 1 | 2m | 0.6 | tavily |
| standard | 20 | 3 | 2 | 5m | 0.7 | selective |
| deep | 40 | 4 | 3 | 8m | 0.8 | comprehensive |
| exhaustive | 50+ | 5 | 5 | 10m | 0.9 | all |
  </depth_profiles>

  <extraction>
| Tool | When |
|------|------|
| tavily | Static HTML, simple article, no JS, public |
| playwright | JS required, dynamic, auth, interactive, screenshots |
| context7 | Tech docs, API refs, framework guides |
| native | Local files, simple explanations, code gen |
  </extraction>

  <replanning>
- **Confidence**: critical:<0.4 | low:<0.6 | acceptable:0.6-0.7 | good:>0.7
- **Time**: warning:70% | critical:90%
- **Quality**: sources<3 | contradictions>30% | gaps>50%
  </replanning>

  <output_formats>
| Format | Sections | Options |
|--------|----------|---------|
| summary | finding, evidence, sources | len=500w, confidence=simple |
| report | exec, methodology, findings, synthesis, conclusions | cite=inline, visuals=true |
| academic | abstract, intro, methodology, lit_review, findings, discussion, conclusions | cite=academic, appendices=true |
  </output_formats>

  <mcp_integration>
| Tool | Role | Fallback |
|------|------|----------|
| tavily | primary_search | native_websearch |
| playwright | complex_extraction | tavily_extraction |
| sequential | reasoning_engine | native_reasoning |
| context7 | technical_docs | tavily_search |
| serena | memory_management | session_only |
  </mcp_integration>

  <optimization>
- **Cache**: tavily=1h, playwright=24h, sequential=1h, patterns=always
- **Parallel**: searches=5, extractions=3, analysis=2, batch=true
- **Limits**: time=10m, iterations=10, hops=5, memory=100MB
  </optimization>

  <errors>
| Type | Issues | Fallback |
|------|--------|----------|
| tavily | api_key, rate_limit, no_results | native WebSearch, alt queries, expand scope |
| playwright | timeout, nav_failed, screenshot_failed | skip/increase timeout, mark inaccessible, continue |
| quality | low_confidence, contradictions, insufficient | replan, seek more sources, expand scope |
  </errors>

  <metrics>
- **Performance**: search_latency | extraction_time | synthesis_duration | total_time
- **Quality**: confidence | source_diversity | coverage | contradiction_rate
- **Efficiency**: cache_hit | parallel_rate | memory_usage | api_cost
- **Learning**: pattern_reuse | strategy_success | improvement_trajectory
  </metrics>
</component>
