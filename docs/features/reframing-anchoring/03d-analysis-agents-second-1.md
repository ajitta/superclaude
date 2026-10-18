# 03d — Phase 2 content value classification: agents (second half) + README

> Split by size into 3 files (part 1 of 3): [part 2](./03d-analysis-agents-second-2.md) · [part 3](./03d-analysis-agents-second-3.md). Section boundaries and content unchanged.

Branch `feature/reframing-anchoring`. Judged only from the text of the files below plus `src/superclaude/ARCHITECTURE.md` and `src/superclaude/scripts/context_loader.py` for delivery. No tests run, nothing else opened.

## 1. Scope and files read

| File (src/superclaude/agents/) | Bytes |
|---|---|
| quality-engineer.md | 5509 |
| refactoring-expert.md | 5436 |
| repo-index.md | 4957 |
| requirements-analyst.md | 4971 |
| root-cause-analyst.md | 5611 |
| security-engineer.md | 5730 |
| self-review.md | 5786 |
| simplicity-guide.md | 8175 |
| socratic-mentor.md | 5260 |
| system-architect.md | 5092 |
| technical-writer.md | 4854 |
| verifier.md | 8578 |
| README.md | 9973 |
| **Total** | **79932** |

Delivery facts used: agents are delivered whole, one file per delegation, via Claude Code native description matching (ARCHITECTURE.md §agents/). `context_loader.py:523` skips any `README` stem, so `agents/README.md` never reaches the model.

Structural note: the 12 agent files share one template (frontmatter, role, focus, actions, outputs, tool_guidance, checklist, memory_guide, examples, gotchas, bounds, handoff). About 60% of every file is template boilerplate whose class is the same in all 12; those rows are repeated per file so each can be re-located, and the byte split for mixed sections (tool_guidance, bounds) is an estimate.

## 2. Classification table

Bytes are approximate; 0 bytes = sub-observation inside a section already counted in another row.

| File | Section | Class | Reason | Failure (B) | Mechanism/exhortation (B) | Quote | ~Bytes |
|---|---|---|---|---|---|---|---|
| quality-engineer | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "Not for running tests and reporting against a plan — verifier" | 387 |
| quality-engineer | role (mission/mindset) | D | Persona/mindset exhortation; no ordering or gate. |  |  | "Go beyond the happy path to uncover hidden failures" | 302 |
| quality-engineer | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 374 |
| quality-engineer | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| quality-engineer | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| quality-engineer | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 377 |
| quality-engineer | outputs | D | Deliverable-type list; restates actions. |  |  | "—" | 299 |
| quality-engineer | checklist | D | Checkbox restatement of actions; no new gate. |  |  | "- [ ]" | 274 |
| quality-engineer | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 487 |
| quality-engineer | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 412 |
| quality-engineer | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 311 |
| quality-engineer | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| quality-engineer | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 52 |
| refactoring-expert | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "Not for preventing complexity before code is written — simplicity-guide" | 390 |
| refactoring-expert | role (mission/mindset) | D | Persona/mindset exhortation; no ordering or gate. |  |  | "Less cognitive load beats a clever rewrite" | 274 |
| refactoring-expert | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 381 |
| refactoring-expert | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| refactoring-expert | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| refactoring-expert | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 440 |
| refactoring-expert | outputs | D | Deliverable-type list; restates actions. |  |  | "—" | 274 |
| refactoring-expert | checklist | D | Checkbox restatement of actions; no new gate. |  |  | "- [ ]" | 381 |
| refactoring-expert | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 484 |
| refactoring-expert | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 547 |
| refactoring-expert | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 335 |
| refactoring-expert | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| refactoring-expert | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 50 |
| repo-index | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "PROJECT_INDEX is missing, more than 7 days old" | 350 |
| repo-index | role (mission/mindset) | D | Persona/mindset exhortation; no ordering or gate. |  |  | "Stay token-frugal at every step" | 239 |
| repo-index | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 345 |
| repo-index | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| repo-index | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| repo-index | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 408 |
| repo-index | outputs | D | Deliverable-type list; restates actions. |  |  | "—" | 241 |
| repo-index | checklist | D | Checkbox restatement of actions; no new gate. |  |  | "- [ ]" | 232 |
| repo-index | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 454 |
| repo-index | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 445 |
| repo-index | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 259 |
| repo-index | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| repo-index | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 48 |
| requirements-analyst | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "Not for choosing an architecture — system-architect" | 429 |
| requirements-analyst | role (mission/mindset) | D | 'Why before how' is the I0 idea stated as a slogan — exhortation, not a step. |  |  | "Ask "why" before "how". Socratic questioning beats assumption" | 276 |
| requirements-analyst | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 363 |
| requirements-analyst | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| requirements-analyst | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| requirements-analyst | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 285 |
| requirements-analyst | outputs | D | Deliverable-type list; restates actions. |  |  | "—" | 265 |
| requirements-analyst | checklist | D | Checkbox restatement of actions; no new gate. |  |  | "- [ ]" | 327 |
| requirements-analyst | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 456 |
| requirements-analyst | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 425 |
| requirements-analyst | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 272 |
| requirements-analyst | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| requirements-analyst | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 55 |
| root-cause-analyst | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "suspected cause must be falsified before remediation" | 386 |
| root-cause-analyst | role (mission/mindset) | D | Persona/mindset exhortation; no ordering or gate. |  |  | "Follow evidence over assumption. Look past symptoms" | 323 |
| root-cause-analyst | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 491 |
| root-cause-analyst | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| root-cause-analyst | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| root-cause-analyst | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 402 |
| root-cause-analyst | outputs | D | Deliverable-type list; restates actions. |  |  | "—" | 403 |
| root-cause-analyst | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 495 |
| root-cause-analyst | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 481 |
| root-cause-analyst | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 272 |
| root-cause-analyst | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| root-cause-analyst | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 57 |
| security-engineer | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "Not for general code review — self-review" | 378 |
| security-engineer | role (mission/mindset) | D | Persona/mindset exhortation; no ordering or gate. |  |  | "Think like the attacker, then build defense in depth" | 248 |
| security-engineer | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 371 |
| security-engineer | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| security-engineer | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| security-engineer | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 507 |
| security-engineer | outputs | D | Deliverable-type list; restates actions. |  |  | "—" | 279 |
| security-engineer | checklist | D | Checkbox restatement of actions; no new gate. |  |  | "- [ ]" | 363 |
| security-engineer | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 461 |
| security-engineer | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 391 |
| security-engineer | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 206 |
| security-engineer | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| security-engineer | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 52 |
| self-review | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "Not for run-and-report test evidence — verifier" | 454 |
| self-review | role (mission/mindset) | D | A4-relevant attitude ('look for what is wrong first') but exhortation only. |  |  | "Assume flaws exist until proven otherwise" | 288 |
| self-review | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 409 |
| self-review | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| self-review | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| self-review | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 371 |
| self-review | checklist | D | Checkbox restatement of actions; no new gate. |  |  | "- [ ]" | 283 |
| self-review | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 525 |
| self-review | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 439 |
| self-review | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 211 |
| self-review | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| self-review | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 50 |
| simplicity-guide | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "Not for restructuring existing code — refactoring-expert" | 407 |
| simplicity-guide | role (mission/mindset) | D | Persona/mindset exhortation; no ordering or gate. |  |  | "Subtraction beats addition. Prevention beats cure" | 465 |
| simplicity-guide | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 377 |
| simplicity-guide | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| simplicity-guide | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| simplicity-guide | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 483 |
| simplicity-guide | outputs | D | Deliverable-type list; restates actions. |  |  | "—" | 217 |
| simplicity-guide | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 497 |
| simplicity-guide | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 407 |
| simplicity-guide | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 283 |
| simplicity-guide | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| simplicity-guide | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 66 |
| socratic-mentor | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "Not for a direct explanation with runnable examples — learning-guide" | 401 |
| socratic-mentor | role (mission/mindset) | D | Persona/mindset exhortation; no ordering or gate. |  |  | "Discovery learning > knowledge transfer > direct answers" | 334 |
| socratic-mentor | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 533 |
| socratic-mentor | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| socratic-mentor | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| socratic-mentor | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 319 |
| socratic-mentor | outputs | D | Deliverable-type list; restates actions. |  |  | "—" | 346 |
| socratic-mentor | checklist | D | Checkbox restatement of actions; no new gate. |  |  | "- [ ]" | 274 |
| socratic-mentor | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 506 |
| socratic-mentor | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 462 |
| socratic-mentor | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 273 |
| socratic-mentor | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| socratic-mentor | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 56 |
| system-architect | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "Not for one service's API or schema — backend-architect" | 385 |
| system-architect | role (mission/mindset) | D | 'Not about adjacent systems' + 'user's stated growth horizon' lock the frame (anti-R2/R1). |  |  | "Think holistically about the question asked, not about adjacent systems" | 400 |
| system-architect | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 393 |
| system-architect | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| system-architect | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
