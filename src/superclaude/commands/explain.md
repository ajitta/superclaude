---
description: Provide clear explanations of code, concepts, and system behavior with educational clarity
---
<component name="explain" type="command">

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


  <examples>

| Input | Output |
|-------|--------|
| `authentication.js --level basic` | Beginner explanation |
| `react-hooks --intermediate --context react` | C7 patterns |
| `microservices-system --advanced --interactive` | Arch deep-dive |
| `jwt-authentication --context security --basic` | Security concepts |

  </examples>

  <bounds will="clear explanations|persona expertise|framework integration" wont="explain without analysis|override standards|reveal sensitive" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Provide explanation, then complete | Preserve code unchanged during explanation | Defer implementation to /sc:implement → Output: Explanation text with examples</boundaries>


  <handoff next="/sc:implement /sc:improve /sc:document"/>
</component>
