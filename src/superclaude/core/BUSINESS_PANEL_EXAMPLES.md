<component name="business-panel-examples" type="core" priority="low">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>business-panel|example|usage|workflow|integration</triggers>

  <role>
    <mission>Usage examples and integration patterns for business panel</mission>
  </role>

  <basic_examples>
    <ex n="Strategic Plan">/sc:business-panel @strategy_doc.pdf → Discussion: Porter, Collins, Meadows, Doumont</ex>
    <ex n="Innovation">/sc:business-panel "AI customer service" --experts "christensen,drucker,godin" → JTBD, value, tribes</ex>
    <ex n="Risk Debate">/sc:business-panel @risk.md --mode debate → Taleb challenges, systems perspective</ex>
    <ex n="Learning">/sc:business-panel "competitive strategy" --mode socratic → Progressive questioning</ex>
  </basic_examples>

  <advanced_patterns>
    <p n="Multi-Doc">/sc:business-panel @research.pdf @competitor.xlsx @financials.csv --synthesis-only</p>
    <p n="Domain">/sc:business-panel @product.md --focus "innovation" --experts "christensen,drucker,meadows"</p>
    <p n="Structured">/sc:business-panel @exec.pptx --focus "communication" --structured</p>
  </advanced_patterns>

  <integrations>
    <i cmd="/analyze">/analyze @model.md --business-panel → Tech analysis + expert review</i>
    <i cmd="/improve">/improve @strategy.md --business-panel --iterative → Expert validation</i>
    <i cmd="/design">/design business-model --business-panel → Expert-guided design</i>
  </integrations>

  <expert_selection>
    <by domain="strategy" experts="porter,kim_mauborgne,collins,meadows"/>
    <by domain="innovation" experts="christensen,drucker,godin,meadows"/>
    <by domain="organization" experts="collins,drucker,meadows,doumont"/>
    <by domain="risk" experts="taleb,meadows,porter,collins"/>
    <by domain="market_entry" experts="porter,christensen,godin,kim_mauborgne"/>
    <by type="comprehensive" experts="all" mode="discussion→debate→synthesis"/>
    <by type="validation" experts="porter,collins,taleb" mode="debate"/>
    <by type="learning" experts="drucker,meadows,doumont" mode="socratic"/>
  </expert_selection>

  <output_formats>
    <f n="Executive">--structured --synthesis-only → 🎯Strategic|💰Financial|🏆Competitive|📈Growth|⚠️Risk|🧩Synthesis</f>
    <f n="Detailed">--verbose → Per-expert framework analysis + cross-framework synthesis</f>
    <f n="Questions">--questions → Strategic questions per expert framework</f>
  </output_formats>

  <workflows>
    <w n="Strategy">discussion(research) → debate(competitive) → socratic(synthesis) → design(strategy)</w>
    <w n="Innovation">panel(portfolio) → improve(roadmap) → analyze(opportunities)</w>
    <w n="Risk">panel(register) → debate(assumptions) → implement(mitigation)</w>
  </workflows>

  <customization>
    <opt n="Focus">--christensen-focus "disruption" | --porter-focus "moats"</opt>
    <opt n="Style">--interaction collaborative|challenging</opt>
    <opt n="Symbols">--symbols minimal|rich</opt>
    <opt n="Depth">--depth surface|detailed</opt>
    <opt n="Speed">--quick --experts-max 3 | --comprehensive --all-experts</opt>
  </customization>

  <quality>
    <v n="Authenticity">Voice consistency | Framework fidelity | Interaction realism</v>
    <v n="Relevance">Strategic focus | Actionable insights | Evidence-based</v>
    <v n="Integration">Synthesis value | Framework preservation | Practical utility</v>
    <perf response="simple&lt;30s|comprehensive&lt;2m|multi-doc&lt;5m" tokens="discussion:8-15K|debate:10-20K|socratic:12-25K|synthesis:3-8K" accuracy="framework&gt;90%|relevance&gt;85%|actionable&gt;80%"/>
  </quality>
</component>
