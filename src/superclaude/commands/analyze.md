---
description: Code analysis across quality, security, performance, architecture domains. Use when user types `/sc:analyze`, asks "audit", "review codebase for X", or names multiple analysis dimensions one request. Do NOT auto-trigger on reading single file, looking up symbol, or "what does this function do" — those direct reads, not multi-domain analysis.
---
<component name="analyze" type="command">

  <role command="/sc:analyze">
    <mission>Code analysis across quality, security, performance, architecture domains</mission>
  </role>

  <syntax>/sc:analyze [target] [--focus quality|security|performance|architecture|rules] [--depth quick|deep] [--format text|json|report]</syntax>

  <flow>
  1. Discover: Categorize files by language
  2. Scan: Domain-specific analysis per --focus
  3. Evaluate: Prioritized findings + severity (🔴🟡🟢)
  4. Recommend: Actionable guidance
  5. Report (routing per RULES.md `<doc_output_convention>` for `--format report` markdown only): on feature path, write report to `docs/features/<slug>/03-analysis.md` (frontmatter: `status: draft, revised: <today>`) AND update `docs/features/<slug>/README.md` (`updated:` bump + append entry to `## Documents`, advance `phase:` if status enum moved). On standalone path, write to `docs/analysis/<target>-<username>-YYYY-MM-DD.md` — no README update needed. text/json formats unchanged (text = console, json = standalone path only).
  6. Bridge: If findings actionable (fixable issues, not informational), suggest: "Would you like to create an implementation plan? → /sc:plan"
  </flow>

  <outputs note="Per --format flag; report format dual-routes per RULES.md `<doc_output_convention>`">
Routing (`--format report` only): per RULES.md `<doc_output_convention>` — feature path `docs/features/<slug>/03-analysis.md` (existing folder OR user picks `[f]`) | standalone path `docs/analysis/<target>-<username>-YYYY-MM-DD.md` (user picks `[s]` or no related work expected, default for one-off analysis). Slug resolution: exact-match silent / multi partial-match prompt / zero match → `[f]/[s]` w/ default `[s]`. text/json unaffected.

  | Format | Output | Content |
  |---|---|---|
  | `text` (default) | Console inline | Findings + recommendations inline |
  | `json` | `docs/analysis/<target>-<username>-YYYY-MM-DD.json` | Structured findings as JSON (standalone path only) |
  | `report` (feature path) | `docs/features/<slug>/03-analysis.md` | Full report with roadmap, when slug resolves to existing/new feature folder |
  | `report` (standalone path) | `docs/analysis/<target>-<username>-YYYY-MM-DD.md` | Full report, one-off analysis |
  </outputs>



  <tools>
  - Glob: File discovery
  - Grep: Pattern analysis
  - Read: Source inspection
  - Bash: External tools
  - Write: Report generation (--format json|report)
  </tools>

  <focus_agent_mapping>
  When --focus specified and task benefits from specialist depth, delegate to corresponding agent:
  security → @security-engineer | performance → @performance-engineer | quality → @quality-engineer | architecture → @system-architect | a11y → @frontend-architect
  </focus_agent_mapping>

  <rules_analysis note="--focus rules: rule effectiveness audit">
    Quality (always): Read RULES.md → summary: rule count, example coverage, severity distribution
    Compliance (when data exists): Glob auto memory + list Serena memories → grep `violated_rule: "[RXX]"` → heatmap
      Hot (≥2 violations) 🔴: needs examples or clarification → /sc:improve
      Warm (1 violation) 🟡: monitor
      Untagged: corrections without violated_rule field → suggest [R14 Correction Capture] format
    Maturity label: Stage 1 (rules defined) | Stage 2 (rules + examples) | Stage 3 (rules + tracking) | Stage 4 (rules + iteration)
    Empty data: report "Stage N" + guide: "To bootstrap tracking, follow [R14 Correction Capture] Correction Capture format when correcting Claude's behavior"
  </rules_analysis>

  <patterns>
    - Domain: Quality|Security|Performance|Architecture|Rules → specialized assessment
    - Recognition: Language detect → appropriate techniques
    - Severity: Issue classification → prioritized recs
  </patterns>

  <examples>

| Input | Output |
|---|---|
| `/sc:analyze` | Multi-domain findings inline |
| `src/auth --focus security --depth deep` | Security vulnerability assessment |
| `--focus performance --format report` | `docs/analysis/<target>-<user>-YYYY-MM-DD.md` with bottleneck roadmap |
| `src/components --focus quality --format json` | `docs/analysis/<target>-<user>-YYYY-MM-DD.json` with code smell findings |
| `--focus rules` | Rule heatmap + maturity label + recommendations |

  <example name="invalid-focus" type="error-path">
    - Input: /sc:analyze --focus everything --scope system
    - Why wrong: --focus accepts: quality|security|performance|architecture|rules. 'everything' not valid.
    - Correct: /sc:analyze --scope system (omit --focus for multi-domain analysis)
  </example>

  </examples>

  <gotchas>
  - evidence-fabrication: Do not construct hypothetical failure scenarios to justify pre-existing recommendation. Evidence (code, config, measurements) must precede proposals.
  - seq-loop: If sequential thinking reaches same conclusion twice on same question, terminate that analysis branch, move to next topic.
  </gotchas>

  <bounds>
    <does>static analysis, severity-rated findings, detailed reports, quantitative rules audit (counts, frequencies, heatmaps via --focus rules).</does>
    <never>dynamic/runtime analysis, modify code, analyze external deps, qualitative rule-effectiveness narrative (delegate to /sc:reflect).</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>


  <handoff next="/sc:plan /sc:improve /sc:cleanup /sc:implement"/>
</component>