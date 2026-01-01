# Prompt Engineering Guide & Checklist for Claude Code with Opus 4.5

**Research Date:** 2026-01-01
**Depth:** Deep (3-4 hops)
**Confidence:** 0.88 (High)
**Sources:** 25+ (Official Anthropic, MCP Spec, Community)

---

## Executive Summary

This guide consolidates prompt engineering best practices for Claude Code using the Opus 4.5 model. It covers the Anthropic 10-component framework, Claude Code specific patterns, Opus 4.5 optimizations (effort parameter, extended thinking), XML structuring, and operational checklists.

---

## 1. Claude Code Architecture Overview

### System Prompt Structure
Claude Code doesn't use a single system prompt. It dynamically assembles **40+ fragments** based on:
- Mode (Plan, Explore, Delegate, Learning)
- Tools being used
- Sub-agents spawned
- Session state

**Token Distribution:**
| Component | Tokens |
|-----------|--------|
| Main system prompt | ~2,981 |
| Tools section | ~9,400 |
| CLAUDE.md | 1,000-2,000 |

### Component Hierarchy
```
Commands → Manual triggers, reusable shortcuts
Skills → Agent-triggered, autonomous, context-efficient
MCP → External tool integration (APIs, databases)
Hooks → Deterministic control (PreToolUse, PostToolUse)
Sub-agents → Specialized workers for focused tasks
```

---

## 2. CLAUDE.md Configuration

### Hierarchy (loaded in order)
1. `~/.claude/CLAUDE.md` (global)
2. Project root `CLAUDE.md`
3. Subdirectory `CLAUDE.md` files

### Required Contents
```markdown
# Project: [Name]

## Code Style
- [Formatting rules, linting preferences]

## Architecture
- [Key patterns, file structure]

## Build Commands
- `npm run test` - Run tests
- `npm run build` - Build project

## Conventions
- [Branch naming, commit format]
- [Import patterns, module structure]

## Warnings
- [Known issues, sensitive areas]
```

### Best Practice
> "Treat CLAUDE.md as high-level guardrails, not a comprehensive manual. Update after significant changes."

---

## 3. Opus 4.5 Optimization

### Effort Parameter
| Level | Use Case | Token Efficiency |
|-------|----------|------------------|
| `low` | Simple tasks, speed priority | 76% fewer tokens |
| `medium` | Standard work (default) | Matches Sonnet 4.5 |
| `high` | Complex analysis, architecture | +4.3% over Sonnet, 48% fewer tokens |

**Key Insight:** Medium effort achieves Sonnet 4.5 performance while using 76% fewer output tokens.

### Extended Thinking Configuration
```json
{
  "thinking": {
    "type": "enabled",
    "budget_tokens": 2048
  }
}
```

**Rules:**
- Minimum: 1,024 tokens
- Must be < `max_tokens`
- **Cannot combine with `temperature`** (incompatible)
- Start low, increase incrementally
- >32K: Use batch processing to avoid timeouts

**Optimization Strategy:**
1. Start at 1,024 tokens
2. Increase by 1,024 increments for complex tasks
3. Analyze thinking transcript to understand reasoning
4. Find optimal balance for your use case

---

## 4. Prompt Structure Framework

### Anthropic 10-Component Framework
```
[ROLE] + [TASK] + [CONTEXT] + [CONSTRAINTS] + [OUTPUT FORMAT] + [SUCCESS CRITERIA]
```

### XML Tag Patterns (Claude 4 Trained)
```xml
<instructions>
Clear task definition - what TO DO (not what NOT to do)
</instructions>

<context>
Background information, constraints, project details
</context>

<examples>
Few-shot demonstrations with input/output pairs
</examples>

<thinking>
Reasoning steps before final answer
</thinking>

<output_format>
Expected structure: JSON, markdown, code blocks
</output_format>
```

### Why XML Tags Work
- **Clarity:** Separates prompt components
- **Accuracy:** Reduces misinterpretation
- **Flexibility:** Easy to modify sections
- **Parseability:** Enables automated extraction

---

## 5. Claude 4.x Specific Techniques

### Positive Framing
```
# Instead of:
"Do not use markdown in your response"

# Use:
"Your response should be composed of smoothly flowing prose paragraphs."
```

### XML Format Indicators
```
"Write the prose sections in <prose> tags."
"Provide code in <code> tags with language specified."
```

### Agentic Coding Patterns
1. **Write tests first:** `tests.json` before implementation
2. **Verify before moving on:** Run tests, check results
3. **Provide verification tools:** Playwright MCP, computer use
4. **Context awareness:** Inform about compaction/saving

### Verbosity Control
```
# For more visibility during tool use:
"After completing a task that involves tool use, provide a quick summary of the work you've done."
```

---

## 6. Session Management

### Context Limits
| Threshold | Action |
|-----------|--------|
| 0-176K | Full capabilities |
| 176K-200K | Performance degrades |
| >200K | Model "sweats" |

### Best Practices
- `/clear` between unrelated tasks
- One major task per session
- Check token usage before complex operations
- Fresh sessions prevent context drift
- Update CLAUDE.md after significant changes

---

## 7. Skills & Hooks

### Skills Architecture
- Agent-triggered (autonomous activation)
- Context-efficient (progressive disclosure)
- Unbounded size (filesystem-based)
- Bundle instructions + executable code

### Activation Problem & Solution
Skills don't activate reliably (~50% without hooks).

**LLM Eval Hook Solution:**
```json
{
  "hooks": {
    "PreToolUse": [{
      "type": "command",
      "command": "evaluate-skills.sh"
    }]
  }
}
```
- Uses Haiku 4.5 for pre-evaluation
- Cost: ~$0.0004/prompt
- Achieves 100% activation on targeted skills

### PostToolUse Hooks
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "npx prettier --write"
      }]
    }]
  }
}
```

---

## 8. MCP Integration

### Tool Categories
| Tool Type | Use Case |
|-----------|----------|
| Tavily | Web search, research |
| Context7 | Official documentation |
| Sequential | Multi-step reasoning |
| Serena | Session persistence, memory |
| Playwright | Browser automation, E2E |

### Skills vs MCP
- **MCP:** External integrations (REST-like)
- **Skills:** Internal procedural knowledge (workflows)

---

## Comprehensive Checklist

### Pre-Session Setup
- [ ] CLAUDE.md configured (global + project + subdirs)
- [ ] settings.json permissions defined (allow/deny)
- [ ] MCP servers configured for needed tools
- [ ] Skills installed with activation hooks
- [ ] Effort level pre-determined for task type

### Prompt Structure
- [ ] Clear task definition (what TO DO)
- [ ] Context provided (constraints, background)
- [ ] Role defined (expertise, persona)
- [ ] Output format specified (XML tags, JSON schema)
- [ ] Success criteria stated
- [ ] Examples included (few-shot if complex)

### Opus 4.5 Configuration
- [ ] Effort level selected:
  - [ ] Low: Simple tasks, speed priority
  - [ ] Medium: Standard work (default)
  - [ ] High: Complex analysis, architecture
- [ ] Extended thinking configured:
  - [ ] Budget >= 1,024 tokens
  - [ ] Start low, increase if needed
  - [ ] Temperature NOT set (incompatible)
- [ ] Context budget allocated appropriately

### XML Structure Applied
- [ ] `<instructions>` wraps task details
- [ ] `<context>` wraps background info
- [ ] `<examples>` wraps few-shot demos
- [ ] `<thinking>` for reasoning before answer
- [ ] Output tags defined (`<json>`, `<reply>`, `<code>`)

### Session Management
- [ ] `/clear` between unrelated tasks
- [ ] Token usage checked before complex ops
- [ ] Stay under ~176K active context
- [ ] Update CLAUDE.md after significant changes
- [ ] One major task per session

### Agentic Coding
- [ ] Plan mode before implementation
- [ ] Tests written before code (tests.json)
- [ ] Verification tools provided (Playwright, etc.)
- [ ] Git commit patterns established
- [ ] Self-verification loops enabled

### Anti-Patterns Avoided
- [ ] No "do not" instructions (use positive framing)
- [ ] No massive monolithic prompts (break into steps)
- [ ] No skipped verification steps
- [ ] No temperature with extended thinking
- [ ] No assumptions (use hooks for determinism)

---

## Quick Reference Card

### Effort Selection Matrix
| Task Type | Effort | Thinking Budget |
|-----------|--------|-----------------|
| Bug fix, simple edits | low | 1,024 |
| Feature implementation | medium | 2,048-4,096 |
| Architecture, refactoring | high | 8,192-16,384 |
| Complex debug, system design | high | 16,384-32,768 |

### Prompt Template
```markdown
<instructions>
You are [ROLE] working on [PROJECT].
Your task is to [SPECIFIC TASK].
</instructions>

<context>
[BACKGROUND INFO]
[CONSTRAINTS]
[RELEVANT CODE/FILES]
</context>

<output_format>
Provide your response as:
1. Analysis in <thinking> tags
2. Final output in <result> tags
</output_format>

<success_criteria>
- [CRITERION 1]
- [CRITERION 2]
</success_criteria>
```

---

## Sources

### Official Anthropic
- [Prompt Engineering for Business Performance](https://www.anthropic.com/news/prompt-engineering-for-business-performance)
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Writing Effective Tools for AI Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Building with Extended Thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
- [Claude 4.x Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Introducing Claude Opus 4.5](https://www.anthropic.com/news/claude-opus-4-5)

### Documentation
- [Claude Code Settings](https://code.claude.com/docs/en/settings)
- [Claude Code Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [XML Tags in Prompts](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags)
- [Anthropic Cookbook - Extended Thinking](https://github.com/anthropics/anthropic-cookbook)
- [Anthropic Courses - Prompt Engineering](https://github.com/anthropics/courses)

### Community
- [Claude Code System Prompts (Piebald-AI)](https://github.com/Piebald-AI/claude-code-system-prompts)
- [CLAUDE.md Best Practices (Arize)](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/)
- [How to Make Claude Code Skills Activate Reliably](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably)
- [What Makes Claude Code So Good (MinusX)](https://minusx.ai/blog/decoding-claude-code/)

---

*Research conducted using Tavily search, Context7 documentation, and Sequential reasoning MCP.*
