<component name="research-config" type="core" priority="medium">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>research|deep-research|planning|hop|confidence|tavily</triggers>

  <role>
    <mission>Deep research configuration and strategy settings</mission>
  </role>

  <defaults>
planning: unified | max_hops: 5 | confidence: 0.7 | memory: true | parallel: true (DEFAULT)
  </defaults>

  <parallel_rules>
- Mandatory: Multiple searches | Batch extractions | Independent analyses | Non-dependent hops
- Sequential only: Explicit dependency | Rate limit | User request
- Batch: searches=5, extractions=3, analyses=2, group_by=domain|complexity|resource
  </parallel_rules>

  <strategies>
| Strategy | When | Action |
|----------|------|--------|
| Planning-Only | clear query, tech docs | Immediate execution |
| Intent-Planning | ambiguous, broad | Clarify first (max 3 questions) |
| Unified | complex, collaborative | Present plan, get feedback |
  </strategies>

  <hop_config max="5" timeout="60s" parallel="true" loop_detect="true">
- Entity: Paper→Authors→Works→Collaborators (branches:3)
- Concept: Topic→Subtopics→Details→Examples (depth:4)
- Temporal: Current→Recent→Historical→Origins
- Causal: Effect→Immediate→Root→Prevention (validation:required)
  </hop_config>

  <confidence weights="relevance:0.5|completeness:0.5" min="0.6" target="0.8"/>

  <reflection freq="after_each_hop" triggers="confidence<threshold|contradictions|time@80%">
assess_quality | identify_gaps | consider_replanning | adjust_strategy
  </reflection>

  <memory case_based="true" pattern_learning="true" cross_session="true" retention_days="30"/>

  <tool_routing>
| Tool | Primary Use | Fallback |
|------|-------------|----------|
| tavily | Search, static HTML, public content | native WebSearch, alt queries |
| playwright | JS required, dynamic, auth, interactive | tavily extraction |
| sequential | Reasoning, synthesis, analysis | native reasoning |
| context7 | Tech docs, API refs, framework guides | tavily search |
| serena | Memory, session persistence | session only |
  </tool_routing>

  <gates>
planning: objectives+strategy+criteria | execution: confidence≥0.6 | synthesis: coherence+clarity
  </gates>

  <credibility>
| Tier | Score | Sources |
|------|-------|---------|
| 1 | 0.9-1.0 | Academic, Gov, Official, Peer-reviewed |
| 2 | 0.7-0.9 | Established media, Industry, Expert |
| 3 | 0.5-0.7 | Community, Wikipedia, Verified social |
| 4 | 0.3-0.5 | Forums, Unverified, Personal blogs |
  </credibility>

  <depth_profiles>
| Profile | Sources/Hops/Iter | Time | Conf | Extract |
|---------|-------------------|------|------|---------|
| quick | 10/1/1 | 2m | 0.6 | tavily |
| standard | 20/3/2 | 5m | 0.7 | selective |
| deep | 40/4/3 | 8m | 0.8 | comprehensive |
| exhaustive | 50+/5/5 | 10m | 0.9 | all |
  </depth_profiles>

  <output_formats>
| Format | Key Sections |
|--------|--------------|
| summary | finding, evidence, sources (500w) |
| report | exec, methodology, findings, synthesis, conclusions |
| academic | abstract, lit_review, methodology, findings, discussion |
  </output_formats>

  <replanning>
confidence: critical<0.4|low<0.6|acceptable≥0.6|good>0.7
time: warning@70%|critical@90%
quality: sources<3|contradictions>30%|gaps>50%
  </replanning>

  <optimization>
cache: tavily=1h|playwright=24h|sequential=1h|patterns=always
parallel: searches=5|extractions=3|analysis=2
limits: time=10m|iterations=10|hops=5|memory=100MB
  </optimization>

  <errors>
- tavily: api_key|rate_limit|no_results → native WebSearch, alt queries, expand scope
- playwright: timeout|nav_failed → skip/increase timeout, mark inaccessible
- quality: low_confidence|contradictions → replan, seek more sources
  </errors>

  <metrics>
perf: search_latency|extraction_time|synthesis_duration|total_time
quality: confidence|source_diversity|coverage|contradiction_rate
efficiency: cache_hit|parallel_rate|memory_usage|api_cost
  </metrics>
</component>
