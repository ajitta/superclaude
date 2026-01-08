---
name: confidence-check
description: Pre-implementation confidence assessment (≥90% to proceed)
triggers: /confidence-check, pre-implementation, verify-before-implementing, 확인해줘
mcp: c7:docs|tavily:oss-search

# v2.1.0 Compatibility Fields
context: inline                    # inline (default) | fork (sub-agent)
agent: quality-engineer            # Optional: agent type for execution
user-invocable: true               # true (default) | false (hide from slash menu)

allowed-tools:
  - Read
  - Grep
  - Glob
  - WebFetch
  - WebSearch
  - mcp__context7__*
  - mcp__tavily__*
  - mcp__serena__find_symbol
  - mcp__serena__search_for_pattern

hooks:
  PreToolUse:
    - type: command
      command: python {{SCRIPTS_PATH}}/validate_confidence_context.py
      matcher: WebFetch|WebSearch
      once: true
---
<component name="confidence-check" type="skill">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

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

  <usage note="See confidence.ts for interfaces">
```typescript
const checker = new ConfidenceChecker();
const result = await checker.assess(context);
if (result.score >= 0.9) { /* proceed */ }
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

  <bounds will="pre-implementation validation|evidence-based assessment" wont="runtime checks|modify code"/>
</component>
