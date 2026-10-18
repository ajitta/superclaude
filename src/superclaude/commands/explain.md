---
description: Give clear explanations of code, concepts and system behavior with progressive depth and examples. Use when asked for a structured walkthrough tailored to an audience. Not for "what does this function do?" — answer in 1-2 sentences.
---
<component name="explain" type="command">

  <role command="/sc:explain">
    <mission>Give clear explanations of code, concepts and system behavior with educational clarity</mission>
  </role>

  <syntax>/sc:explain [target] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]</syntax>

  <flow>
  1. Analyze: Target code/concept/system
  2. Assess: Audience level + depth
  3. Structure: Progressive complexity
  4. Generate: Explain + examples
  5. Validate: Accuracy + effective
  </flow>

  <flags>
  - --level basic|intermediate|advanced: audience level that the Assess step otherwise infers: basic assumes no domain knowledge, advanced assumes the reader knows the domain.
  - --context <domain>: domain that frames the explanation (e.g. react, security); for a library, look up its current docs first.
  - --format text|examples|interactive: text: prose; examples: lead with runnable examples; interactive: explain in steps with one comprehension question between steps.
  </flags>

  <examples>

  <example name="explain-without-context" type="error-path">
    - Input: /sc:explain 'the code' --level advanced
    - Why wrong: No file path or specific code ref. 'the code' too vague to explain.
    - Correct: /sc:explain src/auth/jwt.ts --level advanced or /sc:explain 'JWT refresh token rotation'
  </example>

  </examples>

  <gotchas>
  - symbolic-first: prefer symbol-aware queries (when connected) or targeted Grep for code exploration, not full file read
  - audience: Check user context/memory for expertise level before pick explain depth
  </gotchas>

  <bounds>
    <does>clear explanations, agent expertise, framework integration.</does>
    <never>explains without analysis, overrides standards, or reveals sensitive information.</never>
  </bounds>

  <handoff next="/sc:implement /sc:improve /sc:document"/>
</component>