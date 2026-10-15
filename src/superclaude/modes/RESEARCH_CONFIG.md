<component name="research-config" type="config">
  <role>
    <mission>Deep research configuration and strategy settings</mission>
  </role>

  <defaults>
planning: chosen by query clarity per the strategies table when no --strategy is given, so a clear query runs without waiting for approval (--depth quick always runs without asking) | max_hops: 5 | memory: true | parallel: true (DEFAULT)
  </defaults>

  <parallel_rules>
- Mandatory: Many searches | Batch extracts | Independent analyses | Independent hops
- Sequential only: Explicit dependency | Rate limit | User request
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
| playwright | JS required, dynamic, auth, interactive | tavily extraction |
| context7 | Tech docs, API refs, framework guides | tavily search |
  </tool_routing>

  <gates>
planning: objectives+strategy+criteria | execution: each load-bearing claim has ≥2 independent sources, except a claim settled by one primary source (the official documentation, specification, or primary record of the thing itself); a claim with only one source is labeled single-source, no open contradiction on a load-bearing claim | synthesis: coherence+clarity
  </gates>

  <credibility>
| Tier | Sources |
|------|---------|
| 1 | Academic, Gov, Official, Peer-reviewed |
| 2 | Established media, Industry, Expert |
| 3 | Community, Wikipedia, Verified social |
| 4 | Forums, Unverified, Personal blogs |
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
replan when: sources disagree on a load-bearing claim | a load-bearing claim has fewer than 2 independent sources, unless one primary source (the official documentation, specification, or primary record of the thing itself) settles it — no second source can outrank that, so label the claim single-source and continue | the core question is still unanswered
  </replanning>

  <errors>
- tavily: api_key|rate_limit|no_results → native WebSearch, alt queries, widen scope
- playwright: timeout|nav_failed → skip/raise timeout, mark unreachable
- quality: thin sources|contradictions → replan, get more sources
  </errors>

  <handoff next="/sc:research /sc:document"/>
</component>