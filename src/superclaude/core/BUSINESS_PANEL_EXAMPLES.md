<component name="business-panel-examples" type="core" priority="low">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>business-panel|example|usage|workflow|integration</triggers>

  <role>
    <mission>Usage examples and integration patterns for business panel</mission>
  </role>

  <basic_examples>
- Strategic Plan: `/sc:business-panel @strategy_doc.pdf` → Discussion: Porter, Collins, Meadows, Doumont
- Innovation: `/sc:business-panel "AI customer service" --experts "christensen,drucker,godin"` → JTBD, value, tribes
- Risk Debate: `/sc:business-panel @risk.md --mode debate` → Taleb challenges, systems perspective
- Learning: `/sc:business-panel "competitive strategy" --mode socratic` → Progressive questioning
  </basic_examples>

  <advanced_patterns>
- Multi-Doc: `/sc:business-panel @research.pdf @competitor.xlsx @financials.csv --synthesis-only`
- Domain: `/sc:business-panel @product.md --focus "innovation" --experts "christensen,drucker,meadows"`
- Structured: `/sc:business-panel @exec.pptx --focus "communication" --structured`
  </advanced_patterns>

  <integrations>
- `/analyze @model.md --business-panel` → Tech analysis + expert review
- `/improve @strategy.md --business-panel --iterative` → Expert validation
- `/design business-model --business-panel` → Expert-guided design
  </integrations>

  <expert_selection>
| Domain/Type | Experts | Mode |
|-------------|---------|------|
| strategy | porter, kim_mauborgne, collins, meadows | - |
| innovation | christensen, drucker, godin, meadows | - |
| organization | collins, drucker, meadows, doumont | - |
| risk | taleb, meadows, porter, collins | - |
| market_entry | porter, christensen, godin, kim_mauborgne | - |
| comprehensive | all | discussion→debate→synthesis |
| validation | porter, collins, taleb | debate |
| learning | drucker, meadows, doumont | socratic |
  </expert_selection>

  <output_formats>
- Executive: `--structured --synthesis-only` → 🎯Strategic|💰Financial|🏆Competitive|📈Growth|⚠️Risk|🧩Synthesis
- Detailed: `--verbose` → Per-expert framework analysis + cross-framework synthesis
- Questions: `--questions` → Strategic questions per expert framework
  </output_formats>

  <workflows>
- Strategy: discussion(research) → debate(competitive) → socratic(synthesis) → design(strategy)
- Innovation: panel(portfolio) → improve(roadmap) → analyze(opportunities)
- Risk: panel(register) → debate(assumptions) → implement(mitigation)
  </workflows>

  <customization>
- Focus: `--christensen-focus "disruption"` | `--porter-focus "moats"`
- Style: `--interaction collaborative|challenging`
- Symbols: `--symbols minimal|rich`
- Depth: `--depth surface|detailed`
- Speed: `--quick --experts-max 3` | `--comprehensive --all-experts`
  </customization>

  <quality>
- Authenticity: Voice consistency | Framework fidelity | Interaction realism
- Relevance: Strategic focus | Actionable insights | Evidence-based
- Integration: Synthesis value | Framework preservation | Practical utility
- Performance: response=simple<30s|comprehensive<2m|multi-doc<5m, tokens=discussion:8-15K|debate:10-20K|socratic:12-25K|synthesis:3-8K, accuracy=framework>90%|relevance>85%|actionable>80%
  </quality>
</component>
