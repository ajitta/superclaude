---
description: Multi-expert business analysis with adaptive interaction modes. Use when the user types `/sc:business-panel` or asks for a multi-expert (Porter, Christensen, Drucker, etc.) panel review of a strategy decision. Do NOT auto-trigger on a single-perspective business question or quick "what's the trade-off?" — those get a direct answer.
---
<component name="business-panel" type="command">

  <role command="/sc:business-panel">
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
|---|---|
| `market-analysis.md --mode discussion --focus strategy` | Collaborative expert analysis |
| `'SaaS pricing strategy' --experts "porter,godin" --mode debate` | Adversarial pricing analysis |
| `startup-pitch.md --mode socratic --all-experts` | Deep questioning with all 9 experts |
| `competitive-landscape.md --synthesis-only` | Summary synthesis only |

  <example name="panel-technical-question" type="error-path">
    - Input: /sc:business-panel 'how to fix my React useState bug'
    - Why wrong: Business panel provides strategic analysis, not technical debugging. Wrong tool for code issues.
    - Correct: /sc:troubleshoot for bugs, /sc:explain for concepts. Use /sc:business-panel for market, strategy, competitive analysis.
  </example>

  </examples>


  <gotchas>
  - single-framework: Always apply 2+ expert frameworks. Single-framework analysis violates the command's purpose
  - opinion-as-fact: Label which expert framework drives each claim. Never present opinions as consensus
  </gotchas>

  <bounds>
    <does>multi-expert analysis, adaptive modes, and comprehensive synthesis.</does>
    <never>replace professional advice and make decisions for user.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:brainstorm /sc:design"/>
</component>
