<component name="research-config" type="core" priority="medium">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>research|deep-research|planning|hop|confidence|tavily</triggers>

  <role>
    <mission>Deep research configuration and strategy settings</mission>
  </role>

  <defaults>
    <d n="planning">unified</d><d n="max_hops">5</d><d n="confidence">0.7</d>
    <d n="memory">true</d><d n="parallel">true (DEFAULT_MODE)</d>
  </defaults>

  <parallel_rules>
    <mandatory>Multiple searches | Batch extractions | Independent analyses | Non-dependent hops | Result processing</mandatory>
    <sequential_only_if>Explicit dependency (Hop N needs N-1) | Rate limit | User request</sequential_only_if>
    <batch searches="5" extractions="3" analyses="2" group_by="domain|complexity|resource"/>
  </parallel_rules>

  <strategies>
    <s n="Planning-Only" when="clear query, tech docs, well-defined">Immediate execution, no confirmation</s>
    <s n="Intent-Planning" when="ambiguous, broad, multi-interpretation">Clarify first (max 3 questions)</s>
    <s n="Unified" when="complex, collaborative, iterative, high-stakes">Present plan, get feedback, adjust</s>
  </strategies>

  <hop_config max="5" timeout="60s" parallel="true" loop_detect="true" genealogy="true">
    <pattern n="Entity">Paper→Authors→Works→Collaborators (branches:3)</pattern>
    <pattern n="Concept">Topic→Subtopics→Details→Examples (depth:4)</pattern>
    <pattern n="Temporal">Current→Recent→Historical→Origins (backward)</pattern>
    <pattern n="Causal">Effect→Immediate→Root→Prevention (validation:required)</pattern>
  </hop_config>

  <confidence weights="relevance:0.5|completeness:0.5" min="0.6" target="0.8"/>

  <reflection freq="after_each_hop" triggers="confidence&lt;threshold|contradictions|time@80%|user">
    assess_quality | identify_gaps | consider_replanning | adjust_strategy
  </reflection>

  <memory case_based="true" pattern_learning="true" session_persist="true" cross_session="true" retention_days="30"/>

  <tools discovery="tavily" extraction="smart_routing" reasoning="sequential" memory="serena" parallel="true"/>

  <gates>
    <g n="planning">objectives, strategy, success_criteria</g>
    <g n="execution">confidence ≥ 0.6</g>
    <g n="synthesis">coherence + clarity</g>
  </gates>

  <credibility>
    <tier n="1" score="0.9-1.0">Academic, Gov, Official docs, Peer-reviewed</tier>
    <tier n="2" score="0.7-0.9">Established media, Industry, Expert blogs, Tech forums</tier>
    <tier n="3" score="0.5-0.7">Community, User docs, Verified social, Wikipedia</tier>
    <tier n="4" score="0.3-0.5">Forums, Unverified social, Personal blogs, Comments</tier>
  </credibility>

  <depth_profiles>
    <p n="quick" sources="10" hops="1" iter="1" time="2m" conf="0.6" extract="tavily"/>
    <p n="standard" sources="20" hops="3" iter="2" time="5m" conf="0.7" extract="selective"/>
    <p n="deep" sources="40" hops="4" iter="3" time="8m" conf="0.8" extract="comprehensive"/>
    <p n="exhaustive" sources="50+" hops="5" iter="5" time="10m" conf="0.9" extract="all"/>
  </depth_profiles>

  <extraction>
    <route to="tavily" when="Static HTML, simple article, no JS, public"/>
    <route to="playwright" when="JS required, dynamic, auth, interactive, screenshots"/>
    <route to="context7" when="Tech docs, API refs, framework guides"/>
    <route to="native" when="Local files, simple explanations, code gen"/>
  </extraction>

  <replanning>
    <trigger type="confidence">critical:&lt;0.4 | low:&lt;0.6 | acceptable:0.6-0.7 | good:&gt;0.7</trigger>
    <trigger type="time">warning:70% | critical:90%</trigger>
    <trigger type="quality">sources&lt;3 | contradictions&gt;30% | gaps&gt;50%</trigger>
  </replanning>

  <output_formats>
    <f n="summary" len="500w" sections="finding,evidence,sources" confidence="simple"/>
    <f n="report" sections="exec,methodology,findings,synthesis,conclusions" cite="inline" visuals="true"/>
    <f n="academic" sections="abstract,intro,methodology,lit_review,findings,discussion,conclusions" cite="academic" appendices="true"/>
  </output_formats>

  <mcp_integration>
    <i tool="tavily" role="primary_search" fallback="native_websearch"/>
    <i tool="playwright" role="complex_extraction" fallback="tavily_extraction"/>
    <i tool="sequential" role="reasoning_engine" fallback="native_reasoning"/>
    <i tool="context7" role="technical_docs" fallback="tavily_search"/>
    <i tool="serena" role="memory_management" fallback="session_only"/>
  </mcp_integration>

  <optimization>
    <cache tavily="1h" playwright="24h" sequential="1h" patterns="always"/>
    <parallel searches="5" extractions="3" analysis="2" batch="true"/>
    <limits time="10m" iterations="10" hops="5" memory="100MB"/>
  </optimization>

  <errors>
    <e type="tavily" issues="api_key|rate_limit|no_results" fallback="native WebSearch, alt queries, expand scope"/>
    <e type="playwright" issues="timeout|nav_failed|screenshot_failed" fallback="skip/increase timeout, mark inaccessible, continue"/>
    <e type="quality" issues="low_confidence|contradictions|insufficient" fallback="replan, seek more sources, expand scope"/>
  </errors>

  <metrics>
    <m cat="perf">search_latency | extraction_time | synthesis_duration | total_time</m>
    <m cat="quality">confidence | source_diversity | coverage | contradiction_rate</m>
    <m cat="efficiency">cache_hit | parallel_rate | memory_usage | api_cost</m>
    <m cat="learning">pattern_reuse | strategy_success | improvement_trajectory</m>
  </metrics>
</component>
