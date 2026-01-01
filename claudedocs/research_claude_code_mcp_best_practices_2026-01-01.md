# Claude Code MCP Best Practices

**Research Date:** 2026-01-01
**Research Depth:** Standard (2-3 hops)
**Confidence:** 0.85 (High - multiple authoritative sources)
**Sources:** 15+ (Official docs, Anthropic engineering, community)

---

## Executive Summary

This research consolidates best practices for using Model Context Protocol (MCP) with Claude Code, covering security, configuration, tool design, architecture, and operational guidelines from official Anthropic documentation, the MCP specification, and community sources.

---

## 1. Security Best Practices

### Authentication & Authorization

| Requirement | Implementation |
|-------------|----------------|
| OAuth 2.1 | REQUIRED for remote servers |
| PKCE | REQUIRED for all clients |
| Token storage | Secure storage following OAuth best practices |
| Token rotation | SHOULD implement for enhanced security |
| HTTPS | REQUIRED for all authorization endpoints |

### Transport Security (Python SDK)

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

security_settings = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=["localhost:8000", "api.example.com"],
    allowed_origins=["http://localhost:3000", "https://app.example.com"]
)
mcp = FastMCP("Secure Server", transport_security=security_settings)
```

### Permission Tiers

- **Read-only by default** - Enable write operations only through explicit approval
- **Query logging** - Capture all interactions for audit
- **Row-level security** - Enforce data access policies at source
- **Never run as root** - AI should never have admin powers

### OAuth 2.1 Resource Server Implementation

```python
from pydantic import AnyHttpUrl
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP

class SimpleTokenVerifier(TokenVerifier):
    """Verify access tokens from authorization server."""

    async def verify_token(self, token: str) -> AccessToken | None:
        # Implement token validation:
        # - Verify signature with AS public key
        # - Check expiration
        # - Validate scopes
        if token == "valid-token":
            return AccessToken(token=token, scopes=["user"], expires_at=None)
        return None

mcp = FastMCP(
    "Protected Service",
    token_verifier=SimpleTokenVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl("https://auth.example.com"),
        resource_server_url=AnyHttpUrl("http://localhost:3001"),
        required_scopes=["user"]
    )
)
```

---

## 2. Configuration Best Practices

### File Structure

| File | Purpose | Scope |
|------|---------|-------|
| `~/.claude/settings.json` | Global user settings | User |
| `.claude/settings.local.json` | Personal/sensitive settings | Local |
| `.mcp.json` | Project MCP servers | Project |
| `managed-settings.json` | Enterprise policies | Enterprise |

### MCP Server Scopes

```bash
claude mcp add --scope local    # Current setup only (default)
claude mcp add --scope project  # Shared in .mcp.json
claude mcp add --scope user     # Available across all projects
```

### Permission Configuration

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write",
      "Bash(git *)",
      "Bash(npm *)"
    ],
    "deny": [
      "Read(.env*)",
      "Write(production.*)"
    ]
  }
}
```

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `MCP_TIMEOUT` | Startup timeout (e.g., `10000` for 10s) |
| `MAX_MCP_OUTPUT_TOKENS` | Output token limits |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Max output tokens |
| `BASH_DEFAULT_TIMEOUT_MS` | Bash command timeout |

### MCP Server Configuration Example

```json
{
  "mcpServers": {
    "mcp-omnisearch": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-omnisearch"],
      "env": {
        "TAVILY_API_KEY": "your-key-here"
      }
    }
  }
}
```

---

## 3. Tool Design Best Practices

### Namespacing

> "Your AI agents will potentially gain access to dozens of MCP servers and hundreds of tools. When tools overlap in function, agents get confused about which ones to use."

**Recommendations:**
- Use clear, unique tool names
- Prefix with domain context (e.g., `github_create_pr`, `slack_send_message`)
- Avoid vague names like `send` or `get`

### Tool Annotations

- Mark tools that require **open-world access**
- Flag tools that make **destructive changes**
- Provide **clear descriptions** for each tool and argument
- Use `zod` schemas to validate arguments

### Design for Agents

```python
@mcp.tool()
def get_weather(city: str = "London") -> dict[str, str]:
    """Get weather data for a city.

    Args:
        city: City name (default: London)

    Returns:
        Weather data including temperature, condition, humidity
    """
    return {
        "city": city,
        "temperature": "22",
        "condition": "Partly cloudy",
        "humidity": "65%"
    }
```

### Prompt Best Practices

- Use intuitive names (often mapping directly to UI commands like `/review-code`)
- Provide clear descriptions for the prompt itself and its arguments
- Handle optional arguments gracefully within the prompt generation logic

---

## 4. Architecture Patterns

### Client-Server Model

```
Host (Claude Code) --> MCP Client --> MCP Server --> External Data/Tools
```

**Key Components:**
- **Hosts**: Applications like Claude Code that manage MCP clients
- **Clients**: Protocol handlers that manage stateful 1:1 connections to servers
- **Servers**: Programs that serve context data (local or remote)

### Transport Options

| Transport | Use Case | Auth Method |
|-----------|----------|-------------|
| STDIO | Local servers | N/A (same machine) |
| Streamable HTTP | Remote servers | OAuth 2.1, Bearer tokens, API keys |

### Token Efficiency Patterns

1. Save large MCP responses to `/tmp/mcp_<tool>_<timestamp>.json`
2. Invoke analysis skill to filter data with specified filters
3. Receive compact result (e.g., 300 tokens instead of 10,000)
4. Access full data from preserved file for deeper analysis if required

**Observed Reductions:**
- Small dataset tests: 51% reduction
- Realistic datasets: 92.9% reduction
- Real-world scenarios: 95-98% reduction

---

## 5. Operational Best Practices

### Security Checklist

- [ ] Disable hooks unless explicitly needed
- [ ] Only enable trusted MCP servers
- [ ] Use deny rules aggressively
- [ ] Keep transcript retention short (7-14 days)
- [ ] Run in sandboxed/containerized environment
- [ ] Never run as root
- [ ] Audit `managed-settings.json` monthly

### Block Risky Servers

```json
{
  "disabledMcpjsonServers": ["filesystem"]
}
```

### Enterprise Security Settings

```json
{
  "allowedMcpServers": [
    { "serverName": "github" },
    { "serverName": "memory" }
  ]
}
```

### Review Workflow

1. **Always review changes** before accepting
2. Configure tool permissions for your environment
3. Use hooks for auto code formatting/validation
4. Keep sensitive data in `.env` files with deny permissions
5. Don't use YOLO mode unless proper safeguards are in place

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Settings not applying | Check syntax: `jq . ~/.claude/settings.json` |
| MCP server slow | Increase `MCP_TIMEOUT` |
| Too many tokens consumed | Use token efficiency patterns |
| Permission denied | Check allow/deny rules in settings |

---

## 6. MCP Protocol Requirements

### Security Requirements (from MCP Spec)

1. Clients MUST securely store tokens following OAuth 2.0 best practices
2. Servers SHOULD enforce token expiration and rotation
3. All authorization endpoints MUST be served over HTTPS
4. Servers MUST validate redirect URIs to prevent open redirect vulnerabilities
5. Redirect URIs MUST be either localhost URLs or HTTPS URLs
6. MCP Servers MUST NOT use sessions for authentication

### Implementation Requirements

1. Implementations MUST follow OAuth 2.1 security best practices
2. PKCE is REQUIRED for all clients
3. Token rotation SHOULD be implemented for enhanced security
4. Token lifetimes SHOULD be limited based on security requirements

---

## 7. Sources

### Official Documentation

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification)
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [MCP Architecture Overview](https://modelcontextprotocol.io/docs/learn/architecture)
- [Claude Code Settings](https://code.claude.com/docs/en/settings)

### Anthropic Engineering

- [Writing Effective Tools for AI Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Building Agents with Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
- [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)

### SDK Documentation

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Server Development Guide](https://github.com/cyanheads/model-context-protocol-resources/blob/main/guides/mcp-server-development-guide.md)

### Community Resources

- [Optimizing Token Efficiency in Claude Code Workflows](https://medium.com/@pierreyohann16/optimizing-token-efficiency-in-claude-code-workflows)
- [Configuring MCP Tools in Claude Code](https://scottspence.com/posts/configuring-mcp-tools-in-claude-code)
- [Claude Code Security Best Practices](https://www.backslash.security/blog/claude-code-security-best-practices)
- [MCP Security Implementation Guide for AWS](https://builder.aws.com/content/34ehRAhM6rygBjYNee6sZ6AjPSi/)

---

## 8. Roadmap (MCP Specification)

**Priority Areas for Next Release (November 2025):**
- Asynchronous Operations
- Statelessness and Scalability
- Server Identity
- Official Extensions
- SDK Support Standardization
- MCP Registry General Availability
- Validation

---

*Research conducted using Tavily search and Context7 documentation lookup.*
