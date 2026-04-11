---
description: Multi-expert specification review and improvement using renowned software engineering experts
---
<component name="spec-panel" type="command">

  <role>
    /sc:spec-panel
    <mission>Multi-expert specification review and improvement using renowned software engineering experts</mission>
  </role>

  <syntax>/sc:spec-panel [spec|@file] [--mode discussion|critique|socratic] [--experts "name1,name2"] [--focus implementability|simplicity|reliability|testing|observability] [--iterations N]</syntax>

  <flow>
    1. Analyze: Parse spec content
    2. Assemble: Select relevant experts
    3. Review: Multi-expert analysis
    4. Collaborate: Expert dialogue
    5. Synthesize: Improvement roadmap
  </flow>


  <experts>
    - Osmani (AI implementability, modular specs): "Can an AI agent execute this section by section?"
    - Hickey (Essential complexity, data-driven design): "What's left after removing accidental complexity?"
    - Beck (Testability, incremental design): "What's the first failing test?"
    - Fowler (Interface design, patterns): "Are concerns properly separated?"
    - Nygard (Failure modes, resilience): "What happens when this fails at 3AM?"
    - Majors (Observability, production debugging): "How do you debug this in production?"
  </experts>

  <modes>
    - discussion: Sequential expert dialogue building insights
    - critique: Issue → Severity → Recommendation → Priority
    - socratic: Deep questioning to surface assumptions
  </modes>

  <focus_areas>
    - implementability (Osmani,Beck): AI executability, modularity, testability
    - simplicity (Hickey,Fowler): Essential vs accidental complexity, patterns
    - reliability (Nygard,Majors): Failure modes, resilience, observability
    - testing (Beck,Majors): Test strategy, verification, production validation
    - observability (Majors,Nygard): Debugging, monitoring, incident response
  </focus_areas>

  <examples>

| Input | Output |
|-------|--------|
| `@auth_api.yml --mode critique --focus implementability,reliability` | Multi-focus review |
| `'user story' --mode discussion --experts 'osmani,hickey'` | Expert dialogue |
| `@system.yml --mode socratic --iterations 3` | Deep questioning |

  <example name="spec-no-document" type="error-path">
    <input>/sc:spec-panel --mode critique (with no spec document provided)</input>
    <why_wrong>Panel review requires a specification document to critique. No input means no structured review possible.</why_wrong>
    <correct>Provide a spec: /sc:spec-panel @api-spec.yml --mode critique --focus implementability</correct>
  </example>
  </examples>


  <gotchas>
  - existing-spec: Check if a spec already exists before starting review. Build on existing work
  - necessity-test: Apply R18 to each proposed spec addition. Only spec what's needed
  </gotchas>

  <bounds should="expert-level review|actionable recs|multi-mode analysis" avoid="replace human judgment|modify without consent|legal guarantees" fallback="Ask user for guidance when uncertain">

    Produce expert review document, then complete | Preserve specifications unchanged | Provide recommendations; defer implementation to /sc:implement → Output: Expert review document with recommendations

  </bounds>

  <handoff next="/sc:design /sc:implement"/>
</component>
