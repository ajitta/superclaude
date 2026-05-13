---
description: Task reflect + validate use Serena MCP analysis. Use when user type `/sc:reflect` or ask validate multi-step task truly done (assumptions surface, residuals list, gaps name). NO auto-trigger after every task close — routine end-turn summary go inline, not reflection pass.
---
<component name="reflect" type="command">

  <role command="/sc:reflect">
    <mission>Task reflect + validate use analysis power</mission>
    <note>For evidence-based done-check, use /sc:test with verify workflow</note>
  </role>

  <syntax>/sc:reflect [--type task|session|completion] [--analyze] [--validate]</syntax>

  <flow>
  1. Analyze: judge completeness of info gathered
  2. Validate: check goal align + drift
    2.5. Misunderstanding-Audit: spot moments user intent misread this session. Each: what trigger misread, what actual intent, what rule stop it. Save feedback memory if not stored yet.
  3. Reflect: weigh done-criteria
    3.5. Gotchas-Gardening: if `.claude/rules/gotchas/` exist, check: (a) files with `# Last reviewed:` older 90 days → warn, (b) `paths:` glob match zero files in project → warn stale pattern, (c) gotcha entries cite identifiers not in codebase → warn maybe stale.
  4. Persist: write learnings for cross-session catch
  </flow>


  <patterns>
    - Task: approach → goal align → drift → fix
    - Session: info gather → completeness → quality → insight
    - Completion: progress → criteria → work left → decide
    - Gotchas: stale check → paths: validate → content relevance → prune advice
  </patterns>

  <examples>
  | Input | Output |
  |---|---|
  | `--type task --analyze` | Goal align validate |
  | `--type session --validate` | Session work quality check |
  | `--type completion` | Done-ready judge |
  </examples>


  <gotchas>
  - evidence-required: cite real test output + file state, not predict result
  - baseline-compare: compare now-state vs baseline metric (test count, pass rate)
  </gotchas>

  <bounds>
    <does>full reflect, cross-session learn, qualitative rule-effect analysis (misread audit + improvement story).</does>
    <never>override done, bypass integrity, quantitative rule stats (delegate to /sc:analyze --focus rules).</never>
    <fallback>No Serena: use Claude auto memory for session persist.</fallback>
  </bounds>

  <handoff next="/sc:improve /sc:troubleshoot"/>
</component>