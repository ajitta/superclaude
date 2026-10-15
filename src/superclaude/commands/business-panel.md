---
description: Multi-expert business analysis (Porter, Christensen, Drucker and others) with adaptive modes. Use when asked for a multi-expert panel review of a strategy decision. Not for a single-perspective business question — answer directly.
---
<component name="business-panel" type="command">

  <role command="/sc:business-panel">
    <mission>Multi-expert business analysis with adaptive modes</mission>
  </role>

  <syntax>/sc:business-panel [doc|content] [--experts "names"] [--mode discussion|debate|socratic|adaptive] [--focus domain] [--all-experts] [--synthesis-only] [--structured]</syntax>
  <flow>
  1. Route: identify the domain and pick the mode (Discussion, Debate, Socratic)
  2. Analyze: apply the selected experts' frameworks (2-3 by default; every named expert with --experts or --all-experts) and surface where they agree and diverge
  3. Synthesize: Integrate cross-framework with trade-off clarity
  4. Present: Multi-lens analysis with labeled expert attributions
  </flow>

  <flags>
  - --experts "names": panel members by surname from the experts section, e.g. "porter,christensen,meadows".
  - --mode discussion|debate|socratic|adaptive: one of the four modes in the modes section.
  - --focus domain: business domain (e.g. strategy, risk) that picks the experts the Analyze step applies; ignored when --experts or --all-experts is given; unrelated to the global --focus.
  - --all-experts: include all 9 experts in the experts section.
  - --synthesis-only: skip per-expert detail and show only the synthesis.
  - --structured: use the business symbol system (core/BUSINESS_SYMBOLS.md).
  </flags>

  <experts>9 lenses (surnames for --experts): christensen, porter, drucker, godin, kim-mauborgne, collins, taleb, meadows, doumont — frameworks per agents/business-panel-experts.md `<focus>` (SSOT).</experts>

  <modes>
    - discussion: Collaborative, experts build on insights
    - debate: Adversarial for controversial topics
    - socratic: Question-driven for deep learning
    - adaptive: System picks by content
  </modes>


  <examples>

| Input | Output |
|---|---|
| `market-analysis.md --mode discussion --focus strategy` | Collaborative expert analysis |
| `'SaaS pricing strategy' --experts "porter,godin" --mode debate` | Adversarial pricing analysis |
| `startup-pitch.md --mode socratic --all-experts` | Deep questioning with all 9 experts |
| `competitive-landscape.md --synthesis-only` | Summary synthesis only |

  <example name="panel-technical-question" type="error-path">
    - Input: /sc:business-panel 'how to fix my React useState bug'
    - Why wrong: Panel gives strategy analysis, not tech debug. Wrong tool for code.
    - Correct: /sc:troubleshoot for bugs, /sc:explain for concepts. Use /sc:business-panel for market, strategy, competitive analysis.
  </example>

  </examples>


  <gotchas>
  - single-framework: always apply at least 2 expert frameworks; a single-framework answer defeats the command's purpose.
  - opinion-as-fact: Label which framework drives each claim. Never present opinions as consensus
  </gotchas>

  <bounds>
    <does>multi-expert analysis, adaptive modes, comprehensive synthesis.</does>
    <never>replaces professional advice or decides for the user.</never>
  </bounds>

  <handoff next="/sc:brainstorm /sc:design"/>
</component>