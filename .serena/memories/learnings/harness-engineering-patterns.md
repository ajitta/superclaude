# Harness Engineering Patterns — Key Learnings

## Field Definition
Harness Engineering = meta-discipline of designing execution environments, constraints, and feedback loops for AI agents. Convergent across OpenAI, Anthropic, LangChain (2025-2026).

## Three Instantiations
- **OpenAI**: Environmental Engineering — accumulate durable infrastructure, progressive disclosure, entropy management
- **Anthropic**: Cognitive Engineering — diagnose model limits, build targeted interventions, plan to remove
- **LangChain**: Middleware Engineering — composable middleware stack, batteries-included

## Seven Universal Components
1. Architecture Constraints (SuperClaude: 7/10 — core/ always-loaded)
2. Repository Knowledge System (6/10 — context_loader)
3. Agent Legibility (4/10 — gap)
4. Feedback Loops & Observability (3/10 — gap)
5. Validation & Guardrails (6/10 — skills)
6. Entropy Management (2/10 — biggest gap)
7. Middleware Architecture (4/10 — emerging skills)

## Bitter Lesson Classification
- Durable: workflow discipline, behavioral correction (YAGNI), entropy management, feedback loops
- Adaptive: token efficiency, MCP routing, depth profiles, prompt patterns
- Uncertain: generation-evaluation separation, agent delegation scoring

## Critical Anthropic Findings (Source-Verified)
- "Out of the box, Claude is a poor QA agent" — agents approve mediocre work
- "Tuning a standalone evaluator to be skeptical is far more tractable than self-critique" (exact quote)
- Evaluator effectiveness came from: separate agent + iterative tuning + concrete criteria
- Sprint contract negotiation was collaborative (NOT information isolation)
- Opus 4.6 made some harness components unnecessary → supports "build to remove"
- 20x cost multiplier ($9 solo vs $200 harness) — the most important number

## SuperClaude = Constitutional Layer Harness
- core/ always-loaded = Architecture Constraints + Repository Knowledge + Validation
- context: fork isolates conversation/reasoning but reloads core/ via CLAUDE.md @import
- Genuine diversity requires: different evidence sources + different evaluation frames (not just different personas)
