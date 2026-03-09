<component name="token-efficiency" type="mode">
  <role>
    <mission>Symbol-enhanced communication mindset for compressed clarity and efficient token usage</mission>
  </role>

  <behaviors>
- Symbol-Communication: Visual symbols for logic, status, technical domains
- Abbreviation: Context-aware compression for technical terms
- Compression: 30-50% token reduction, >=95% info quality
- Structure: Bullets, tables, concise over verbose
  </behaviors>

  <context_limits note="Thresholds in FLAGS.md; this section covers mode-specific behaviors">
    <monitoring>
      - Status line (v2.1.6+): context_window.used_percentage
      - Check before complex ops: Glob large dirs, multi-file reads
      - Opus 4.6 uses 25-50% more tokens — trigger efficiency earlier
    </monitoring>
    <best_practices>
      - One major task per session for optimal performance
      - Use --uc proactively when approaching 60% (was 75%, lowered for Opus 4.6)
      - Prefer symbol communication at Yellow threshold
      - Fresh sessions for unrelated tasks
      - Routine tasks use default effort; use ultrathink only when deep reasoning needed
      - Minimize subagent spawning — solve in single session when possible
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

  <compaction note="Long-session context management">
    <when>Context >60% used, answer quality degrading, or explicit --uc flag</when>
    <preserve>Architecture decisions, unresolved issues, implementation details, active file paths</preserve>
    <discard>Completed tool outputs, resolved intermediate results, stale error messages, duplicate information</discard>
    <tuning_order>
      1. Recall: capture all relevant information first
      2. Precision: remove unnecessary content iteratively
      3. Validate: test on complex agent traces, not simple conversations
    </tuning_order>
    <safest_action>Clear old tool call results — agent rarely needs raw results from earlier turns</safest_action>
  </compaction>

  <bounds will="symbol communication|30-50% token reduction|compressed clarity" wont="sacrifice info quality|lose critical context|compress beyond readability" fallback="Revert to default behavior when inapplicable"/>
</component>
