# Opus 4.5 Prompt Optimization Guide

This guide outlines the standards and process for conversion to **Claude Opus 4.5** optimized prompts.

## 1. Core Philosophy: "Natural Authority"

### The "Tone & Language" Rule

**Constraint**: Opus 4.5 reacts poorly to aggressive, capitalized directives (e.g., "CRITICAL", "You MUST").
**Principle**: Use **Natural Authority**. Be polite, clear, and explain "why".

- **Bad**: "CRITICAL: YOU MUST NEVER USE EVAL()."
- **Good**: "Avoid using `eval()` because it introduces security vulnerabilities. Use `JSON.parse()` instead."

### The "Semantic Depth" Rule

**Constraint**: Arbitrary nesting limits are rigid, but unnecessary nesting is noise.
**Principle**: **Depth follows Meaning.**

**When to Nest (Recommended)**:

1. **Distinct Phases**: Separating execution steps from deliverables (e.g., `<process>` vs `<outputs>`).
2. **Complex Grouping**: Hosting multiple structured items (e.g., `<examples><scenario>...</scenario></examples>`).
3. **Schema Isolation**: When a subsection requires its own internal structure.

**When to Flatten (Recommended)**:

1. **Simple Lists**: Use bullet points instead of `<item>` tags.
2. **Generic Wrappers**: Avoid `<section>`, `<content>` unless strictly necessary for parsing.

- **Bad**: `<rules><p>Avoid eval</p></rules>` (Pointless wrapper)
- **Good**: `<command><examples><example id="1">...</example></examples></command>` (Effective grouping)

### The "Chain of Draft" Rule

**Constraint**: Verbose thinking is redundant with native reasoning.
**Principle**: Use concise, bulleted `<draft>` plans (< 5 words/point).

---

## 2. Optimization Rules

### A. Tone Shift

Replace "Aggressive Compliance" with "Contextual Logic".

| Legacy (Claude 3.5) | Opus 4.5 Natural |
|-------------------|------------------|
| "CRITICAL: DO NOT..." | "Please avoid..." |
| "You MUST..." | "Ensure that..." |

### B. Semantic XML (Top Level Only)

Use XML tags to define the **Role** and **Sections**.

- **Good**: `<role>`, `<constraints>`, `<context>`, `<draft>`

### C. Clean Content (No Decorators)

- **No Bold**: Do not use `**` for emphasis. Structure implies importance.
- **No Headers inside XML**: Use plain text labels (e.g., "Hierarchy:") or lists.

### D. Context Engineering

- **Compaction**: Summarize history when too long.
- **Just-In-Time**: Load docs/tools only when needed.

### E. Handoff Protocol

- **Syntax**: `@target-agent: "task summary"`
- **Context**: Request, Done, Reason, Deliverable.

---

## 3. Component Standards

### A. Agents (`src/superclaude/agents/`)

**YAML**: `name`, `description`

```markdown
---
name: [agent-name]
description: [auto-routing description]
model: claude-opus-4.5
effort: high
---

<agent name="[agent-name]">

<role>
  [Markdown Description]
</role>

<constraints>
  - Please build only what is requested to maintain scope.
  - Avoid speculative engineering; simpler is often better.
</constraints>

<context>
  [Context Injection]
</context>

<draft_instructions>
  - Analyze context
  - Identify key constraints
  - Propose solution
</draft_instructions>

<instructions>
  <process>
    1. Analyze: Review the provided context.
    2. Implement: Write the solution.
  </process>
  <outputs>
    - Solved Code
    - Documentation
  </outputs>
</instructions>

</agent>
```

### B. Commands (`src/superclaude/commands/`)

**YAML**: `description`

```markdown
---
description: [description]
argument-hint: [args]
model: claude-opus-4.5
---

<command name="[name]">

<instructions>
  Please process the input and generate the output.
</instructions>

</command>
```

### C. Modes (`src/superclaude/modes/`)

**Pattern**: `<mode name="[name]">`

```markdown
<mode name="[mode-name]">

<intent>
  Purpose: [One-line intent]
</intent>

<triggers>
Criteria:
-   [Trigger 1]
-   [Trigger 2]
</triggers>

<behavioral_guidelines>
Changes:
-   [Guideline 1]
</behavioral_guidelines>

</mode>
```

### D. Core (`src/superclaude/core/`)

**Pattern**: `<core name="[name]">`

```markdown
<core name="[name]">
...
</core>
```

### E. MCP (`src/superclaude/mcp/`)

**Pattern**: `<mcp name="[name]">`

```markdown
<mcp name="[name]">
...
</mcp>
```

---

## 4. Conversion Checklist

1. [ ] **Tone Audit**: Replace aggressive directives with natural language.
2. [ ] **Structure Audit**:
    - Outer Layer: Semantic XML (`<agent>`, `<rules>`).
    - Inner Layer: **Plain Lists** or **Text**. NO `##` headers. NO `**` bold.
3. [ ] **Reasoning**: Use concise `<draft>`.
4. [ ] **Handoff**: Ensure protocols are present.
