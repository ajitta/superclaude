<component name="sequential" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>--effort medium|--effort high|--effort max|debug|architecture|analysis|reasoning|sequential</triggers>

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

  <synergy>
- Context7: Sequential coordinates → Context7 provides patterns
- Magic: Sequential analyzes UI logic → Magic implements
- Playwright: Sequential identifies test strategy → Playwright executes
  </synergy>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| why is API slow | Sequential | systematic perf analysis |
| design microservices | Sequential | structured system design |
| debug auth flow | Sequential | multi-component investigation |
| security vulnerabilities | Sequential | comprehensive threat modeling |
| explain this function | Native Claude | simple explanation |
  </examples>

  <bounds will="multi-step reasoning|systematic analysis|complex problem decomposition" wont="simple tasks|single-file fixes|basic explanations" fallback="Fall back to native tools when unavailable"/>
</component>
