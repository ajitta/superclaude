---
description: Multi-expert business analysis with adaptive interaction modes
---
<component name="business-panel" type="command">

  <role>
    /sc:business-panel
    <mission>Multi-expert business analysis with adaptive interaction modes</mission>
  </role>

  <syntax>/sc:business-panel [doc|content] [--experts "names"] [--mode discussion|debate|socratic|adaptive] [--focus domain] [--all-experts] [--synthesis-only] [--structured]</syntax>
  <flow>
    1. Route: Identify domain and select interaction mode (Discussion, Debate, or Socratic)
    2. Analyze: Apply 2-3 expert frameworks, surface where they agree and diverge
    3. Synthesize: Integrate insights across frameworks with trade-off clarity
    4. Present: Deliver multi-lens analysis with labeled expert attributions
  </flow>


  <experts>
    - Christensen: Disruption Theory, Jobs-to-be-Done
    - Porter: Competitive Strategy, Five Forces
    - Drucker: Management Philosophy, MBO
    - Godin: Marketing Innovation, Tribe Building
    - Kim-Mauborgne: Blue Ocean Strategy
    - Collins: Organizational Excellence, Good to Great
    - Taleb: Risk Management, Antifragility
    - Meadows: Systems Thinking, Leverage Points
    - Doumont: Communication Systems, Structured Clarity
  </experts>

  <modes>
    - discussion: Collaborative analysis, experts build on insights
    - debate: Adversarial analysis for controversial topics
    - socratic: Question-driven exploration for deep learning
    - adaptive: System selects based on content
  </modes>

  <options>
    - --experts: Select specific: "porter,christensen,meadows"
    - --focus: Auto-select for domain
    - --all-experts: Include all 9
    - --synthesis-only: Skip detailed, show synthesis
    - --structured: Use symbol system
  </options>


  <examples>

| Input | Output |
|-------|--------|
| `market-analysis.md --mode discussion --focus strategy` | Collaborative expert analysis |
| `'SaaS pricing strategy' --experts "porter,godin" --mode debate` | Adversarial pricing analysis |
| `startup-pitch.md --mode socratic --all-experts` | Deep questioning with all 9 experts |
| `competitive-landscape.md --synthesis-only` | Summary synthesis only |

  <example name="panel-technical-question" type="error-path">
    <input>/sc:business-panel 'how to fix my React useState bug'</input>
    <why_wrong>Business panel provides strategic analysis, not technical debugging. Wrong tool for code issues.</why_wrong>
    <correct>/sc:troubleshoot for bugs, /sc:explain for concepts. Use /sc:business-panel for market, strategy, competitive analysis.</correct>
  </example>

  </examples>


  <gotchas>
  - single-framework: Always apply 2+ expert frameworks. Single-framework analysis violates the command's purpose
  - opinion-as-fact: Label which expert framework drives each claim. Never present opinions as consensus
  </gotchas>

  <bounds should="multi-expert analysis|adaptive modes|comprehensive synthesis" avoid="replace professional advice|make decisions for user" fallback="Ask user for guidance when uncertain">

    Produce business analysis document, then complete | Defer business decisions to stakeholders | Preserve code and configurations unchanged → Output: Business analysis synthesis document

  </bounds>

  <handoff next="/sc:brainstorm /sc:design"/>
</component>
