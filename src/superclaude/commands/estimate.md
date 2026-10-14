---
description: Give development estimates for tasks, features or projects — effort, risks, dependencies. Use when asked for a structured estimate of a feature, PRD or multi-task project. Not for a quick "is this hard?" — answer in one line.
---
<component name="estimate" type="command">

  <role command="/sc:estimate">
    <mission>Give dev estimates for tasks/features/projects with smart analysis</mission>
  </role>

  <syntax>/sc:estimate [target] [--type effort|complexity] [--breakdown]</syntax>

  <flow>
  1. Analyze: Scope, complexity, deps, patterns
  2. Calculate: Methodology + benchmarks
  3. Validate: Cross-reference + domain expertise
  4. Present: Breakdown + confidence + risk
  </flow>

  <flags>
  - --type effort|complexity: effort: relative size with a confidence level, by category; complexity: risks and a dependency map.
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
| `'auth system' --type effort --breakdown` | Relative effort L, 85% confidence |
| `'monolith to microservices' --type complexity --breakdown` | Risk + dependency map |
| `'optimize performance' --type effort` | Effort by category |

  <example name="estimate-no-scope" type="error-path">
    - Input: /sc:estimate 'make it better' --type effort
    - Why wrong: No measurable scope. 'make it better' span typo fix to full rewrite.
    - Correct: Define scope first: /sc:estimate 'refactor auth module to use JWT' --type effort --breakdown
  </example>

  </examples>

  <gotchas>
  - no-time-estimates: Never give time estimates in hours/days. Focus complexity, deps, risks
  - scope-assumptions: Make scope assumptions explicit before estimate
  </gotchas>

  <bounds>
    <does>systematic estimates, confidence intervals, multi-agent analysis.</does>
    <never>guarantee accuracy, estimate without analysis, override benchmarks.</never>
  </bounds>

  <handoff next="/sc:roadmap /sc:implement"/>
</component>