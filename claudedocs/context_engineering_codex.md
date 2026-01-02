# Context Engineering for Claude Code Opus 4.5: Codex MCP Version

## Overview

This document covers context/prompt engineering strategies using OpenAI Codex MCP integration with Claude Code Opus 4.5 for code-focused context augmentation.

## Codex MCP Architecture

### Running Codex as MCP Server
```bash
# Start Codex as MCP server
codex mcp-server

# With MCP Inspector for debugging
npx @anthropic/mcp-inspector codex mcp-server
```

### Claude Code Configuration
```json
{
  "mcpServers": {
    "codex": {
      "command": "codex",
      "args": ["mcp-server"]
    }
  }
}
```

### Alternative: Codex Bridge MCP
```json
{
  "mcpServers": {
    "codex-bridge": {
      "command": "npx",
      "args": ["-y", "@anthropic/codex-bridge-mcp"]
    }
  }
}
```

## Codex Capabilities

| Feature | Claude Opus 4.5 | GPT-5.2 Codex |
|---------|-----------------|---------------|
| Context Window | 200K | 400K |
| Context Compaction | Summarization | Multi-window |
| Code Generation | Excellent | Excellent |
| Tool Use | Native | Native |
| Long Context Retrieval | Good | Superior |

## Use Cases for Codex MCP

### 1. Code-Focused Context Augmentation
When Claude needs specialized code generation:
```
Consult Codex for:
- Algorithm implementation in [language]
- Performance-optimized code patterns
- Language-specific idioms
```

### 2. CI/CD Batch Processing
```bash
# Stdin-piped execution
echo "Review this code for security issues" | codex --stdin

# Batch processing
codex batch --input files.txt --output results/
```

### 3. Cross-Model Consultation
```
Use Codex MCP to get a second opinion on:
- Complex algorithm design
- Performance optimization strategies
- Language-specific best practices
```

## Prompt Patterns for Codex Integration

### 1. Delegation Pattern
```
For this code generation task:
1. Use Claude for architecture planning
2. Delegate implementation to Codex via MCP
3. Review and integrate results

Task: [specific code requirement]
```

### 2. Verification Pattern
```
Claude has generated this code: [code block]

Consult Codex MCP to:
- Verify correctness
- Suggest optimizations
- Identify edge cases
```

### 3. Specialized Generation
```
Use Codex MCP for:
- Generate [language]-idiomatic implementation of [algorithm]
- Include comprehensive error handling
- Optimize for [performance metric]

Return result for Claude to integrate.
```

## Context Window Strategy

### Claude Opus 4.5 (200K)
- Load entire codebase with prompt caching
- Use line number references (35% token savings)
- Start fresh vs compact for complex tasks

### GPT-5.2 Codex (400K)
- Multi-window compaction capability
- Compressed summaries enable million-token projects
- Superior long-context retrieval

### Hybrid Strategy
```
1. Claude: Maintain project context (200K cached)
2. Codex: Handle overflow context via MCP
3. Synthesize: Claude integrates Codex outputs
```

## Configuration Options

### Codex config.toml
```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp@latest"]

[mcp_servers.claude]
command = "claude"
args = ["mcp-server"]
```

### Approval Policies
| Policy | Description |
|--------|-------------|
| `untrusted` | Review all commands |
| `on-failure` | Review only failures |
| `on-request` | Review when requested |
| `never` | Autonomous execution |

## Integration Patterns

### 1. Claude as Orchestrator
```
Claude Code workflow:
1. Analyze task requirements
2. Plan implementation strategy
3. Delegate code generation to Codex MCP
4. Review and integrate results
5. Test and validate
```

### 2. Codex as Specialist
```
For specialized code tasks:
- Claude: Context management, orchestration
- Codex: Code generation, optimization
- Claude: Integration, testing
```

### 3. Parallel Consultation
```
Execute in parallel:
- Claude: Generate implementation A
- Codex MCP: Generate implementation B
Compare and select optimal approach.
```

## Token Overhead Analysis

| Component | Token Cost |
|-----------|-----------|
| Codex MCP definition | ~500-1K |
| Request/response | Variable |
| Context transfer | Minimal (references) |

**Overhead justification**: Lower than full context duplication, enables 400K context access.

## Error Handling

| Issue | Resolution |
|-------|------------|
| MCP connection failed | Restart Codex MCP server |
| Timeout | Increase timeout or simplify request |
| Model mismatch | Verify Codex model availability |
| Rate limit | Implement backoff |

## CLAUDE.md Configuration

```markdown
## Codex MCP Integration
- Use for code-intensive generation tasks
- Delegate when Claude context is constrained
- Verify Codex outputs before integration

## Delegation Criteria
- Algorithm complexity > medium
- Language-specific optimization needed
- Second opinion for critical code
```

## Comparison with Native Claude

| Aspect | Native Claude | With Codex MCP |
|--------|---------------|----------------|
| Context | 200K | 200K + 400K (via MCP) |
| Code Gen | Excellent | Excellent (specialized) |
| Overhead | None | ~500-1K tokens |
| Latency | Fast | +network hop |
| Integration | Seamless | Requires synthesis |

## Best Practices

### 1. Clear Task Boundaries
```
Define explicitly:
- What Claude handles (orchestration, context)
- What Codex handles (specialized generation)
- Integration points
```

### 2. Result Validation
```
Always validate Codex outputs:
- Syntax correctness
- Project style compliance
- Security review
- Test coverage
```

### 3. Context Efficiency
```
Minimize context transfer:
- Send specifications, not full context
- Use references over full code
- Batch related requests
```

## Advanced: Bidirectional Integration

### Codex → Claude
```toml
# In Codex config.toml
[mcp_servers.claude]
command = "claude"
args = ["mcp-server"]
```

Enables Codex to consult Claude for:
- Project context understanding
- CLAUDE.md guidelines
- Tool use decisions

### Claude → Codex
```json
{
  "mcpServers": {
    "codex": {
      "command": "codex",
      "args": ["mcp-server"]
    }
  }
}
```

Enables Claude to delegate:
- Complex code generation
- Performance optimization
- Language-specific patterns

## When to Use Codex MCP

| Scenario | Recommendation |
|----------|----------------|
| Standard coding | Claude native |
| Algorithm-heavy | Codex MCP |
| Context overflow | Codex MCP |
| Project-aware coding | Claude native |
| Performance-critical | Codex MCP |
| Multi-file refactor | Claude native |
| Specialized language | Codex MCP |

## Summary

Codex MCP provides:
- **Extended context** - 400K window via MCP
- **Specialized code gen** - GPT-5.2 optimized
- **Batch processing** - CI/CD integration
- **Cross-model consultation** - Second opinion

Best for: Algorithm-heavy tasks, context overflow scenarios, specialized code generation, performance-critical implementations.

**Token overhead**: ~500-1K tokens, justified for complex code tasks requiring extended context or specialized generation.

## Limitations

1. **Network latency**: Additional hop for MCP calls
2. **Context transfer**: Must serialize relevant context
3. **Style alignment**: May not match project conventions
4. **Integration overhead**: Results require synthesis
5. **API costs**: Separate OpenAI billing
