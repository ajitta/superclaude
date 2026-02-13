---
description: Multi-expert business analysis with adaptive interaction modes
---
<component name="business-panel" type="command">

  <role>
    /sc:business-panel
    <mission>Multi-expert business analysis with adaptive interaction modes</mission>
  </role>

  <syntax>/sc:business-panel [doc|content] [--experts "names"] [--mode discussion|debate|socratic|adaptive] [--focus domain]</syntax>

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

  <mcp servers="seq|c7"/>
  <personas p="anal|arch|mentor" auto="true"/>


  <bounds will="multi-expert analysis|adaptive modes|comprehensive synthesis" wont="replace professional advice|make decisions for user" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Produce business analysis document, then complete | Defer business decisions to stakeholders | Preserve code and configurations unchanged → Output: Business analysis synthesis document</boundaries>


  <handoff next="/sc:brainstorm /sc:design"/>
</component>
