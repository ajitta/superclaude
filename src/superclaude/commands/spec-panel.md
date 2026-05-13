---
description: Multi-expert spec review + improvement via renowned software engineering experts. Use when user types `/sc:spec-panel` or asks for multi-expert panel critique (Fowler, Beck, Martin, etc.) of software spec. Do NOT auto-trigger on routine spec read or single-reviewer feedback — those get direct review.
---
<component name="spec-panel" type="command">

  <role command="/sc:spec-panel">
    <mission>Multi-expert spec review + improvement via renowned software engineering experts</mission>
  </role>

  <syntax>/sc:spec-panel [spec|@file] [--mode discussion|critique|socratic] [--experts "name1,name2"] [--focus implementability|simplicity|reliability|testing|observability] [--iterations N]</syntax>

  <flow>
  1. Analyze: parse spec
  2. Assemble: pick experts
  3. Review: multi-expert analysis
  4. Collaborate: expert dialogue
  5. Synthesize: improvement roadmap
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
    - discussion: sequential expert dialogue, builds insights
    - critique: Issue → Severity → Recommendation → Priority
    - socratic: deep questioning, surface assumptions
  </modes>

  <focus_areas>
    - implementability (Osmani,Beck): AI executability, modularity, testability
    - simplicity (Hickey,Fowler): essential vs accidental complexity, patterns
    - reliability (Nygard,Majors): failure modes, resilience, observability
    - testing (Beck,Majors): test strategy, verification, prod validation
    - observability (Majors,Nygard): debugging, monitoring, incident response
  </focus_areas>

  <examples>

| Input | Output |
|---|---|
| `@auth_api.yml --mode critique --focus implementability,reliability` | Multi-focus review |
| `'user story' --mode discussion --experts 'osmani,hickey'` | Expert dialogue |
| `@system.yml --mode socratic --iterations 3` | Deep questioning |

  <example name="spec-no-document" type="error-path">
    - Input: /sc:spec-panel --mode critique (no spec doc)
    - Why wrong: panel review needs spec doc to critique. No input = no structured review.
    - Correct: provide spec: /sc:spec-panel @api-spec.yml --mode critique --focus implementability
  </example>
  </examples>


  <gotchas>
  - existing-spec: check if spec exists before review. Build on existing work
  - necessity-test: apply R18 to each proposed spec addition. Spec only what needed
  </gotchas>

  <bounds>
    <does>expert-level review, actionable recs, multi-mode analysis.</does>
    <never>replace human judgment, modify without consent, legal guarantees.</never>
    <fallback>ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:design /sc:implement"/>
</component>