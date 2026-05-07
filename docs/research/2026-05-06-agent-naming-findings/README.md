# Agent Naming — Distilled Findings

**Date**: 2026-05-06
**Source**: 107 trials across 3 experiment phases via `claude -p`, ~$20 total. Detailed audit trail and raw data live on branch `docs/agent-naming-experiment` (not merged to keep master lean).

This document captures the **durable findings** that future SuperClaude agent authoring should know. Methodology lessons live in `methodology-lessons.md`.

## The 4 Core Findings

### 1. Renaming is not cosmetic

Changing `name` and `description` of an agent (body unchanged) produces measurable shifts in subagent output:

- **Length**: `python-engineer` outputs ran ~46% shorter than `python-expert`'s on the same fixtures (945 vs 509 chars after excluding broken trials).
- **Style**: `-engineer` had higher prescriptive-verb density (`use|raise|add|replace|change`) per 100 words.
- **Direction matches English connotation**: `expert` connotes one-shot authoritative output; `engineer` connotes terse procedural output.

Don't assume any agent rename is purely aesthetic — verify on representative tasks.

### 2. Description vocabulary can trigger context-hallucination

Five out of five `python-engineer` outputs and three out of three `senior-python-engineer` outputs on the pytest-writing task fabricated prior context — claims like:

- "The test file already exists at tests/test_is_palindrome.py"
- "Here's the generated test file (… 509 lines): # … 90 test functions …"
- "Fixed. Changed `high-performance` → `performant` in the mission" (recursive: subagent narrating an edit to its own definition file)

Reverting senior's `<mission>` body to the original `python-expert` wording **did not fix it**. The hallucination is description-driven, not body-driven.

The pattern: descriptions that imply prior practice/experience appear to prime a "this is a continuation of prior work" frame.

| Vocabulary in description | Hallucination rate (pytest task) |
|---|---|
| "**following** SOLID and modern engineering practices" (engineer) | 5/5 |
| "with pragmatic tradeoff judgment and **deep production experience**" (senior) | 3/3 |
| "**learning** to write production-grade code by **applying** conventional patterns" (junior) | 0/3 |
| "**grounded in** SOLID and modern best practices" (expert) | 0/3 |
| "with **deep mastery and seasoned judgment**" (guru) | 0/3 (mild self-correction note in 1 trial) |

Avoid past-implying phrasing in agent descriptions. Use forward-looking voice (`learning`, `applying`, `grounded in`).

### 3. Description directives can override the name's prior

Re-running `python-guru` with the **same name** but a Zen-of-Python wisdom-framed description ("simple is better than complex… values minimal solutions, the smallest abstraction that solves the problem, and code that any junior can read") cut over-engineering signals 25–73% across 15 trials:

| metric (aggregate, 15 trials) | original guru | wisdom guru | Δ |
|---|---|---|---|
| chars | 1486 | 1121 | **−25%** |
| code_lines | 25.5 | 19.6 | −23% |
| classes | 1.27 | 0.53 | **−58%** |
| decorators | 1.13 | 0.40 | **−65%** |
| TypeVar | 0.27 | 0.00 | **−100%** |

On the most over-engineering-prone task (pytest writing) the same name produced classes 6.33→2.67 (−58%) and decorators 5.0→1.33 (−73%). The agent's name was unchanged; only the description text shifted.

This is a **viable lever**: anti-over-engineering can be tuned through description wording without renaming. Caveat — `hypothesis`-style advanced patterns were stickier (only −20%); some priors resist directive override.

### 4. Behavior is task-shape-dependent

`python-expert` was elaborate on free-form pytest writing (75 code lines, hypothesis property tests added unprompted) but **the most minimal of all four variants** on a constrained design task (auth class, "Include only what's essential" — 27.7 lines vs 35.3 junior, 39.3 senior).

`senior-python-engineer` was 0/3 on pytest writing but 3/3 clean on auth class design — the hallucination trigger needs both (a) experience-implying description and (b) long-output enumerable task.

Don't generalize agent behavior from a single task. Evaluation needs both:
- **Free-form long tasks** (where over-engineering and hallucination triggers fire)
- **Constrained design tasks** (where prompt scope shapes behavior more than the persona)

## Practical Implications for SuperClaude

### Don't

- **Don't rename `python-expert` → `python-engineer`** without re-validating on long-output tasks. Hallucination rate goes 0/3 → 5/5.
- **Don't rename `python-expert` → `senior-python-engineer`** for the same reason — the seniority prefix did not rescue from the engineer suffix's failure mode.
- **Don't add `python-guru`** without a wisdom-framed description. The default "deep mastery" framing produced the most over-engineered output of any variant tested.

### Do (carefully)

- **Consider appending a Zen-of-Python clause** to existing `python-expert` / `refactoring-expert` descriptions to reduce over-engineering. Validated on `python-guru`; not yet validated on `-expert`. Run the same fixture set if attempting this.
- **Trust prompt-level scope constraints** ([R06 Scope] Scope, [R18 Necessity Test] Necessity) — `python-expert` already produces minimal output when the prompt says "essential only". Authors should not assume expert is uniformly elaborate.

### Maybe explore

- **`junior-python-engineer` for test-writing scenarios**: comprehensive coverage via `parametrize`, no `hypothesis` abuse, simpler structures, fully reliable on long-output. Worth A/B testing in real SuperClaude usage before adopting.

## Limitations

- N=3 trials per variant per task at most. Effect sizes are descriptive, not pre-registered.
- Single language (Python), single model (Sonnet 4.6 via `claude -p`). Generalization conjectural.
- Hallucination cause not fully isolated — could be name, description vocabulary, or interaction with task length. A larger description-only ablation (varying description while holding name and body fixed) would tighten the causal claim.
- The Phase 1 writeup originally over-claimed "B caught an edge case A missed"; correcting it required reading all 30 trials and running quality classification. See `methodology-lessons.md` for what to do differently next time.

## Where to find the full data

Branch `docs/agent-naming-experiment` (not merged to master) contains:

- 107 raw `claude -p` JSON outputs across 3 experiment phases
- Reproducibility scripts (`run.sh`, `run4way.sh`, `run_phase3.sh`, `rerun.sh`)
- Quality classifier (`quality_check.py`) and metric analyzers (`analyze.py`, `analyze_4way.py`, `analyze_phase3.py`)
- Per-phase READMEs documenting the audit trail of corrections

Check it out with `git checkout docs/agent-naming-experiment` if a deeper dive is needed.
