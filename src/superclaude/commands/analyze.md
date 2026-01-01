---
description: Comprehensive code analysis across quality, security, performance, and architecture domains
---
<component name="analyze" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:analyze
    <mission>Comprehensive code analysis across quality, security, performance, and architecture domains</mission>
  </role>

  <syntax>/sc:analyze [target] [--focus quality|security|performance|architecture] [--depth quick|deep] [--format text|json|report]</syntax>

  <triggers>
    - Code quality assessment
    - Security vulnerability scanning
    - Performance bottleneck identification
    - Architecture review + tech debt
  </triggers>

  <flow>
    1. Discover: Categorize files by language
    2. Scan: Domain-specific analysis
    3. Evaluate: Prioritized findings + severity
    4. Recommend: Actionable guidance
    5. Report: Metrics + roadmap
  </flow>

  <tools>
    - Glob: File discovery
    - Grep: Pattern analysis
    - Read: Source inspection
    - Bash: External tools
    - Write: Report generation
  </tools>

  <patterns>
    - Domain: Quality|Security|Perf|Arch → specialized assessment
    - Recognition: Language detect → appropriate techniques
    - Severity: Issue classification → prioritized recs
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `/sc:analyze` | Multi-domain project report |
| `src/auth --focus security --deep` | Vulnerability assessment |
| `--focus performance --format report` | Bottleneck analysis |
| `src/components --focus quality --quick` | Code smell detection |

  </examples>

  <bounds will="static analysis|severity-rated findings|detailed reports" wont="dynamic/runtime analysis|modify code|analyze external deps"/>
</component>
