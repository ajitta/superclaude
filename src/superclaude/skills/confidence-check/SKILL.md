---
name: confidence-check
description: Pre-implementation confidence assessment with 90% threshold to proceed.
when-to-use: >
  When user mentions 'confidence check', 'before implementing', 'validate first',
  'check before building', or wants validation before starting implementation work.
hooks:
  PreToolUse:
    - matcher: "WebFetch|WebSearch"
      hooks:
        - type: command
          command: "python3 {{SKILLS_PATH}}/confidence-check/scripts/validate_confidence_context.py"
          timeout: 30
          once: true
---
<component name="confidence-check" type="skill">

  <role>
    <mission>Prevent wrong-direction execution by assessing confidence BEFORE implementation</mission>
    <stats>Precision: 1.000 | Recall: 1.000 | 69/69 tests passed</stats>
  </role>

  <thresholds>
| Level | Score | Action |
|-------|-------|--------|
| High | ≥90% | Proceed with implementation |
| Medium | 70-89% | Present alternatives, investigate more |
| Low | <70% | STOP - Request clarification |
  </thresholds>

  <references note="Load on demand">
  - `references/checks-detail.md` — Detailed weights for all 5 checks, MCP integration, ROI figures
  </references>

  <gotchas>
  - websearch-dup: Do not duplicate Context7 results with WebSearch. Use WebSearch only when Context7 fails
  - score-rounding: Do not round 89% up to "almost 90%". 70-89% = Medium — must present alternatives
  - evidence-gap: When presenting scores, always cite the evidence source for each check
  </gotchas>

  <bounds will="pre-implementation validation|evidence-based assessment" wont="runtime checks|modify code"/>

  <checklist>
- [ ] All 5 checks evaluated (duplicates, architecture, docs, OSS, root cause)
- [ ] Score computed with correct weights (25/25/20/15/15)
- [ ] Recommendation matches threshold (≥90% proceed, 70-89% investigate, <70% stop)
- [ ] Evidence sources cited for each check
  </checklist>

  <handoff next="/sc:implement /sc:test /sc:analyze"/>
</component>
