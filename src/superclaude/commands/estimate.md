---
description: Give development estimates for tasks, features or projects — effort, risks, dependencies. Use when asked for a structured estimate of a feature, PRD or multi-task project. Not for a quick "is this hard?" — answer in one line.
---
<component name="estimate" type="command">

  <role command="/sc:estimate">
    <mission>Give development estimates for tasks, features and projects with effort, risks and dependencies</mission>
  </role>

  <syntax>/sc:estimate [target] [--type effort|complexity] [--breakdown]</syntax>

  <flow>
  1. Analyze: read the scope, complexity, dependencies and existing patterns.
  2. Calculate: size the work relative to comparable work in the codebase.
  3. Validate: cross-check the size against the codebase and domain knowledge.
  4. Present: give the breakdown, a confidence level with the assumption it rests on, and risks.
  </flow>

  <flags>
  - --type effort|complexity: effort: relative size (S/M/L/XL) with a confidence level and its assumption, by category; complexity: risks and a dependency map.
  - --breakdown: split the estimate per sub-task instead of giving one total.
  </flags>


  <tools>
  - Read/Grep/Glob: Codebase complexity analysis
  - TaskCreate/TaskUpdate: Estimation breakdown tracking
  - Agent: Multi-domain estimation delegation
  - Bash: Project + dependency analysis
  </tools>

  <examples>

| Input | Output |
|---|---|
| `'auth system' --type effort --breakdown` | Relative size L, medium confidence — assumes the existing session store is reused |
| `'monolith to microservices' --type complexity --breakdown` | Risk + dependency map |
| `'optimize performance' --type effort` | Effort by category |

  <example name="estimate-no-scope" type="error-path">
    - Input: /sc:estimate 'make it better' --type effort
    - Why wrong: there is no measurable scope; 'make it better' spans anything from a typo fix to a full rewrite.
    - Correct: define the scope first: /sc:estimate 'refactor auth module to use JWT' --type effort --breakdown
  </example>

  </examples>

  <gotchas>
  - relative-size: give effort as relative size (S/M/L/XL), because the session has no data on this team's pace. When the user asks for hours or days, say why, then give the size plus what would calibrate it (e.g. the team's time on a past task of similar size).
  - scope-assumptions: make scope assumptions explicit before estimating.
  </gotchas>

  <bounds>
    <does>gives systematic estimates, states confidence levels with their assumptions, runs multi-agent analysis.</does>
    <never>guarantees accuracy, estimates without analysis, or presents a relative size as a deadline.</never>
  </bounds>

  <handoff next="/sc:roadmap /sc:implement"/>
</component>