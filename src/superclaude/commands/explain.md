---
description: Provide clear explanations of code, concepts, and system behavior with educational clarity
---
<component name="explain" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <constraints note="Reinforced from RULES.md">Scope: build only what's asked | Read before edit | No adjacent improvements</constraints>

  <role>
    /sc:explain
    <mission>Provide clear explanations of code, concepts, and system behavior with educational clarity</mission>
  </role>

  <syntax>/sc:explain [target] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]</syntax>

  <triggers>code understanding|system behavior|educational content|framework concepts</triggers>

  <flow>
    1. Analyze: Target code/concept/system
    2. Assess: Audience level + depth
    3. Structure: Progressive complexity
    4. Generate: Explanations + examples
    5. Validate: Accuracy + effectiveness
  </flow>

  <mcp servers="seq|c7"/>
  <personas p="educator|arch|sec"/>

  <tools>
    - Read/Grep/Glob: Code analysis + pattern ID
    - TaskCreate/TaskUpdate: Multi-part explanation tracking
    - Task: Complex explanation delegation
  </tools>

  <patterns>
    - Progressive: Basic → intermediate → advanced
    - Framework: C7 docs → official patterns
    - Multi-Domain: Technical + clarity + security
    - Interactive: Static → examples → exploration
  </patterns>

  <checklist note="Completion criteria">
    - [ ] Target code/concept fully analyzed (read source first)
    - [ ] Explanation matches requested --level
    - [ ] Examples provided for clarity (runnable code shown)
    - [ ] Output format matches --format
  </checklist>

  <examples>

| Input | Output |
|-------|--------|
| `authentication.js --level basic` | Beginner explanation |
| `react-hooks --intermediate --context react` | C7 patterns |
| `microservices-system --advanced --interactive` | Arch deep-dive |
| `jwt-authentication --context security --basic` | Security concepts |

  </examples>

  <bounds will="clear explanations|persona expertise|framework integration" wont="explain without analysis|override standards|reveal sensitive" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only" critical="true">
    <rule>Provide explanation, then complete</rule>
    <rule>Preserve code unchanged during explanation</rule>
    <rule>Defer implementation to /sc:implement</rule>
    <output>Explanation text with examples</output>
  </boundaries>

  <handoff>
    <next command="/sc:implement">For implementing explained concepts</next>
    <next command="/sc:improve">For applying explained best practices</next>
    <next command="/sc:document">For formal documentation</next>
    <format>Provide concept context for implementation</format>
  </handoff>
</component>
