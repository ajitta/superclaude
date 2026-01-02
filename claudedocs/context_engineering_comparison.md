# Context Engineering for Claude Code Opus 4.5: Comparison Guide

## Executive Summary

This document compares three context/prompt engineering approaches for Claude Code Opus 4.5:
1. **Native WebSearch/WebFetch** - Built-in, zero overhead
2. **Tavily MCP** - Deep research capabilities
3. **Codex MCP** - Code-focused context extension

**Key Finding**: These approaches are **complementary, not competing**. Optimal strategy uses the right tool for each task type.

## Quick Comparison Matrix

| Criterion | WebSearch (Native) | Tavily MCP | Codex MCP |
|-----------|-------------------|------------|-----------|
| **Token Overhead** | 0 | 2-5K | 0.5-1K |
| **Setup** | None | API key required | OpenAI access |
| **Context Window** | 200K (shared) | 200K (shared) | +400K (via MCP) |
| **Research Depth** | Single-hop | Multi-hop (5 levels) | N/A |
| **Code Generation** | Good | Good | Specialized |
| **Caching** | No | Yes (1h/24h) | No |
| **Latency** | Fast | Medium | Medium |
| **Cost** | Free | Tavily API ($) | OpenAI API ($) |

## Detailed Feature Comparison

### Context Window Management

| Aspect | WebSearch | Tavily | Codex |
|--------|-----------|--------|-------|
| Base context | 200K | 200K | 200K + 400K |
| System overhead | ~18K (9%) | ~20-23K | ~18.5-19K |
| Working context | ~137K | ~132-135K | ~137K + 400K |
| Compaction | Summarization | Summarization | Multi-window |
| Prompt caching | Yes (35% savings) | Yes | Yes |

### Research Capabilities

| Capability | WebSearch | Tavily | Codex |
|------------|-----------|--------|-------|
| Single URL fetch | Yes | Yes | N/A |
| Web search | Yes | Yes (advanced) | N/A |
| Multi-hop research | No | Yes (5 hops) | N/A |
| Domain filtering | Basic | Advanced | N/A |
| Time filtering | No | Yes | N/A |
| Credibility scoring | No | Yes (4 tiers) | N/A |
| Result caching | No | 1h search, 24h extract | N/A |

### Code Generation

| Capability | WebSearch | Tavily | Codex |
|------------|-----------|--------|-------|
| Code understanding | Claude native | Claude native | GPT-5.2 specialized |
| Algorithm optimization | Good | Good | Excellent |
| Language idioms | Good | Good | Excellent |
| Project awareness | Excellent | Excellent | Limited |
| Style compliance | Excellent | Excellent | Requires synthesis |

## Token Budget Analysis

### Per-Task Token Consumption

| Task Type | WebSearch | Tavily | Codex |
|-----------|-----------|--------|-------|
| Quick lookup | 500-1K | 3-5K | N/A |
| Standard research | 3-7K | 10-15K | N/A |
| Deep investigation | N/A | 20-30K | N/A |
| Code generation | Native | Native | 2-5K |
| Complex algorithm | Native | Native | 5-10K |

### ROI Calculation

| Scenario | Best Choice | Reason |
|----------|-------------|--------|
| <3 sources needed | WebSearch | Zero overhead |
| >3 sources needed | Tavily | Overhead justified |
| Algorithm-heavy | Codex | Specialized capability |
| Context overflow | Codex | +400K extension |
| Simple fact check | WebSearch | Fastest |

## Decision Framework

### When to Use Each Approach

```
START
  │
  ├─ Is this a code generation task?
  │   ├─ YES: Is it algorithm-heavy or context-constrained?
  │   │   ├─ YES → Use Codex MCP
  │   │   └─ NO → Use Claude native
  │   │
  │   └─ NO: Is this a research task?
  │       ├─ YES: How many sources needed?
  │       │   ├─ 1-2 sources → Use WebSearch/WebFetch
  │       │   ├─ 3+ sources → Use Tavily MCP
  │       │   └─ Deep investigation → Use Tavily + Sequential
  │       │
  │       └─ NO: Quick information lookup
  │           └─ Use WebSearch (native)
END
```

### Task-Based Recommendations

| Task | Primary Tool | Fallback |
|------|-------------|----------|
| Official docs lookup | WebFetch | Tavily extract |
| General fact check | WebSearch | Tavily search |
| Multi-source research | Tavily | WebSearch + manual |
| Competitive analysis | Tavily | N/A |
| Algorithm implementation | Codex MCP | Claude native |
| Code review | Claude native | Codex consultation |
| Context overflow | Codex MCP | /compact + continue |
| Debug investigation | Sequential + Tavily | Claude native |

## Integration Patterns

### Pattern 1: Layered Approach (Recommended)
```
Level 1 (Default): Native WebSearch/WebFetch
  ↓ If insufficient
Level 2 (Research): Tavily MCP
  ↓ If code-focused
Level 3 (Code): Codex MCP
```

### Pattern 2: Parallel Consultation
```
For critical decisions:
├─ Claude native analysis
├─ Tavily research (parallel)
└─ Codex code review (parallel)
    ↓
Synthesize all inputs
```

### Pattern 3: Specialized Pipelines
```
Research Pipeline:
Tavily:discover → Sequential:analyze → Tavily:followup → Serena:store

Code Pipeline:
Claude:plan → Codex:generate → Claude:integrate → Claude:test
```

## Configuration Recommendations

### Minimal Setup (Native Only)
```markdown
# CLAUDE.md
## Web Research
- Use WebFetch for official documentation
- Use WebSearch for general queries
- Summarize before applying
```

### Standard Setup (+ Tavily)
```json
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "@anthropic/tavily-mcp"],
      "env": { "TAVILY_API_KEY": "${TAVILY_API_KEY}" }
    }
  }
}
```

### Full Setup (All Three)
```json
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "@anthropic/tavily-mcp"],
      "env": { "TAVILY_API_KEY": "${TAVILY_API_KEY}" }
    },
    "codex": {
      "command": "codex",
      "args": ["mcp-server"]
    }
  }
}
```

## Performance Benchmarks

### Latency Comparison

| Operation | WebSearch | Tavily | Codex |
|-----------|-----------|--------|-------|
| Single search | ~1-2s | ~1-3s | N/A |
| URL extraction | ~2-5s | ~2-5s | N/A |
| Multi-hop (3) | N/A | ~5-10s | N/A |
| Code generation | Native | Native | ~3-8s |

### Quality Comparison

| Metric | WebSearch | Tavily | Codex |
|--------|-----------|--------|-------|
| Research accuracy | Good | Excellent | N/A |
| Source diversity | Limited | Excellent | N/A |
| Code quality | Good | Good | Excellent |
| Project alignment | Excellent | Excellent | Requires synthesis |

## Cost Analysis

### Monthly Estimates (Active Use)

| Approach | API Cost | Token Overhead | Total Impact |
|----------|----------|----------------|--------------|
| WebSearch only | $0 | 0 | Baseline |
| + Tavily | ~$20-50 | +2-5K/session | Low-Medium |
| + Codex | ~$30-100 | +0.5-1K/session | Medium |
| All three | ~$50-150 | +3-6K/session | Medium |

### ROI Justification

| Scenario | Without MCP | With MCP | Savings |
|----------|-------------|----------|---------|
| Deep research (10 sources) | 2-3 hours manual | 15-30 min | 80-90% time |
| Complex algorithm | 1-2 hours trial/error | 15-30 min | 75-85% time |
| Context overflow | Session restart | Continue seamlessly | Context preserved |

## Best Practices Summary

### 1. Start Minimal
```
Begin with native tools. Add MCP only when needed.
Token overhead compounds across sessions.
```

### 2. Match Tool to Task
```
Quick lookup → WebSearch
Deep research → Tavily
Code generation → Codex
Default → Claude native
```

### 3. Monitor Token Budget
```
Check /context regularly
Context >75% → consider /compact or /clear
Critical tasks → start fresh session
```

### 4. Leverage Caching
```
Tavily caches searches (1h) and extractions (24h)
Reuse research within session
Prompt caching for static context (35% savings)
```

### 5. Synthesize Cross-Tool Results
```
When using multiple tools:
- Validate consistency
- Resolve contradictions
- Integrate with project context
- Document sources
```

## Conclusion

### Recommended Default Configuration

For most users, the **Layered Approach** works best:

1. **Always available**: Native WebSearch/WebFetch (zero cost)
2. **Add when needed**: Tavily MCP for research-heavy projects
3. **Add for code**: Codex MCP for algorithm-intensive work

### Key Takeaways

| Principle | Implementation |
|-----------|----------------|
| Zero overhead by default | Use native tools first |
| Pay for capability | MCP only when justified |
| Complementary tools | Each serves different needs |
| Context is precious | Minimize tool definitions |
| Quality over speed | Right tool for right task |

### Files Reference

| Document | Focus |
|----------|-------|
| `context_engineering_websearch.md` | Native tools deep dive |
| `context_engineering_tavily.md` | Research workflows |
| `context_engineering_codex.md` | Code generation |
| `context_engineering_comparison.md` | This comparison guide |

---

*Generated for Claude Code Opus 4.5 context engineering optimization.*
