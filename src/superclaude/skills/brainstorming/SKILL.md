---
name: brainstorming
description: |
  Design-first exploration before any implementation. Use before creating features,
  building components, adding functionality, or modifying behavior. Explores user intent,
  requirements and design through collaborative dialogue before writing code.
---

# Brainstorming Ideas Into Designs

Turn ideas into actionable designs through structured collaborative dialogue. Start by understanding the project context — files, docs, conventions — then guide the user through clarifying questions, approach trade-offs, and design presentation before any code is written.

## HARD GATE

**Do NOT invoke any implementation skill, write code, or take implementation action until the design is explicitly approved by the user.**

This gate applies to EVERY project, regardless of perceived simplicity or urgency.

### Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this gate. "Simple" is exactly where unexamined assumptions waste the most work. A two-minute design conversation can prevent a two-hour rewrite.

## Checklist

1. **Explore project context** — read key files, docs, recent commits, understand current state
2. **Offer visual companion** — if visual questions lie ahead, suggest diagramming or sketching
3. **Ask clarifying questions** — one at a time, prefer multiple choice when possible
4. **Propose 2-3 approaches** — include trade-offs and a clear recommendation
5. **Present design** — scale sections to complexity, get approval before proceeding
6. **Write design doc** — save to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
7. **Spec review loop** — dispatch reviewer subagent, fix issues, max 5 iterations
8. **User reviews written spec** — explicit approval required
9. **Transition to implementation** — invoke writing-plans skill

## The Process

### Understanding the Idea

- Check project state: read README, recent commits, open issues, existing architecture
- Assess scope: is this a new feature, a modification, or a refactor?
- Ask one question at a time — never dump a list of five questions
- Prefer multiple choice over open-ended ("Would you prefer A, B, or C?" over "What do you want?")
- Summarize understanding back to the user before moving on

### Exploring Approaches

- Always present 2-3 distinct options
- Lead with your recommendation and explain why
- For each option, state:
  - What it solves well
  - What it trades away
  - Rough effort estimate (small / medium / large)
- If all options feel equivalent, say so — don't manufacture false distinctions

### Presenting the Design

- Scale detail to complexity:
  - Small change: a few bullet points
  - Medium feature: sections for scope, approach, data flow, edge cases
  - Large system: full design doc with diagrams, interfaces, migration plan
- Present one section at a time, ask if the direction is right before continuing
- Never present a monolithic design and ask "does this look good?"

### Design for Isolation and Clarity

- Break work into the smallest independent units possible
- Define clear boundaries between components
- Specify interfaces explicitly — inputs, outputs, error cases
- Prefer composition over inheritance, loose coupling over tight integration
- Ask: "Can this be tested in isolation?"

### Working in Existing Codebases

- Explore before proposing — understand existing patterns and conventions
- Follow established patterns unless there is a strong reason to diverge
- Document any intentional deviations and the reasoning behind them
- Consider migration paths: can old and new coexist during transition?

## After the Design

### Write the Spec

- Save to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- Include: problem statement, chosen approach, key decisions, interfaces, open questions

### Spec Review Loop

- Dispatch a reviewer subagent (requirements-analyst) to check for:
  - Missing edge cases
  - Unclear interfaces
  - Unstated assumptions
  - Scope creep
- Address findings, re-review — max 5 iterations
- If issues persist after 5 rounds, flag to user for judgment

### User Review Gate

- Present the final spec to the user
- Require explicit approval ("approved", "looks good", "go ahead")
- Silence or ambiguity is NOT approval — ask again

### Terminal State

- Once approved, invoke the writing-plans skill to break the design into implementation steps
- Do not begin coding directly from the design — always create a plan first

## Key Principles

- **One question at a time** — respect cognitive load, never stack questions
- **YAGNI** — design only what is needed now, note future possibilities without building them
- **Explore alternatives** — the first idea is rarely the best; always generate at least two more
- **Incremental validation** — check understanding at each step, don't wait until the end
- **Reversibility** — prefer designs that are easy to change over designs that are "complete"

## SuperClaude Integration

- Use `/sc:brainstorm` command for structured exploration sessions
- Delegate to `requirements-analyst` agent for spec validation during review loop
- Handoff: writing-plans skill for implementation planning after design approval
