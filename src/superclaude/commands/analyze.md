---
description: Comprehensive code analysis across quality, security, performance, and architecture domains
---
<component name="analyze" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

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
    2. Scan: Domain-specific analysis per --focus
    3. Evaluate: Prioritized findings + severity (🔴🟡🟢)
    4. Recommend: Actionable guidance
    5. Report: Generate output per --format
  </flow>

  <outputs note="Per --format flag">
| Format | Output | Content |
|--------|--------|---------|
| text | console | Inline findings + recs |
| json | analysis.json | Structured findings |
| report | ANALYSIS_REPORT.md | Full report + roadmap |
  </outputs>

  <checklist note="SHOULD complete all">
    - [ ] All files in target scanned
    - [ ] Findings prioritized by severity
    - [ ] Actionable recommendations provided
    - [ ] Output format matches --format
  </checklist>

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

  <token_note>Medium-high consumption — use --scope file or --scope module to limit analysis boundary</token_note>

  <bounds will="static analysis|severity-rated findings|detailed reports" wont="dynamic/runtime analysis|modify code|analyze external deps"/>

  <boundaries type="document-only" critical="true">
    <rule>Produce analysis report, then complete</rule>
    <rule>Preserve source code unchanged</rule>
    <rule>Report issues; defer fixes to /sc:improve or /sc:cleanup</rule>
    <output>Analysis report with severity-rated findings</output>
  </boundaries>

  <handoff>
    <next command="/sc:improve">For quality improvements and refactoring</next>
    <next command="/sc:cleanup">For dead code removal and optimization</next>
    <next command="/sc:implement">For implementing missing features</next>
    <format>Include finding references for targeted fixes</format>
  </handoff>
</component>
