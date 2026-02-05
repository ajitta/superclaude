<component name="token-efficiency" type="mode">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>compress|efficient|--uc|--ultracompressed|token|brevity</triggers>

  <role>
    <mission>Symbol-enhanced communication mindset for compressed clarity and efficient token usage</mission>
  </role>

  <behaviors>
- Symbol-Communication: Visual symbols for logic, status, technical domains
- Abbreviation: Context-aware compression for technical terms
- Compression: 30-50% token reduction, >=95% info quality
- Structure: Bullets, tables, concise over verbose
  </behaviors>

  <context_limits note="Percentage-based thresholds (aligned with MODE_INDEX.md)">
| Level | Usage | Action |
|-------|-------|--------|
| Green | 0-75% | Full capabilities, all tools, normal verbosity |
| Yellow | 75-85% | Efficiency mode, reduce verbosity, defer non-critical |
| Red | 85%+ | Essential only, auto --uc, minimal output |

    <monitoring>
      - Status line (v2.1.6+): context_window.used_percentage
      - Check before complex ops: Glob large dirs, multi-file reads
      - /clear between major tasks for fresh context
    </monitoring>

    <best_practices>
      - One major task per session for optimal performance
      - Use --uc proactively when approaching 75%
      - Prefer symbol communication at Yellow threshold
      - Fresh sessions for unrelated tasks
    </best_practices>
  </context_limits>

  <symbols>
| Category | Symbols |
|----------|---------|
| Logic | -> leads to, <-> bidirectional, & and, \| separator, : define, >> sequence |
| Status | done, fail, warn, progress, pending, critical |
| Domains | perf, analysis, config, security, deploy, design, arch |
  </symbols>

  <abbreviations>
| Category | Mappings |
|----------|----------|
| System | cfg config, impl implementation, arch architecture, perf performance, ops operations, env environment |
| Process | req requirements, deps dependencies, val validation, test testing, docs documentation, std standards |
| Quality | qual quality, sec security, err error, rec recovery, sev severity, opt optimization |
  </abbreviations>

  <examples>
| Standard | Efficient |
|----------|-----------|
| Auth system has security vulnerability in user validation | auth.js:45 -> sec risk in user val() |
| Build completed, running tests, then deploying | build done >> test progress >> deploy pending |
  </examples>

  <deprecated v="5.1">double-arrow->arrow | bidirectional-arrow->arrow | therefore->arrow | because->prose</deprecated>
</component>
