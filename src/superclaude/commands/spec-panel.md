---
description: Multi-expert specification review and improvement using renowned software engineering experts
---
<component name="spec-panel" type="command">

  <role>
    /sc:spec-panel
    <mission>Multi-expert specification review and improvement using renowned software engineering experts</mission>
  </role>

  <syntax>/sc:spec-panel [spec|@file] [--mode discussion|critique|socratic] [--experts "name1,name2"] [--focus requirements|architecture|testing|compliance] [--iterations N]</syntax>

  <triggers>specification review|expert panel analysis|requirements quality</triggers>

  <flow>
    1. Analyze: Parse spec content
    2. Assemble: Select relevant experts
    3. Review: Multi-expert analysis
    4. Collaborate: Expert dialogue
    5. Synthesize: Improvement roadmap
  </flow>

  <mcp servers="seq|c7"/>
  <personas p="arch|qa|pm"/>

  <experts>
    - Wiegers (Requirements quality, SMART): "How would you validate this?"
    - Adzic (BDD, Given/When/Then): "Concrete examples?"
    - Cockburn (Use cases, goals): "Primary stakeholder?"
    - Fowler (API design, patterns): "Separation of concerns?"
    - Nygard (Production reliability): "What happens when this fails?"
    - Newman (Microservices): "Service evolution?"
    - Crispin (Testing strategies): "How to validate?"
    - Hightower (Cloud native, K8s): "Cloud deployment?"
  </experts>

  <modes>
    - discussion: Sequential expert dialogue building insights
    - critique: Issue → Severity → Recommendation → Priority
    - socratic: Deep questioning to surface assumptions
  </modes>

  <focus_areas>
    - requirements (Wiegers,Adzic,Cockburn): Clarity, testability, acceptance
    - architecture (Fowler,Newman,Nygard): Interfaces, boundaries, patterns
    - testing (Crispin,Adzic): Strategy, edge cases, validation
    - compliance (Wiegers,Nygard): Security, regulatory, audit
  </focus_areas>


  <examples>

| Input | Output |
|-------|--------|
| `@auth_api.yml --mode critique --focus requirements,architecture` | Multi-focus review |
| `'user story' --mode discussion --experts 'wiegers,adzic'` | Expert dialogue |
| `@system.yml --mode socratic --iterations 3` | Deep questioning |

  </examples>

  <bounds will="expert-level review|actionable recs|multi-mode analysis" wont="replace human judgment|modify without consent|legal guarantees" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Produce expert review document, then complete | Preserve specifications unchanged | Provide recommendations; defer implementation to /sc:implement → Output: Expert review document with recommendations</boundaries>


  <handoff next="/sc:design /sc:implement"/>
</component>
