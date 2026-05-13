---
description: Give clear explain of code, concepts, system behavior with edu clarity. Use when user type `/sc:explain` or ask for structured walkthrough with progressive depth, examples, audience tailor. Do NOT auto-trigger on "what does this function do?" or short factual lookup — those get 1-2 sentence direct answer.
---
<component name="explain" type="command">

  <role command="/sc:explain">
    <mission>Give clear explain of code, concepts, system behavior with edu clarity</mission>
  </role>

  <syntax>/sc:explain [target] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]</syntax>

  <flow>
  1. Analyze: Target code/concept/system
  2. Assess: Audience level + depth
  3. Structure: Progressive complexity
  4. Generate: Explain + examples
  5. Validate: Accuracy + effective
  </flow>


  <tools>
  - Read/Grep/Glob: Code analyze + pattern ID
  - TaskCreate/TaskUpdate: Multi-part explain track
  - Task: Complex explain delegate
  </tools>

  <patterns>
    - Progressive: Basic → intermediate → advanced
    - Framework: C7 docs → official patterns
    - Multi-Domain: Technical + clarity + security
    - Interactive: Static → examples → explore
  </patterns>

  <examples>

| Input | Output |
|---|---|
| `authentication.js --level basic` | Beginner explain |
| `react-hooks --level intermediate --context react` | C7 patterns |
| `microservices-system --level advanced --format interactive` | Arch deep-dive |
| `jwt-authentication --context security --level basic` | Security concepts |

  <example name="explain-without-context" type="error-path">
    - Input: /sc:explain 'the code' --level advanced
    - Why wrong: No file path or specific code ref. 'the code' too vague to explain.
    - Correct: /sc:explain src/auth/jwt.ts --level advanced or /sc:explain 'JWT refresh token rotation'
  </example>

  </examples>


  <gotchas>
  - serena-first: Use Serena symbolic tools for code explore, not full file read
  - audience: Check user context/memory for expertise level before pick explain depth
  </gotchas>

  <bounds>
    <does>clear explain, agent expertise, framework integration.</does>
    <never>explain without analyze, override standards, reveal sensitive.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:improve /sc:document"/>
</component>