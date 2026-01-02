# Context Engineering for Claude Code Opus 4.5: Tavily MCP Version

## Overview

This document covers advanced context/prompt engineering using Tavily MCP for deep research workflows with Claude Code Opus 4.5.

## Tavily MCP Capabilities

### Core Tools
| Tool | Function |
|------|----------|
| `tavily_search` | Web search with ranking, filtering |
| `tavily_extract` | Full-text extraction from URLs |
| `tavily_crawl` | Multi-page crawling (500 char/page) |
| `tavily_map` | Site structure discovery |

### Configuration
```json
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "@anthropic/tavily-mcp"],
      "env": {
        "TAVILY_API_KEY": "tvly-YOUR_KEY"
      }
    }
  }
}
```

## Token Overhead Analysis

| Component | Token Cost |
|-----------|-----------|
| Tool definitions | ~2-5K tokens |
| Search result (5 items) | ~1-2K tokens |
| Full extraction | ~3-10K tokens |
| Crawl results | Variable |

**Total MCP overhead**: 2-5K tokens upfront
**ROI**: Justified for complex research (>3 sources needed)

## Deep Research Prompt Patterns

### 1. Multi-Hop Research
```
Research [topic] using multi-hop strategy:

Hop 1: Discover key concepts and entities
Hop 2: Follow references to authoritative sources
Hop 3: Verify claims with independent sources
Hop 4: Identify gaps and contradictions
Hop 5: Synthesize into coherent findings

Track information genealogy throughout.
Confidence threshold: 0.7
```

### 2. Domain-Filtered Search
```
Search for [topic] with constraints:
- Include domains: arxiv.org, github.com, official docs
- Exclude domains: medium.com, stackoverflow.com
- Time range: past month
- Max results: 10

Rank by credibility tier:
- Tier 1 (0.9-1.0): Academic, Gov, Official docs
- Tier 2 (0.7-0.9): Industry, Expert blogs
- Tier 3 (0.5-0.7): Community, Wikipedia
```

### 3. Structured Extraction
```
Use tavily_extract on these URLs:
1. [url1] - Extract: API endpoints, auth methods
2. [url2] - Extract: Configuration options
3. [url3] - Extract: Migration steps

Format as comparison table with source citations.
```

### 4. Research Planning (Unified Strategy)
```
Before executing research:
1. Define clear objectives
2. Identify success criteria
3. Plan search strategy (parallel vs sequential)
4. Set confidence threshold (default: 0.7)
5. Allocate token budget

Present plan for approval before proceeding.
```

## Research Depth Profiles

| Profile | Sources | Hops | Time | Confidence |
|---------|---------|------|------|------------|
| Quick | 10 | 1 | 2m | 0.6 |
| Standard | 20 | 3 | 5m | 0.7 |
| Deep | 40 | 4 | 8m | 0.8 |
| Exhaustive | 50+ | 5 | 10m | 0.9 |

## Integration with Sequential MCP

Optimal workflow combining Tavily + Sequential:
```
1. Tavily: Broad discovery search
2. Sequential: Analyze and identify gaps
3. Tavily: Targeted follow-up searches
4. Sequential: Synthesize findings
5. Serena: Store session results (optional)
```

## SuperClaude /sc:research Integration

```bash
# Activate deep research mode
/sc:research "topic" --depth deep --confidence 0.8
```

Built-in features:
- Automatic parallel search batching
- Credibility scoring
- Gap identification
- Source tracking
- Memory persistence (with Serena)

## Context Engineering Strategies

### 1. Parallel Search Batching
```
Execute these searches in parallel:
- Search 1: [aspect A of topic]
- Search 2: [aspect B of topic]
- Search 3: [aspect C of topic]

Batch config: searches=5, group_by=domain
```

### 2. Selective Extraction
```
From search results, extract full content only from:
- Tier 1 credibility sources
- Sources with unique information
- Primary references (not aggregators)

Use tavily_extract for selected URLs only.
```

### 3. Iterative Refinement
```
Research iteration protocol:
1. Initial broad search
2. Assess confidence (target: 0.7)
3. If below threshold:
   - Identify specific gaps
   - Execute targeted searches
   - Re-assess confidence
4. Repeat until threshold met or max iterations (5)
```

## Credibility Assessment

| Tier | Score | Source Types |
|------|-------|--------------|
| 1 | 0.9-1.0 | Academic, Government, Official docs, Peer-reviewed |
| 2 | 0.7-0.9 | Established media, Industry, Expert blogs |
| 3 | 0.5-0.7 | Community, User docs, Wikipedia |
| 4 | 0.3-0.5 | Forums, Unverified social, Personal blogs |

## Error Handling

| Issue | Resolution |
|-------|------------|
| API key missing | Check TAVILY_API_KEY env var |
| Rate limit | Exponential backoff, batch requests |
| No results | Expand terms, remove filters |
| Timeout | Increase timeout or skip source |
| Low confidence | Add more sources, verify claims |

**Fallback chain**: Tavily → Native WebSearch → Alternative queries

## Caching Strategy

| Content Type | Cache Duration |
|--------------|----------------|
| Search results | 1 hour |
| Extractions | 24 hours |
| Patterns | Always |

## Token Budget for Research Tasks

| Task Complexity | Budget |
|-----------------|--------|
| Simple lookup | 3-5K |
| Standard research | 10-15K |
| Deep analysis | 20-30K |
| Exhaustive investigation | 40-50K |

## CLAUDE.md Configuration

```markdown
## Deep Research Configuration
- Default depth: standard
- Max hops: 5
- Confidence threshold: 0.7
- Memory: enabled
- Parallel: true (default)

## Tavily Integration
- Primary search tool for research tasks
- Use domain filtering for technical queries
- Cache results for session
```

## Performance Optimization

1. **Batch similar searches**: Group related queries
2. **Cache aggressively**: Reuse results within session
3. **Prioritize high-value sources**: Skip low-credibility early
4. **Limit extraction depth**: Full content only when needed
5. **Use crawl sparingly**: 500 char/page limit

## When to Use Tavily vs Native

| Scenario | Recommended |
|----------|-------------|
| Single URL lookup | Native WebFetch |
| Multi-source research | Tavily |
| Official docs only | Native WebFetch |
| Competitive analysis | Tavily |
| Quick fact check | Native WebSearch |
| Deep investigation | Tavily + Sequential |

## Summary

Tavily MCP provides:
- **Multi-hop research** - Follow reference chains
- **Structured extraction** - Ranked, filtered results
- **Deep workflows** - /sc:research integration
- **Caching** - 1h search, 24h extraction
- **Credibility scoring** - Source quality assessment

Best for: Complex research, multi-source synthesis, competitive analysis, deep investigation tasks.

**Token overhead**: 2-5K upfront, justified for tasks requiring >3 sources.
