---
name: confidence-check
description: Pre-implementation confidence assessment (≥90% to proceed)
metadata:
  context: inline
  agent: quality-engineer
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
    <stats>Precision: 1.000 | Recall: 1.000 | 63/63 tests passed</stats>
  </role>

  <thresholds>
| Level | Score | Action |
|-------|-------|--------|
| High | ≥90% | Proceed with implementation |
| Medium | 70-89% | Present alternatives, investigate more |
| Low | <70% | STOP - Request clarification |
  </thresholds>

  <checks>
| Check | Weight | Tools | Validates |
|-------|--------|-------|-----------|
| No Duplicates | 25% | Grep, Glob, Serena | No existing similar functionality |
| Architecture | 25% | CLAUDE.md, pyproject.toml | Uses existing tech stack |
| Official Docs | 20% | Context7, WebFetch | Documentation reviewed |
| OSS Reference | 15% | Tavily, WebSearch | Working implementations found |
| Root Cause | 15% | Investigation | Problem source identified |
  </checks>

  <mcp_integration>
| MCP | Role | Fallback |
|-----|------|----------|
| Context7 | Official docs (Check 3) | WebFetch |
| Tavily | OSS search (Check 4) | WebSearch |
| Serena | Symbol detection (Check 1) | Grep/Glob |
  </mcp_integration>

  <usage note="See confidence.py for interfaces">
```python
checker = ConfidenceChecker()
result = checker.assess(context)
if result >= 0.9:  # proceed
    pass
```
  </usage>

  <pytest note="See confidence.py for full API">
```python
@pytest.mark.confidence_check
def test_feature(confidence_checker):
    result = confidence_checker.assess(context)
    assert result >= 0.9
```
  </pytest>

  <roi>100-200 tokens check → saves 5,000-50,000 tokens (25-250x ROI)</roi>

  <hooks note="validate_confidence_context.py runs on PreToolUse for WebFetch/WebSearch — injects evidence-focus guidance (once per session)"/>

  <bounds will="pre-implementation validation|evidence-based assessment" wont="runtime checks|modify code"/>

  <checklist>
- [ ] All 5 checks evaluated (duplicates, architecture, docs, OSS, root cause)
- [ ] Score computed with correct weights (25/25/20/15/15)
- [ ] Recommendation matches threshold (≥90% proceed, 70-89% investigate, <70% stop)
- [ ] Evidence sources cited for each check
  </checklist>

  <handoff next="/sc:implement /sc:test /sc:analyze"/>
</component>
