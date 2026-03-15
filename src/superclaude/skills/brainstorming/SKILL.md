---
name: brainstorming
description: |
  Design-first exploration before any implementation. Use before creating features,
  building components, adding functionality, or modifying behavior. Explores user intent,
  requirements and design through collaborative dialogue before writing code.
---
<component name="brainstorming" type="skill">

  <role>
    <mission>Turn ideas into fully formed designs and specs through collaborative dialogue before any code is written</mission>
  </role>

  <when>
  - Before creating features, building components, adding functionality, or modifying behavior
  - When user intent, requirements, or design need exploration
  - Before any implementation work begins
  </when>

  <flow>
    1. Explore project context — check files, docs, recent commits to understand current state
    2. Offer visual companion (optional) — if the topic involves visual questions, offer the browser-based companion in a standalone message. If accepted, read `skills/brainstorming/visual-companion.md` before proceeding
    3. Ask clarifying questions — one question per message, multiple choice preferred when possible. Focus on purpose, constraints, and success criteria. If the request spans multiple independent subsystems, flag decomposition before diving into details
    4. Propose 2-3 approaches — with trade-offs, rough effort estimates (small/medium/large), and your recommendation. If options feel equivalent, say so
    5. Present design section by section — scale each section to its complexity. Ask after each section whether it looks right. Cover architecture, components, data flow, error handling, testing. YAGNI ruthlessly
    6. Write spec — save to `docs/specs/YYYY-MM-DD-<topic>-design.md` (user preferences override this path). Include problem statement, chosen approach, key decisions, interfaces, open questions. Commit to git
    7. Spec review loop — dispatch `spec-document-reviewer` subagent with crafted review context (not your session history). Fix issues and re-dispatch until approved, max 5 iterations before surfacing to human
    8. User review — ask user to review the written spec before proceeding. If they request changes, make them and re-run the review loop
    9. Handoff — invoke writing-plans skill to create the implementation plan
  </flow>

  <constraints>
  - Do not write code or invoke implementation skills until the user approves the design
  - Only one question per message — break multi-part topics into sequential questions
  - writing-plans is the only valid next skill after brainstorming
  - In existing codebases, follow established patterns. Include targeted improvements only where they serve the current goal
  - Do not propose unrelated refactoring
  </constraints>

  <bounds will="design exploration|spec writing|collaborative dialogue|review coordination" wont="write implementation code|invoke implementation skills before approval|propose unrelated refactoring"/>

  <handoff next="writing-plans"/>
</component>
