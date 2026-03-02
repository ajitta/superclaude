<component name="sequential" type="mcp">
  <role>
    <mission>Multi-step reasoning engine for complex analysis and systematic problem solving</mission>
  </role>

  <choose>
Use:
- Complex problems: 3+ interconnected components
- Systematic analysis: Root cause, architecture review, security assessment
- Structured approach: Decomposition, evidence gathering
- Cross-domain: Frontend + backend + database + infrastructure

Avoid:
- Simple tasks: Basic explanations, single-file, straightforward fixes
  </choose>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| why is API slow | Sequential | systematic perf analysis |
| design microservices | Sequential | structured system design |
| debug auth flow | Sequential | multi-component investigation |
| security vulnerabilities | Sequential | comprehensive threat modeling |
| explain this function | Native Claude | simple explanation |
  </examples>

  <workflows>
    <debugging_with_revision>
1. State symptoms and reproduction steps
2. Hypothesize root causes (rank by likelihood)
3. Gather evidence — read logs, trace code paths
4. Revise hypotheses based on evidence (isRevision=true)
5. Verify fix against original symptoms
    </debugging_with_revision>
    <architecture_decision>
1. Define requirements and constraints
2. Enumerate candidate approaches (min 3)
3. Evaluate trade-offs (latency, complexity, cost)
4. Branch into alternative if primary has blockers (branchFromThought)
5. Synthesize recommendation with rationale
    </architecture_decision>
  </workflows>

  <scenarios>
    <security_analysis>
Scenario: audit authentication and authorization flow
1. Map trust boundaries: client, API gateway, service, database
2. Enumerate attack vectors per boundary (OWASP Top 10)
3. Trace token lifecycle: issuance, validation, refresh, revocation
4. Identify gaps: rate limits, token storage, privilege escalation
5. Prioritize by impact; recommend mitigations with effort estimate
    </security_analysis>
  </scenarios>

  <tool_guide>
- totalThoughts: start with estimate, adjust via needsMoreThoughts
- isRevision: when new evidence invalidates earlier reasoning
- branchFromThought: explore alternatives without losing main thread
- Combine with --c7 for evidence-backed architecture decisions
- Combine with --devtools for systematic performance root cause analysis
  </tool_guide>
</component>
