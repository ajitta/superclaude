---
name: token-efficiency
type: mode
cache: pinned
triggers: [compress, efficient, --uc, --ultracompressed, token, brevity]
---
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

  <context_limits note="Claude Code practical thresholds">
| Threshold | Tokens | Action |
|-----------|--------|--------|
| Usable | ~176K | Full capabilities, normal operation |
| Degradation | >200K | Model performance drops noticeably |
| Warning | 75% | Trigger --token-efficient mode |
| Critical | 85% | Trigger --safe-mode, auto --uc |
| Maximum | 200K | Hard limit, context window full |

Best practices:
- Monitor usage before complex operations
- Use /clear between unrelated tasks
- Fresh sessions prevent context drift
- One major task per session recommended
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
| Authentication system has security vulnerability in user validation | auth.js:45 -> sec risk in user val() |
| Build completed, running tests, then deploying | build done >> test progress >> deploy pending |
| Performance analysis shows slow due to O(n^2) | perf: slow -> O(n^2) |
  </examples>

  <deprecated v="5.1">double-arrow->arrow | left-right-prose | bidirectional-arrow->arrow | therefore->arrow | because->prose</deprecated>
</component>
