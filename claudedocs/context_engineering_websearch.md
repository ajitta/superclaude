# Context Engineering for Claude Code Opus 4.5: Native WebSearch Version

## Overview

This document covers context/prompt engineering strategies using Claude Code's built-in web capabilities (WebSearch and WebFetch) without external MCP servers.

## Native Web Tools

### WebSearch
- **Token Cost**: Built-in, minimal overhead
- **Capability**: Web search with domain filtering
- **Security**: Results are summarized (reduces prompt injection risk)

### WebFetch
- **Token Cost**: ~265 tokens tool definition
- **Capability**: Fetch and parse single web page content
- **Format**: Returns clean markdown
- **Limitation**: Cannot access some sites (Reddit, paywalled content)

## Optimal Prompt Patterns

### 1. Direct Information Lookup
```
Search for [specific topic] and provide the key findings.
Focus on official documentation and authoritative sources.
```

### 2. Documentation Verification
```
Use WebFetch to retrieve the official [framework] documentation at [URL].
Extract the relevant configuration options for [feature].
```

### 3. Fact-Checking Pattern
```
Verify this claim using WebSearch: "[claim]"
Prioritize sources from: [domain1], [domain2]
```

## Context Window Management

### Opus 4.5 Specifications
| Parameter | Value |
|-----------|-------|
| Total Context | 200K tokens |
| System Prompt Overhead | ~18K tokens (~9%) |
| Reserved for Compaction | 45K tokens |
| Usable Working Context | ~137K tokens |

### Efficiency Strategies

1. **Start Fresh Over Compact**
   - Claude 4.5 excels at discovering state from filesystem
   - New context windows often outperform compacted ones
   - Use `/clear` between unrelated tasks

2. **Prompt Caching**
   - 200K context with prompt caching available
   - Cache entire codebases, reference by line numbers
   - 35% token savings on subsequent tasks
   - Trade-off: 2-minute initial load vs 30% sustained savings

3. **Minimal Tool Overhead**
   - Native tools have fixed, optimized definitions
   - No MCP server startup or connection overhead
   - Predictable token consumption

## Use Case Matrix

| Task | Recommended Approach |
|------|---------------------|
| Quick fact lookup | WebSearch |
| Official docs extraction | WebFetch |
| API reference check | WebFetch to official URL |
| General research | WebSearch with domain filter |
| Dynamic page content | Not supported (use Tavily/Playwright) |

## Prompt Engineering Best Practices

### 1. Normal Language Over Intensity
```
# Good
Use WebFetch to read the React hooks documentation.

# Avoid
CRITICAL: You MUST use WebFetch to read the React hooks documentation.
```
Opus 4.5 is more responsive to system prompts; intensity causes over-triggering.

### 2. Parallel Tool Calling
Claude 4.5 aggressively parallelizes. Structure prompts to enable:
```
Search for:
1. [topic A] focusing on [domain1]
2. [topic B] focusing on [domain2]
3. [topic C] from official sources

Synthesize findings into a unified summary.
```

### 3. Context-Aware Extraction
```
Fetch [URL] and extract:
- Configuration options
- Default values
- Required vs optional parameters
Return as structured table.
```

## Limitations

1. **Single-Hop Only**: No follow-up research chains
2. **Site Restrictions**: Some sites block automated access
3. **No Caching**: Each fetch consumes fresh tokens
4. **No Memory**: Results not persisted across sessions
5. **Static Content Only**: Cannot handle JavaScript-rendered pages

## Fallback Strategies

When WebFetch fails:
1. Try alternative official documentation URLs
2. Use WebSearch to find cached/mirror versions
3. Ask user to provide content directly
4. Suggest Gemini CLI fallback (via tmux skill)

## Integration with CLAUDE.md

```markdown
## Web Research Guidelines
- Prefer official documentation over blog posts
- Use WebFetch for specific URLs, WebSearch for discovery
- Summarize findings before applying to code
- Verify version compatibility with project dependencies
```

## Token Budget Allocation

| Phase | Token Budget |
|-------|-------------|
| Initial search | 500-1000 |
| Content extraction | 2000-5000 |
| Synthesis | 500-1000 |
| Total per research task | 3000-7000 |

## When to Upgrade to Tavily MCP

Consider Tavily when you need:
- Multi-hop research (following references)
- Structured extraction with ranking
- Domain/time filtering
- Research caching
- Higher volume searches
- Complex synthesis workflows

## Summary

Native WebSearch/WebFetch provides:
- **Zero MCP overhead** - No additional tool definitions
- **Simplicity** - Built-in, always available
- **Security** - Summarized results reduce injection risk
- **Speed** - No server startup latency

Best for: Quick lookups, official documentation, fact verification, simple research tasks.
