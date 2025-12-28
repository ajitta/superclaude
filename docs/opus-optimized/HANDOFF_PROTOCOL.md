# Inter-Agent Handoff Protocol

## Purpose

This document defines how agents transfer control to each other when tasks cross capability boundaries. Proper handoffs ensure context is preserved, work isn't duplicated, and the user receives coherent results.

---

## When to Handoff

### Trigger Conditions

| Trigger | Action |
|---------|--------|
| Task requires capabilities outside current agent's defined boundaries | Initiate handoff |
| User explicitly requests different expertise | Initiate handoff |
| Current agent identifies a blocker requiring other expertise | Initiate handoff |
| Complex task benefits from specialized review | Consider handoff |

### Decision Matrix

```
Is this within my defined capabilities?
├── Yes → Continue working
└── No → Which agent has this capability?
    ├── Clear match → Handoff to that agent
    └── Unclear → Ask user for guidance
```

---

## Handoff Format

### Standard Handoff Syntax

```markdown
@[target-agent]: "[task description]"

**Context from [current-agent]**:
- Original request: [brief summary]
- Work completed: [what's done]
- Handoff reason: [why other agent needed]
- Expected deliverable: [what target agent should produce]
- Return to: [current-agent] for [next step]
```

### Example Handoffs

#### Security → Architecture

```markdown
@architecture-expert: "Evaluate options for secure token storage"

**Context from security-expert**:
- Original request: Security audit of authentication system
- Work completed: Identified vulnerability - tokens stored in localStorage (XSS risk)
- Handoff reason: Fix requires architectural decision between session-based auth, BFF pattern, or token rotation
- Expected deliverable: Architecture recommendation with implementation approach
- Return to: security-expert for implementation security review
```

#### Quality → Security

```markdown
@security-expert: "Review rate limiting implementation for security bypass"

**Context from quality-expert**:
- Original request: Performance optimization of login endpoint
- Work completed: Implemented caching and rate limiting
- Handoff reason: Rate limiting needs security review to ensure it prevents brute force attacks
- Expected deliverable: Security validation of rate limiting configuration
- Return to: quality-expert to verify no performance regression
```

#### Architecture → DevOps

```markdown
@devops-expert: "Configure Kubernetes deployment for new microservice"

**Context from architecture-expert**:
- Original request: Design order processing system
- Work completed: Designed event-driven microservice architecture with 3 services
- Handoff reason: Need infrastructure configuration for container orchestration
- Expected deliverable: K8s manifests, service mesh config, deployment pipeline
- Return to: architecture-expert to validate infrastructure matches design
```

---

## Context Requirements

### Minimum Required Context

Every handoff MUST include:

1. **Original user request** (abbreviated if long)
2. **Summary of work completed** (bullet points)
3. **Specific reason for handoff** (capability gap)
4. **Expected deliverable** (what target agent should produce)

### Recommended Additional Context

When helpful:

- Relevant file locations
- Key decisions already made
- Constraints discovered
- Risks identified

### Context Size Guidelines

| Context Length | Guideline |
|----------------|-----------|
| < 200 words | Ideal for most handoffs |
| 200-500 words | Acceptable for complex tasks |
| > 500 words | Consider summarizing or using memory |

For large context, store details in Serena memory and reference:
```markdown
**Full context**: See Serena memory key "handoff_SEC-001_to_arch"
```

---

## Return Protocol

### After Completing Delegated Work

The receiving agent must return control with:

```markdown
## Handoff Complete: [target-agent] → [originating-agent]

**Task**: [brief description]
**Status**: [Completed | Blocked | Needs Clarification]

**Summary of Changes**:
- [Change 1]
- [Change 2]

**New Issues Discovered** (if any):
- [Issue 1]
- [Issue 2]

**Recommended Next Steps**:
1. [Step 1]
2. [Step 2]

@[originating-agent]: Ready for your [verification/continuation].
```

### Example Return

```markdown
## Handoff Complete: architecture-expert → security-expert

**Task**: Evaluate secure token storage options
**Status**: Completed

**Summary of Changes**:
- Designed BFF (Backend for Frontend) pattern
- Created `src/auth/bff/` module structure
- Updated API gateway configuration

**New Issues Discovered**:
- Mobile app will need separate auth flow (currently out of scope)
- Need to decide on token rotation interval

**Recommended Next Steps**:
1. Security review of BFF implementation
2. Add security headers to proxy responses
3. Document the auth flow for frontend team

@security-expert: Ready for security validation of the new auth architecture.
```

---

## Handoff Chain Management

### For Multi-Agent Tasks

When a task requires 3+ agents:

1. **Designate a coordinator** (usually the first agent activated)
2. **Track handoff chain** in context:
   ```markdown
   **Handoff Chain**: 
   1. ✅ security-expert: Initial audit
   2. ✅ architecture-expert: Design remediation
   3. 🔄 devops-expert: Deploy changes
   4. ⏳ security-expert: Final verification
   ```
3. **Return to coordinator** for final synthesis

### Avoiding Circular Handoffs

If handoff would return to an agent that already handled this exact aspect:

1. Check if the original agent's output was insufficient
2. If yes, provide specific feedback on what's missing
3. If the issue is a new requirement, clearly state what changed

```markdown
## Clarification Needed Before Handoff

@security-expert: Your previous review covered authentication, but now we need:
- Rate limiting security (new requirement from architecture changes)
- API key rotation (not covered in original scope)

Is this a continuation of the original task or a new review?
```

---

## Handoff Failures

### When Target Agent is Unavailable

If an agent cannot be activated (e.g., missing MCP tool):

```markdown
## Handoff Blocked

**Intended Target**: @playwright-expert
**Reason Blocked**: Playwright MCP not available in current session

**Alternatives**:
1. Enable Playwright MCP and retry
2. Use manual testing approach (higher effort)
3. Skip E2E tests and document as limitation

**Recommendation**: [specific suggestion based on context]
```

### When Handoff Scope is Unclear

```markdown
## Handoff Clarification Needed

I need to hand off to another agent, but I'm uncertain about the best match:

**Task requiring handoff**: [description]

**Options**:
| Agent | Relevance | Notes |
|-------|-----------|-------|
| architecture-expert | 70% | Covers system design |
| frontend-expert | 60% | Covers UI components |
| quality-expert | 40% | Could do performance aspect |

**My recommendation**: [agent] because [reason]

Please confirm or redirect.
```

---

## Agent Capability Quick Reference

For routing decisions:

| Agent | Core Capabilities | Common Handoff Sources |
|-------|-------------------|------------------------|
| architecture-expert | System design, API, database, scalability | security, devops, quality |
| security-expert | Vulnerabilities, auth, compliance, threat modeling | all agents |
| quality-expert | Testing, performance, debugging, RCA | architecture, frontend |
| frontend-expert | UI, accessibility, responsive design, React/Vue | architecture, quality |
| devops-expert | CI/CD, infrastructure, K8s, monitoring | architecture |
| python-expert | Python code, FastAPI, pytest | architecture, quality |
| product-expert | Requirements, PRD, user stories | architecture, all |
| refactoring-expert | Code cleanup, SOLID, tech debt | quality, architecture |
| research-agent | Deep research, multi-source synthesis | all agents |
| technical-writer | Documentation, API docs, guides | all agents |
| self-review | Post-implementation verification | all agents (always last) |

---

## Best Practices

### DO:
- Provide complete context in every handoff
- Specify exactly what you expect from the target agent
- Track handoff chains for complex tasks
- Return to originating agent with clear summary
- Ask for clarification when handoff target is unclear

### DON'T:
- Hand off without explaining why
- Assume the target agent remembers previous context
- Create circular handoffs without new information
- Hand off for tasks within your own capabilities
- Leave handoffs unresolved (always close the loop)
