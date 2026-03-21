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
    6. Bridge: If findings are actionable (fixable issues, not just informational), suggest: "Would you like to create an implementation plan? → /sc:plan"
  </flow>

  <outputs note="Per --format flag">
  | Format | Output | Content |
  |--------|--------|---------|
  | `text` (default) | Console inline | Findings + recommendations inline |
  | `json` | `docs/analysis/YYYY-MM-DD-<target>-analysis-<username>.json` | Structured findings as JSON |
  | `report` | `docs/analysis/YYYY-MM-DD-<target>-analysis-<username>.md` | Full report with roadmap |
  </outputs>


  <mcp servers="seq|c7"/>
  <personas p="arch|perf|sec|qual"/>

  <tools>
    - Glob: File discovery
    - Grep: Pattern analysis
    - Read: Source inspection
    - Bash: External tools
    - Write: Report generation (--format json|report)
  </tools>

  <patterns>
    - Domain: Quality|Security|Perf|Arch → specialized assessment
    - Recognition: Language detect → appropriate techniques
    - Severity: Issue classification → prioritized recs
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `/sc:analyze` | Multi-domain findings inline |
| `src/auth --focus security --deep` | Security vulnerability assessment |
| `--focus performance --format report` | ANALYSIS_REPORT.md with bottleneck roadmap |
| `src/components --focus quality --format json` | analysis.json with code smell findings |

  <example name="invalid-focus" type="error-path">
    <input>/sc:analyze --focus everything --scope system</input>
    <why_wrong>--focus accepts: quality|security|performance|architecture. 'everything' is not valid.</why_wrong>
    <correct>/sc:analyze --scope system (omit --focus for multi-domain analysis)</correct>
  </example>

  </examples>

  <token_note>Medium-high consumption — use --scope file or --scope module to limit analysis boundary</token_note>

  <bounds will="static analysis|severity-rated findings|detailed reports" wont="dynamic/runtime analysis|modify code|analyze external deps" fallback="Ask user for guidance when uncertain" type="document-only">
    Produce analysis report, then complete | Preserve source code unchanged | Report issues; defer fixes to /sc:improve or /sc:cleanup
  </bounds>


  <handoff next="/sc:plan /sc:improve /sc:cleanup /sc:implement"/>
</component>
