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

  <bounds will="multi-step reasoning|systematic analysis|structured problem solving" wont="simple single-step tasks|basic explanations|straightforward fixes" fallback="Use native Claude reasoning for simple tasks"/>

  <handoff next="/sc:analyze /sc:troubleshoot /sc:research"/>
</component>
