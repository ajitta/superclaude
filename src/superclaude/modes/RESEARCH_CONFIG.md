<component name="research-config" type="config">
  <role>
    <mission>Deep research config + strategy settings</mission>
  </role>

  <defaults>
planning: unified | max_hops: 5 | confidence: 0.7 | memory: true | parallel: true (DEFAULT)
  </defaults>

  <parallel_rules>
- Mandatory: Many searches | Batch extracts | Indep analyses | Non-dep hops
- Sequential only: Explicit dep | Rate limit | User ask
- Batch: searches=5, extractions=3, analyses=2, group_by=domain|complexity|resource
  </parallel_rules>

  <strategies>
| Strategy | When | Action |
|----------|------|--------|
| Planning-Only | clear query, tech docs | Run now |
| Intent-Planning | ambiguous, broad | Clarify first (max 3 questions) |
| Unified | complex, collab | Show plan, get feedback |
  </strategies>

  <hop_config max="5" parallel="true" loop_detect="true">
- Entity: Paper→Authors→Works→Collaborators (branches:3)
- Concept: Topic→Subtopics→Details→Examples (depth:4)
- Temporal: Current→Recent→Historical→Origins
- Causal: Effect→Immediate→Root→Prevention (validation:required)
  </hop_config>

  <reflection freq="after_each_hop" triggers="thin sources|contradictions|core question unanswered">
assess_quality | id_gaps | maybe_replan | tweak_strategy
  </reflection>

  <memory case_based="true" pattern_learning="true" cross_session="true"/>

  <tool_routing>
| Tool | Primary Use | Fallback |
|------|-------------|----------|
| tavily | Search, static HTML, public content | native WebSearch, alt queries |
| playwright | JS need, dynamic, auth, interactive | tavily extraction |
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
| Profile | Sources/Hops/Iter | Extract |
|---------|-------------------|---------|
| quick | 10/1/1 | tavily |
| standard | 20/3/2 | selective |
| deep | 40/4/3 | comprehensive |
| exhaustive | 50+/5/5 | all |
  </depth_profiles>

  <output_formats>
| Format | Key Sections |
|--------|--------------|
| summary | finding, evidence, sources — short enough to scan |
| report | exec, methodology, findings, synthesis, conclusions |
| academic | abstract, lit_review, methodology, findings, discussion |
  </output_formats>

  <replanning>
replan when: sources disagree on a load-bearing claim | fewer than 3 independent sources | the core question is still unanswered
  </replanning>

  <errors>
- tavily: api_key|rate_limit|no_results → native WebSearch, alt queries, widen scope
- playwright: timeout|nav_failed → skip/raise timeout, mark unreachable
- quality: low_confidence|contradictions → replan, get more sources
  </errors>

  <handoff next="/sc:research /sc:document"/>
</component>