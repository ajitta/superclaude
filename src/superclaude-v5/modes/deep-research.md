---
name: deep-research
type: mode
priority: high
triggers: [research, investigate, deep-analysis, understand]
---

<document type="mode" name="deep-research">

# Deep Research Mode

## Activation Conditions
| Condition | Example |
|---|---|
| Deep analysis needed | Architecture understanding |
| Multi-source research | Library comparison |
| Evidence-based conclusion | Technology selection |
| Codebase exploration | Dependency analysis |

## Research Methodology

1. Define the problem -> precise question
2. Gather information -> MCP first, multi-source
3. Analyze -> extended thinking as needed
4. Verify -> cross-validation + confidence
5. Synthesize -> structured conclusion

## Tool Priority

| Purpose | Tool | Reason |
|---|---|---|
| Document lookup | Context7 MCP | Official docs |
| Web search | Tavily MCP | Current info |
| Code analysis | Serena MCP | Symbol tracking |
| Complex reasoning | Extended thinking | Multi-step analysis |

## Quality Control

| Item | Criteria |
|---|---|
| Confidence score | 0-1 scale explicit |
| Uncertainty | Label as "Needs verification" |
| Sources | Evidence required |
| Verification | Cross-validated |

## Output Format

```markdown
## Research Results

### Key Findings
| Finding | Confidence | Evidence |
|---|---|---|
| ... | 0.9 | [Source] |

### Analysis
[Extended thinking summary]

### Conclusion
[Verified conclusion]

### Further Investigation Needed
[Uncertain areas]
```

</document>
