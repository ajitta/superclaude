<component name="business-panel-examples" type="core" priority="low">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>business-panel|example|usage|workflow|integration</triggers>

  <role>
    <mission>Usage examples and integration patterns for business panel</mission>
  </role>

  <examples>
| Type | Command | Result |
|------|---------|--------|
| Strategic | `/sc:business-panel @strategy_doc.pdf` | Porter, Collins, Meadows discussion |
| Innovation | `/sc:business-panel "AI service" --experts "christensen,drucker,godin"` | JTBD, value, tribes |
| Risk Debate | `/sc:business-panel @risk.md --mode debate` | Taleb challenges, systems view |
| Learning | `/sc:business-panel "strategy" --mode socratic` | Progressive questioning |
| Multi-Doc | `/sc:business-panel @research.pdf @competitor.xlsx --synthesis-only` | Cross-doc synthesis |
| Domain | `/sc:business-panel @product.md --focus "innovation"` | Focused expert review |
  </examples>

  <integrations>
`/sc:analyze @model.md --business-panel` | `/sc:improve @strategy.md --business-panel` | `/sc:design business-model --business-panel`
  </integrations>

  <expert_selection>
| Domain | Experts |
|--------|---------|
| strategy | porter, kim_mauborgne, collins, meadows |
| innovation | christensen, drucker, godin, meadows |
| organization | collins, drucker, meadows, doumont |
| risk | taleb, meadows, porter, collins |
| market_entry | porter, christensen, godin, kim_mauborgne |
| comprehensive | all (discussion→debate→synthesis) |
| validation | porter, collins, taleb (debate mode) |
| learning | drucker, meadows, doumont (socratic mode) |
  </expert_selection>

  <output_formats>
- Executive: `--structured --synthesis-only` → 🎯Strategic|💰Financial|🏆Competitive|📈Growth|⚠️Risk|🧩Synthesis
- Detailed: default output (omit `--synthesis-only`) → Per-expert analysis + cross-framework synthesis
- Questions: `--questions` → Strategic questions per framework
  </output_formats>

  <workflows>
- Strategy: discussion(research) → debate(competitive) → socratic(synthesis)
- Innovation: panel(portfolio) → improve(roadmap) → analyze(opportunities)
- Risk: panel(register) → debate(assumptions) → implement(mitigation)
  </workflows>

  <customization>
focus: `--focus innovation|strategy|risk|systems`
experts: `--experts "porter,christensen,meadows"` | `--all-experts`
output: `--structured` | `--synthesis-only`
  </customization>

  <quality>
- Authenticity: voice consistency | framework fidelity | interaction realism
- Relevance: strategic focus | actionable insights | evidence-based
- Performance: simple<30s | comprehensive<2m | tokens: discussion 8-15K, debate 10-20K
  </quality>
</component>
