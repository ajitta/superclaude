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

  <mcp servers="seq|c7"/>
  <personas p="arch|perf|pm"/>

  <tools>
    - Read/Grep/Glob: Codebase complexity analysis
    - TaskCreate/TaskUpdate: Estimation breakdown tracking
    - Task: Multi-domain estimation delegation
    - Bash: Project + dependency analysis
  </tools>

  <patterns>
    - Scope: Requirements → complexity → patterns → risk
    - Method: Time|Effort|Complexity|Cost approaches
    - Multi-Domain: Arch + Perf + Timeline assessment
    - Validation: Benchmarks → cross-check → confidence
  </patterns>


  <examples>

| Input | Output |
|-------|--------|
| `'auth system' --type time --unit days --breakdown` | 8 days, 85% confidence |
| `'monolith to microservices' --type complexity --breakdown` | Risk + dependency map |
| `'optimize performance' --type effort --unit hours` | Effort by category |

  <example name="estimate-no-scope" type="error-path">
    <input>/sc:estimate 'make it better' --type time</input>
    <why_wrong>No measurable scope. 'make it better' could mean anything from a typo fix to a full rewrite.</why_wrong>
    <correct>Define scope first: /sc:estimate 'refactor auth module to use JWT' --type time --breakdown</correct>
  </example>

  </examples>

  <bounds will="systematic estimates|confidence intervals|multi-persona analysis" wont="guarantee accuracy|estimate without analysis|override benchmarks" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Produce estimation report, then complete | Defer implementation to /sc:implement or /sc:workflow | Limit task tracking to estimation scope → Output: Estimation report with breakdown and confidence intervals</boundaries>


  <handoff next="/sc:workflow /sc:implement"/>
</component>
