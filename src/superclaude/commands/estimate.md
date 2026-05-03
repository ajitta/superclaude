---
description: Provide development estimates for tasks, features, or projects with intelligent analysis
---
<component name="estimate" type="command">

  <role>
    /sc:estimate
    <mission>Provide development estimates for tasks, features, or projects with intelligent analysis</mission>
  </role>

  <syntax>/sc:estimate [target] [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]</syntax>

  <flow>
  1. Analyze: Scope, complexity, deps, patterns
  2. Calculate: Methodology + benchmarks
  3. Validate: Cross-reference + domain expertise
  4. Present: Breakdown + confidence + risk
  5. Track: Accuracy for improvement
  </flow>


  <tools>
  - Read/Grep/Glob: Codebase complexity analysis
  - TaskCreate/TaskUpdate: Estimation breakdown tracking
  - Task: Multi-domain estimation delegation
  - Bash: Project + dependency analysis
  </tools>

  <patterns>
    - Scope: Requirements → complexity → patterns → risk
    - Method: Time|Effort|Complexity|Cost approaches
    - Multi-Domain: Architecture + Performance + Timeline assessment
    - Validation: Benchmarks → cross-check → confidence
  </patterns>

  <examples>

| Input | Output |
|---|---|
| `'auth system' --type time --unit days --breakdown` | 8 days, 85% confidence |
| `'monolith to microservices' --type complexity --breakdown` | Risk + dependency map |
| `'optimize performance' --type effort --unit hours` | Effort by category |

  <example name="estimate-no-scope" type="error-path">
    - Input: /sc:estimate 'make it better' --type time
    - Why wrong: No measurable scope. 'make it better' could mean anything from a typo fix to a full rewrite.
    - Correct: Define scope first: /sc:estimate 'refactor auth module to use JWT' --type time --breakdown
  </example>

  </examples>

  <gotchas>
  - no-time-estimates: Never give time estimates in hours/days. Focus on complexity, dependencies, and risks
  - scope-assumptions: Make scope assumptions explicit before estimating
  </gotchas>

  <bounds>
    <should>systematic estimates, confidence intervals, and multi-agent analysis.</should>
    <avoid>guarantee accuracy, estimate without analysis, and override benchmarks.</avoid>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:workflow /sc:implement"/>
</component>
