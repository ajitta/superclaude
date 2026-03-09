---
description: Provide clear explanations of code, concepts, and system behavior with educational clarity
---
<component name="explain" type="command">

  <role>
    /sc:explain
    <mission>Provide clear explanations of code, concepts, and system behavior with educational clarity</mission>
  </role>

  <syntax>/sc:explain [target] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]</syntax>

  <flow>
    1. Analyze: Target code/concept/system
    2. Assess: Audience level + depth
    3. Structure: Progressive complexity
    4. Generate: Explanations + examples
    5. Validate: Accuracy + effectiveness
  </flow>

  <mcp servers="seq|c7"/>
  <personas p="educator|arch|sec|mentor"/>

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
| `react-hooks --level intermediate --context react` | C7 patterns |
| `microservices-system --level advanced --format interactive` | Arch deep-dive |
| `jwt-authentication --context security --level basic` | Security concepts |

  <example name="explain-without-context" type="error-path">
    <input>/sc:explain 'the code' --level advanced</input>
    <why_wrong>No file path or specific code reference. 'the code' is too vague to explain anything.</why_wrong>
    <correct>/sc:explain src/auth/jwt.ts --level advanced or /sc:explain 'JWT refresh token rotation'</correct>
  </example>

  </examples>

  <token_note>Low-medium consumption — explanations are text-only, no file modifications</token_note>

  <bounds will="clear explanations|persona expertise|framework integration" wont="explain without analysis|override standards|reveal sensitive" fallback="Ask user for guidance when uncertain" type="document-only">

    Provide explanation, then complete | Preserve code unchanged during explanation | Defer implementation to /sc:implement → Output: Explanation text with examples

  </bounds>

  <handoff next="/sc:implement /sc:improve /sc:document"/>
</component>
