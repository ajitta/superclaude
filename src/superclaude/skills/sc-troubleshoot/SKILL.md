---
name: sc-troubleshoot
description: >-
  This skill should be used when the user asks to
  "debug this error",
  "troubleshoot a build failure",
  "diagnose performance issues",
  "fix deployment problems",
  "investigate root cause",
  "trace the bug",
  "why is this failing",
  "analyze error logs",
  "resolve this issue".
version: 1.0.0
metadata:
  context: inline
  agent: root-cause-analyst
  mcp: seq
  allowed-tools:
    - Read
    - Bash
    - Grep
    - Write
---
<component name="sc-troubleshoot" type="skill">

  <role>
    <mission>Diagnose and resolve issues in code, builds, deployments, and system behavior</mission>
  </role>

  <syntax>/sc:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]</syntax>

  <flow>
    1. Analyze: Gather issue description, examine system state (logs, error messages, stack traces)
    2. Hypothesize: Form up to 3 hypotheses based on evidence, rank by likelihood
    3. Test: Systematically validate each hypothesis (max 3 hypothesis-test cycles)
    4. Escalate: If no root cause after 3 cycles → summarize findings, present evidence, ask user for guidance
    5. Propose: Present solution with impact assessment, confidence level, and rollback plan
    6. Resolve: Apply fix (if --fix), verify effectiveness, document findings
  </flow>

  <hypothesis_limit note="3-cycle maximum">
    - Cycle 1: Most likely hypothesis → test → confirm/reject
    - Cycle 2: Second hypothesis → test → confirm/reject
    - Cycle 3: Third hypothesis → test → confirm/reject
    - If all 3 fail: ESCALATE — do not continue guessing. Present all evidence and ask user.
    This prevents infinite debugging loops and wasted context.
  </hypothesis_limit>

  <patterns>
    - Bug: Error message → stack trace analysis → code inspection → fix validation
    - Build: Build log analysis → dependency check → config validation → environment verification
    - Performance: Metrics collection → bottleneck identification → profiling → optimization recommendations
    - Deployment: Environment comparison → config verification → service health checks → rollback guidance
  </patterns>

  <auto_fix_threshold>
    <safe>Typos, missing imports, simple config errors, obvious null checks</safe>
    <approval_required>Schema changes, dependency updates, architecture modifications, production config</approval_required>
  </auto_fix_threshold>

  <examples>
| Input | Output |
|-------|--------|
| `'Null pointer in user service' --type bug --trace` | Root cause analysis + targeted fix |
| `'TypeScript compilation errors' --type build --fix` | Auto-apply safe fixes |
| `'API response times degraded' --type performance` | Bottleneck identification + optimization plan |
| `'Service not starting' --type deployment --trace` | Environment analysis + resolution |
| (auto-trigger) "why is this test failing" | Skill activates, runs Bug pattern |
| (auto-trigger) "debug this error" | Skill activates, examines stack trace |

  <example name="symptom-only-fix" type="error-path">
    <input>/sc:troubleshoot 'users report slow page' --fix (applies caching without profiling)</input>
    <why_wrong>Fixing symptoms without diagnosis. Slow page could be N+1 queries, not a caching issue.</why_wrong>
    <correct>/sc:troubleshoot 'users report slow page' --trace first → identify bottleneck → then targeted fix</correct>
  </example>
  </examples>

  <bounds will="systematic diagnosis|validated solutions|safe fixes|3-cycle hypothesis discipline" wont="risky fixes without confirm|modify production without permission|arch changes without impact assessment|guess beyond 3 cycles" fallback="Escalate to user after 3 hypothesis cycles with evidence summary"/>

  <handoff next="/sc:improve /sc:implement"/>
</component>
