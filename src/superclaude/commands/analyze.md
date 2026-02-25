---
description: Comprehensive code analysis across quality, security, performance, and architecture domains
---
<component name="analyze" type="command">

  <role>
    /sc:analyze
    <mission>Comprehensive code analysis across quality, security, performance, and architecture domains</mission>
  </role>

  <syntax>/sc:analyze [target] [--focus quality|security|performance|architecture] [--depth quick|deep] [--format text|json|report]</syntax>

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


  <mcp servers="seq|c7"/>
  <personas p="arch|perf|sec|qual"/>

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

  <example name="invalid-focus" type="error-path">
    <input>/sc:analyze --focus everything --scope system</input>
    <why_wrong>--focus accepts: perf|security|quality|arch|a11y|testing. 'everything' is not a valid domain.</why_wrong>
    <correct>/sc:analyze --scope system (omit --focus for multi-domain analysis)</correct>
  </example>

  </examples>

  <token_note>Medium-high consumption — use --scope file or --scope module to limit analysis boundary</token_note>

  <bounds will="static analysis|severity-rated findings|detailed reports" wont="dynamic/runtime analysis|modify code|analyze external deps" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Produce analysis report, then complete | Preserve source code unchanged | Report issues; defer fixes to /sc:improve or /sc:cleanup → Output: Analysis report with severity-rated findings</boundaries>


  <handoff next="/sc:improve /sc:cleanup /sc:implement"/>
</component>
