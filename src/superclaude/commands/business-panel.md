---
description: Multi-expert biz analysis w/ adaptive modes. Use when user types `/sc:business-panel` or asks multi-expert (Porter, Christensen, Drucker, etc.) panel review of strategy decision. Do NOT auto-trigger on single-perspective biz question or quick "what's trade-off?" — those get direct answer.
---
<component name="business-panel" type="command">

  <role command="/sc:business-panel">
    <mission>Multi-expert biz analysis w/ adaptive modes</mission>
  </role>

  <syntax>/sc:business-panel [doc|content] [--experts "names"] [--mode discussion|debate|socratic|adaptive] [--focus domain] [--all-experts] [--synthesis-only] [--structured]</syntax>
  <flow>
  1. Route: ID domain + pick mode (Discussion, Debate, Socratic)
  2. Analyze: Apply 2-3 expert frameworks, surface agree/diverge
  3. Synthesize: Integrate cross-framework w/ trade-off clarity
  4. Present: Multi-lens analysis w/ labeled expert attributions
  </flow>


  <experts>
    - Christensen: Disruption Theory, Jobs-to-be-Done
    - Porter: Competitive Strategy, Five Forces
    - Drucker: Mgmt Philosophy, MBO
    - Godin: Marketing Innovation, Tribe Building
    - Kim-Mauborgne: Blue Ocean Strategy
    - Collins: Org Excellence, Good to Great
    - Taleb: Risk Mgmt, Antifragility
    - Meadows: Systems Thinking, Leverage Points
    - Doumont: Comm Systems, Structured Clarity
  </experts>

  <modes>
    - discussion: Collaborative, experts build on insights
    - debate: Adversarial for controversial topics
    - socratic: Question-driven for deep learning
    - adaptive: System picks by content
  </modes>

  <options>
    - --experts: Pick specific: "porter,christensen,meadows"
    - --focus: Auto-pick for domain
    - --all-experts: Include all 9
    - --synthesis-only: Skip detail, show synthesis
    - --structured: Use symbol system
  </options>


  <examples>

| Input | Output |
|---|---|
| `market-analysis.md --mode discussion --focus strategy` | Collaborative expert analysis |
| `'SaaS pricing strategy' --experts "porter,godin" --mode debate` | Adversarial pricing analysis |
| `startup-pitch.md --mode socratic --all-experts` | Deep questioning w/ all 9 experts |
| `competitive-landscape.md --synthesis-only` | Summary synthesis only |

  <example name="panel-technical-question" type="error-path">
    - Input: /sc:business-panel 'how to fix my React useState bug'
    - Why wrong: Panel gives strategy analysis, not tech debug. Wrong tool for code.
    - Correct: /sc:troubleshoot for bugs, /sc:explain for concepts. Use /sc:business-panel for market, strategy, competitive analysis.
  </example>

  </examples>


  <gotchas>
  - single-framework: Always apply 2+ expert frameworks. Single-framework violates command purpose
  - opinion-as-fact: Label which framework drives each claim. Never present opinions as consensus
  </gotchas>

  <bounds>
    <does>multi-expert analysis, adaptive modes, comprehensive synthesis.</does>
    <never>replace pro advice or decide for user.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:brainstorm /sc:design"/>
</component>