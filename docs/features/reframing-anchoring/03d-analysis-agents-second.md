# 03d — Phase 2 content value classification: agents (second half) + README

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
| system-architect | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 425 |
| system-architect | outputs | D | Deliverable-type list; restates actions. |  |  | "—" | 391 |
| system-architect | checklist | D | Checkbox restatement of actions; no new gate. |  |  | "- [ ]" | 278 |
| system-architect | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 567 |
| system-architect | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 370 |
| system-architect | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 276 |
| system-architect | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| system-architect | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 54 |
| technical-writer | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "Not for teaching a concept — learning-guide" | 304 |
| technical-writer | role (mission/mindset) | D | Persona/mindset exhortation; no ordering or gate. |  |  | "Write for the audience, not the author" | 309 |
| technical-writer | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 350 |
| technical-writer | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| technical-writer | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| technical-writer | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "query overview → definition → references before whole-file Read" | 240 |
| technical-writer | outputs | D | Deliverable-type list; restates actions. |  |  | "—" | 283 |
| technical-writer | checklist | D | Checkbox restatement of actions; no new gate. |  |  | "- [ ]" | 383 |
| technical-writer | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 475 |
| technical-writer | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 412 |
| technical-writer | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 263 |
| technical-writer | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| technical-writer | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 52 |
| verifier | frontmatter (description/tools/memory) | C | Routing trigger + 'Not for — neighbor' gate; model cannot know the agent roster. |  |  | "Not for a plain test run — the main session runs pytest" | 675 |
| verifier | role (mission/mindset) | D | A2/A3 idea stated as mindset; the mechanism lives in <actions>, so this is duplicate exhortation. |  |  | "A plan line is a hypothesis until a command output confirms it" | 400 |
| verifier | focus | D | Keyword list restating description and actions; generic domain knowledge the model has. |  |  | "— " | 636 |
| verifier | tool_guidance / Ask First trigger list | C | Project-specific list of actions needing confirmation. |  |  | "Ask First:" | 180 |
| verifier | tool_guidance / subagent-cannot-ask boilerplate | D | Identical ~400-byte paragraph in all 12 files; one shortest-form sentence (C) would do. 'Task text counts as confirmation' is a reasonable gate but it is delivered 12 times. |  |  | "As a delegated subagent Claude cannot ask mid-task" | 400 |
| verifier | tool_guidance / Proceed, Symbolic-First, Never | D | Proceed and Never restate the mission; Symbolic-First is a generic tool habit (model greps before reading). A-candidate, not confident on Symbolic-First. |  |  | "run the project's declared build, test, lint and run commands" | 498 |
| verifier | memory_guide | C | Memory category names and 'save only if a future run would act differently' are project conventions; 'verify against current state' is an A2 exhortation (D) inside it. |  |  | "MEMORY.md = prior lessons; verify against current state" | 573 |
| verifier | examples (table) | D | Trigger→behavior rows restate actions in example form; no new mechanism. |  |  | "\| Trigger \| Expected behavior \|" | 829 |
| verifier | bounds / does + never | D | Duplicates mission and tool_guidance Never. |  |  | "<does>" | 630 |
| verifier | bounds / fallback | C | Escalation routing to named neighbor agents. |  |  | "escalate to" | 160 |
| verifier | handoff | C | Command routing after the agent finishes. |  |  | "<handoff next=" | 59 |
| quality-engineer | actions | A | Analyze→design→prioritize→wire CI→track: a model asked for a test plan does this unprompted. No purpose or premise step. |  |  | "Analyze the scenarios, risk areas and critical paths" | 369 |
| quality-engineer | finding_policy | B | Output-shape rule: report everything with severity+confidence tags, refuse prompt guidance like 'don't nitpick'. Resists the prompt's framing of what counts; same 641-byte block in security-engineer and self-review. | A1 (prompt guidance compresses findings), A4 | mechanism (output shape + explicit refusal of prompt filter) | "does not pre-filter under general guidance like "focus on real issues"" | 641 |
| quality-engineer | gotchas / baseline-first, evidence-required | A | Run suite first, report actual output: models do this. |  |  | "run the existing suite before changes" | 250 |
| quality-engineer | gotchas / unchanged-code | D | Scope convention ('tests validate the current task's scope'); narrows frame, anti-I0 in spirit. |  |  | "do not add tests for code the current task did not change" | 124 |
| quality-engineer | checklist / coverage targets | C | Project default thresholds the model cannot know (counted inside checklist row). |  |  | "line ≥80%, branch ≥70% default" | 0 |
| refactoring-expert | actions / 1 and 5 (tool-measured baseline) | B | The baseline number comes from a tool, else is labelled estimated — displaces any complexity figure embedded in the prompt. Weak but structural. | A1 (prompt-embedded number) | mechanism (source gate on the number) | "Capture a baseline complexity metric from a tool's output" | 250 |
| refactoring-expert | actions / 2-4 | A | Pick pattern, small steps, run tests after each: standard refactoring practice. |  |  | "Run the tests after each step" | 248 |
| refactoring-expert | gotchas / status-check | B | Search before starting to see whether the work already exists — a look-beyond-the-prompt step before acting. Minimal I0 mechanism (ordering). | I0 (partial) | mechanism (ordering), but does not ask purpose | "before starting, search to confirm the work is not already done" | 90 |
| refactoring-expert | gotchas / scope-discipline | D | 'Refactor only what was asked' is the opposite of I0's remedy; keep only if the owner wants anti-sprawl over purpose inference. |  |  | "touching file X does not grant license to refactor its callers" | 150 |
| refactoring-expert | gotchas / domain-exceptions, earned-abstraction | A | Essential complexity in auth/crypto and rule-of-three are known to the model. |  |  | "extract on the 2nd occurrence, not the 1st" | 294 |
| repo-index | actions / 1 freshness + re-read from disk | B | Gate: reuse a fresh index only by re-reading it from disk, never from memory; regen is Ask First. Keeps a stale remembered artifact from anchoring the briefing. | A2/A3 (remembered prior output) | mechanism (ordering + gate) | "re-read them from disk (never answer from memory)" | 330 |
| repo-index | actions / 2-4 | C | Where to write (docs/reports/PROJECT_INDEX.md/.json) and the parallel-glob procedure. |  |  | "Write or update docs/reports/PROJECT_INDEX.md" | 239 |
| repo-index | gotchas / token-budget, living-doc | C | Size budget (~3KB/<5KB) and UPPER_SNAKE no-date naming: project facts. |  |  | "PROJECT_INDEX.md ~3KB, PROJECT_INDEX.json <5KB" | 350 |
| repo-index | gotchas / stale-index | D | Duplicates action 1. |  |  | "never from cached or remembered index data" | 177 |
| requirements-analyst | actions / 1 discovery before spec | B | Ordering: discovery questions precede the PRD; as a subagent it returns the questions and stops. Questions the request before specifying — but the file never says to state the inferred purpose or derive a success criterion. | R1/I0 (partial) | mechanism (ordering, stop-and-return); content of the questions unspecified | "Drive structured discovery questions to surface the real requirement" | 330 |
| requirements-analyst | actions / 2-5 | A | Stakeholders, PRD, measurable outcomes, completeness check: standard requirements work. |  |  | "Define measurable outcomes an implementer can verify" | 246 |
| requirements-analyst | gotchas / necessity-gate | D | A gate question, but against over-building, not against a wrong premise; unmeasurable. |  |  | "is the system broken without this?" | 120 |
| requirements-analyst | gotchas / scope-anchoring | D | Explicitly forbids looking beyond the asked requirements — anti-I0. Pairs with Never 'assume unstated reqs'. |  |  | "do not expand to adjacent features or stakeholder groups" | 130 |
| requirements-analyst | gotchas / measurability-first | A | Models already demand verifiable acceptance criteria. |  |  | "never accept "user is happy" as a check" | 142 |
| root-cause-analyst | actions / 2-3 multiple hypotheses then falsify | B | Ordering: generate several hypotheses before testing any — dilutes a prompt-embedded suspected cause. Does NOT say the user's suspect is one hypothesis among them, so the anchor can still head the list. | A1 (suspected cause in prompt) | mechanism (ordering), incomplete quarantine | "Generate multiple hypotheses ranked by simplicity and evidence weight" | 200 |
| root-cause-analyst | actions / 1, 4, 5 | A | Gather evidence, document chain, remediation+prevention: standard RCA. |  |  | "Document the evidence chain" | 227 |
| root-cause-analyst | exploration_budget | B | Measurable re-plan trigger: after three failed hypothesis-test cycles, stop, summarize, ask. The only counted re-plan gate in scope. | A3 (self-anchor, no re-plan trigger) | mechanism (counted gate) | "caps the investigation at three hypothesis-test cycles" | 350 |
| root-cause-analyst | checklist | D | Mostly restates actions; 'backed by direct proof, not absence of alternatives' is a good A2 phrasing but checklist form = exhortation. |  |  | "not absence of alternatives" | 367 |
| root-cause-analyst | gotchas / intent-confirm | B | 'Restate the user's intent before non-trivial work' is the closest thing in scope to an I0 step and it is ordered (before work). But restating the stated intent is not inferring the unstated purpose, and no success criterion is derived. | I0 (partial) | mechanism (ordering); restates, does not infer | "restate the user's intent before non-trivial work" | 150 |
| root-cause-analyst | gotchas / symptom-not-cause | D | Labelling convention for workarounds. |  |  | "document it explicitly as a workaround" | 155 |
| security-engineer | actions | A | Scan, model threats, OWASP check, impact, prioritized remediation: default behavior for a security review request. |  |  | "Scan systematically for security weaknesses across the named scope" | 372 |
| security-engineer | finding_policy | B | Same block as quality-engineer: output shape with severity+confidence, refuses prompt-level filtering. | A1/A4 | mechanism (output shape) | "Recall is the job at this stage; precision is a later stage's job" | 641 |
| security-engineer | gotchas / sc-not-webapp, sc-installer-writes | D | Repo-only leak: both rules apply only inside superclaude's own source tree yet ship to every user's ~/.claude/agents. |  |  | "in superclaude's own source repo (root `pyproject.toml` has `name = "superclaude"`" | 610 |
| self-review | actions | D | Examine→confirm evidence→four-axis report→next steps: procedural; no isolation from the author's rationale. |  |  | "request what is missing instead of guessing" | 314 |
| self-review | outputs / Verdict shape | B | Per-dimension PASS / FAIL(criterion+evidence+repro) / UNVERIFIED(reason) blocks the 'looks good' approval a persuasive rationale invites. | A4 (partial) | mechanism (output shape) | "`UNVERIFIED` with the reason the check could not run" | 365 |
| self-review | finding_policy | B | Same block as quality-engineer/security-engineer. | A1/A4 | mechanism (output shape) | "Coverage beats filtering" | 641 |
| self-review | focus / Requirements 1:1 trace to original intent | D | Tracing deliverable to 'original intent' is A4/I0-relevant but stated as a focus keyword; it also lists 'rationale for designs' as evidence — i.e., it CONSUMES the author's rationale (A4 exposure). |  |  | "rationale for designs" | 0 |
| self-review | gotchas / verification-evidence | C | Tool fact: this agent has no Bash, so tests cannot be run — tests dimension is UNVERIFIED without caller-supplied output. |  |  | "The agent's own tools cannot run tests" | 330 |
| self-review | gotchas / scope-creep | D | 'Review only what changed; don't flag pre-existing issues' narrows the frame (anti-R2). |  |  | "don't reopen the entire task" | 130 |
| self-review | gotchas / premature-approval | D | Duplicates the outputs Verdict rule. |  |  | "never approve on assumption" | 131 |
| simplicity-guide | methodology | D | Dave Thomas OSL exposition + Tip 42 quote: education/persona; model knows feedback loops. |  |  | "the rate of feedback is your speed limit" | 418 |
| simplicity-guide | differentiation | D | Duplicates the description's 'Not for' routing. |  |  | "preventive vs refactoring-expert (curative)" | 286 |
| simplicity-guide | actions / 1-3 orient → restate purpose → question necessity | B | The only ordered purpose step in scope: read artifact first, restate its purpose and constraints, then ask whether the work is needed, with a confidence label, BEFORE any reduction. Restates the artifact's purpose, not the request's purpose; no success criterion derived. | I0 (purpose before acting), R1 (question necessity) | mechanism (ordering: steps 1-3 precede 4) | "Restate the artifact's purpose and constraints" | 420 |
| simplicity-guide | actions / 4-6 | A | Smallest step, verify with feedback, record decisions: generic. |  |  | "one function, not a library" | 332 |
| simplicity-guide | anti_patterns | A | YAGNI, rule of three, hard-code first, avoid dependency accumulation: known to the model. |  |  | "extract on second occurrence fine, on first usually premature" | 582 |
| simplicity-guide | domain_exceptions | A | Essential complexity in security/a11y/compliance/distributed is known; Tesler's Law too. |  |  | "essential complexity cannot be removed, only moved" | 547 |
| simplicity-guide | tool_guidance / Verify-Before-Judging | D | Verify removal claims via a docs-capable Agent or label unverified: A2-adjacent but exhortation-plus-routing; counted in tool_guidance row. |  |  | "dep removal checks current best practice through a docs-capable sub-agent" | 0 |
| simplicity-guide | checklist | D | Restates actions; 'Purpose restated before any simplification recommendation' duplicates action 2; Meta-check is unmeasurable. |  |  | "Purpose restated before any simplification recommendation" | 480 |
| simplicity-guide | example dependency-gate-recommendation | D | Only R3-adjacent content in scope: a yes/no question ('should we add Redis?') gets a conditional answer. It is an example, not a rule. |  |  | "verify load pattern before adopting" | 369 |
| simplicity-guide | gotchas / false-positive, overconfident-removal, stale-knowledge | A | Don't flag domain-standard patterns; say when unsure: default behavior. |  |  | ""seems unnecessary" is not evidence" | 480 |
| simplicity-guide | gotchas / context-blind | D | Third statement of action 2. |  |  | "restate purpose and constraints first (action 2)" | 193 |
| socratic-mentor | actions | D | Teaching protocol (assess level, observation first, reveal name last) — persona. Subagent 'returns the opening questions and stops' sentence is C (~200 bytes). No anchor relevance: the questions are aimed at the user, not at the model's own framing. |  |  | "Reveal the concept name only after the learner articulates the idea" | 598 |
| socratic-mentor | checklist | D | Restates actions. |  |  | "Principle named only after the learner articulates" | 274 |
| socratic-mentor | gotchas | D | ask-not-tell is persona; user-level points at MEMORY.md (C, small). |  |  | "converts the explanation into a question" | 313 |
| system-architect | actions | A | Map dependencies, define interfaces, ADR with rejected alternatives: default for an architecture request. 'sized to user's stated growth horizon' accepts the stated premise (anti-R1). |  |  | "Design solutions sized to user's stated growth horizon" | 367 |
| system-architect | checklist | D | Restates actions. |  |  | "Trade-offs documented with rejected alternatives named" | 278 |
| system-architect | gotchas / necessity-gate, scope-anchoring | D | necessity-gate is unmeasurable; scope-anchoring forbids one-layer-out thinking ('while we're here' is out of scope) — anti-R2. |  |  | "architecture advice answers the user's question, not adjacent systems" | 250 |
| system-architect | gotchas / text-diagrams-only | C | Output format convention. |  |  | "mermaid, ASCII — no binary assets" | 90 |
| system-architect | examples / microservices row | D | R3-adjacent example (yes/no question → staged conditional answer), example only; counted in examples row. |  |  | "staged path (modular monolith first)" | 0 |
| technical-writer | actions | A | Identify reader goal, structure for task completion, runnable examples, trace reader's task: models do this for doc requests. |  |  | "Identify the reader's skill level and the exact goal they bring" | 370 |
| technical-writer | checklist | D | Restates actions plus 'marked unverified' labelling. |  |  | "an example that was not run is marked unverified" | 383 |
| technical-writer | gotchas / no-unsolicited-docs | A | Claude Code's own system prompt already forbids proactive doc files; the 'explicit verb required' refinement is a small C. |  |  | "the word "readme" alone is not permission" | 200 |
| technical-writer | gotchas / naming-convention | C | docs/features/<slug>/ numbered files vs date-suffix one-offs. |  |  | "default docs/features/<slug>/ numbered phase files" | 230 |
| technical-writer | gotchas / audience-match | C | Where to look for audience info (MEMORY.md or task context). |  |  | "check the agent's MEMORY.md or the context passed in the task" | 137 |
| verifier | actions / 1 locate plan | C | Plan path resolution order (docs/features/<slug>/05-plan.md, docs/plans/). |  |  | "else `docs/features/<slug>/05-plan.md`" | 300 |
| verifier | actions / 2 collect commands + hash before-state | C | Where commands live (Proof section, CLAUDE.md, AGENTS.md) and the git hash-object procedure for proving no edits. |  |  | "git ls-files -o --exclude-standard -z \| xargs -0 -r git hash-object" | 520 |
| verifier | actions / 3 run as written, absolute paths | C | Harness fact (cwd does not persist between Bash calls) + one-command-per-call convention. |  |  | "with absolute paths and one command per Bash call" | 190 |
| verifier | actions / 4 exercise behavior, not infer from suite | B | Gate: MATCH requires the changed behavior to be exercised and its output read; a green suite is not evidence. Blocks trusting the plan/suite over observation. | A2 (document/plan trusted over observation) | mechanism (evidence gate) | "read the output rather than inferring it from a green suite" | 250 |
| verifier | actions / 5 per-claim MATCH/MISMATCH/UNVERIFIED + hash recheck | B | Output shape: every plan claim is individually confronted with an observation; struck-task rule needs a '## Deviations' reason. Plan is treated as hypothesis list, not truth. | A2 | mechanism (output shape); '## Deviations' format is C | "classify each as MATCH, MISMATCH or UNVERIFIED with its evidence line" | 330 |
| verifier | actions / 6 report and stop, never repair | B | Isolation: verification and fixing are different roles, so the verifier cannot bend observation toward making the plan work. | A3/A4 (role isolation) | mechanism (isolation) | "a mismatch is reported, never repaired" | 120 |
| verifier | outputs (Ran/Saw/Mismatches/Unverified) | B | Observation-only report shape; 'none found' must list the claims checked. | A2 | mechanism (output shape) | "stated as observation ("the CLI printed X"), not as judgment" | 565 |
| verifier | checklist | D | Restates actions 2-6 as checkboxes. |  |  | "Every command in the report was run in this session" | 513 |
| verifier | gotchas / proof-written-ahead | B | Sharpest A2 statement in scope: the plan's Proof numbers may predate the run — re-run, never copy. | A2 (document anchor) | mechanism (gate on source of numbers) | "re-run its commands, never copy its numbers" | 150 |
| verifier | gotchas / failure-record | B | After an unexpected failure: record hypothesis+next and take a DIFFERENT probe, never an identical retry — a minimal re-plan trigger. | A3 (self-anchor after failure) | mechanism (forbids identical retry) | "take one different probe, never an identical retry" | 200 |
| verifier | gotchas / green-suite-is-not-behavior, cwd-resets, scope-of-report | D | green-suite duplicates action 4; cwd-resets duplicates action 3; scope-of-report narrows the frame (R2) to the plan. |  |  | "cd` does not persist between Bash calls" | 425 |
| README.md | whole file | D | Not delivered to the model: context_loader.py:523 excludes README stems, and ARCHITECTURE.md says agents are delivered by CC-native description matching. Maintainer doc. If it were delivered: Available Agents + Cross-Agent Conflict Resolution tables would be C (~3.3KB); Model Routing (Fable/Sonnet pricing, ~2.6KB), Permission Framework, Authoring Rules pointer to .claude/rules, Agent Memory internals are repo-only; Escalation Rules '>10% chance of breaking change' is unmeasurable. |  |  | "Risk: >10% chance of breaking change → escalate" | 9973 |

## 3. Anchor-point map

| File | Moment | What arrives | B step before it? |
|---|---|---|---|
| quality-engineer | task text | action instruction ('build a test strategy for X') | none — action 1 starts analysing scenarios of the named scope; no purpose/criterion step |
| quality-engineer | reading code under change | code, existing tests, CI config | none |
| quality-engineer | writing the report | prompt guidance such as 'focus on real issues' | yes — finding_policy: "does not pre-filter under general guidance" (A1/A4 output shape) |
| refactoring-expert | task text | action instruction, possibly with a complexity figure | partial — "Capture a baseline complexity metric from a tool's output" (A1) and "search to confirm the work is not already done"; no purpose step |
| refactoring-expert | reading code | code + comments/docstrings | none (A2 gap: comments explaining why code is shaped a way are trusted) |
| repo-index | task text | 'index the repo' / 'give me an overview' | n/a — purely mechanical task |
| repo-index | existing index | prior PROJECT_INDEX files / remembered index | yes — "re-read them from disk (never answer from memory)" (A2/A3) |
| requirements-analyst | task text | fuzzy feature request ('we want a dashboard') | partial — action 1 "Drive structured discovery questions to surface the real requirement"; the file does not say to state the inferred purpose or a success criterion, and gotcha scope-anchoring forbids looking outward |
| requirements-analyst | stakeholder input | stakeholder statements, existing specs | none — 'Never ... assume unstated reqs' and 'skip discovery when reqs exist' accept supplied framing (R1) |
| requirements-analyst | prioritization | MoSCoW candidate list | none — no rule against a starred default (R3) |
| root-cause-analyst | task text | symptom report, often with a suspected cause | partial — "restate the user's intent before non-trivial work" (I0, restates not infers); "Generate multiple hypotheses" (A1) but the user's suspect is not explicitly demoted to one-of-many |
| root-cause-analyst | logs/evidence | logs, prior postmortems, prior AI output | none for prior documents (A2); evidence-over-narrative is exhortation |
| root-cause-analyst | after failed cycles | own earlier hypotheses | yes — exploration_budget: "caps the investigation at three hypothesis-test cycles" (A3 counted gate) |
| security-engineer | task text | 'audit X' instruction, maybe 'I think it's SQLi' | none — action 1 scans 'the named scope'; no purpose or premise step |
| security-engineer | reading code | code + comments ('sanitised upstream'), README security notes | none (A2 gap) |
| security-engineer | writing the report | prompt guidance / scope limits | yes — finding_policy (A1/A4 output shape) |
| self-review | task text | 'review this' + the author's description/rationale | none — focus lists "rationale for designs" as EVIDENCE; nothing orders code-before-rationale or withholds the rationale (A4 gap, the biggest in scope) |
| self-review | work product | diff/plan/design + tests claimed | partial — Verdict shape PASS/FAIL/UNVERIFIED and "42/42 pass requires test output in hand" (A2/A4 output shape) |
| self-review | plan review | a prior plan | partial — checklist "Requirements traced 1:1 to acceptance criteria / stated intent" (stated, not inferred intent) |
| self-review | delegate result | output of an Agent call (tool list includes Agent) | none |
| simplicity-guide | task text | brief/design/'should we add X?' | YES — actions 1-3: "Orient by reading the artifact" → "Restate the artifact's purpose and constraints" → "Question whether the work is needed ... state confidence" before any reduction (I0/R1). Closest to the restructure principle in scope. No success criterion derived. |
| simplicity-guide | yes/no question | 'should we add Redis for caching?' | example only — dependency-gate example answers conditionally ("verify load pattern before adopting"); not a rule (R3 gap) |
| simplicity-guide | delegate result | docs-check sub-agent verdict | none — result reported with the delegate's confidence; no cross-check |
| socratic-mentor | task text | 'quiz me toward X' | n/a — the agent questions the learner, not its own framing; no I0/A/R moment |
| system-architect | task text | design request with stated growth horizon | none — action 2 "sized to user's stated growth horizon" and mindset "not about adjacent systems" accept the frame (R1/R2 anti-mechanism) |
| system-architect | existing architecture | current patterns, ADRs, diagrams | none (A2 gap: existing ADR rationale trusted) |
| system-architect | yes/no question | 'should we move to microservices?' | example only — "trade-off matrix vs current pain, staged path"; not a rule (R3 gap) |
| technical-writer | task text | 'document the API' | none — action 1 identifies the READER's goal, not the requester's purpose; A-level |
| technical-writer | source material | code, docstrings, existing README | none — 'document unverified behavior' in Never is exhortation (A2 gap: docstrings over code) |
| verifier | task text | 'verify X against its plan' | none for purpose — verifier never asks whether the plan serves the feature's purpose (R2: frame locked to the plan document by design) |
| verifier | plan document | prior plan with Proof section and checked boxes | YES — "re-run its commands, never copy its numbers"; "read the output rather than inferring it from a green suite"; per-claim MATCH/MISMATCH/UNVERIFIED (A2) |
| verifier | command failure | own failed probe | yes — failure-record: "take one different probe, never an identical retry" (A3 minimal) |
| verifier | compaction / re-entry | — | none anywhere in scope (A3 re-entry rule absent) |
| README.md | — | not delivered | n/a |

**I0 check per file** (does any step make the model state the purpose behind the request and derive a success criterion BEFORE acting?):

- simplicity-guide — purpose yes, criterion no: "2. Restate the artifact's purpose and constraints; if uncertain about the domain, ask the user rather than assume." Then "3. Question whether the work is needed and what the smallest thing that works looks like; state confidence (high, medium, low) and its basis."
- root-cause-analyst — restatement only: "intent-confirm: restate the user's intent before non-trivial work". Restates the stated intent; does not infer the unstated purpose; no criterion.
- requirements-analyst — questions only: "Drive structured discovery questions to surface the real requirement." No instruction to state purpose or criterion; action 4 ("Define measurable outcomes") comes after specification, as an output.
- All other nine agents — no. quality-engineer, security-engineer, system-architect, technical-writer, refactoring-expert, verifier, self-review, repo-index, socratic-mentor start acting on the named scope at action 1.

## 4. Totals per class

| Class | Rows | ~Bytes | Share of 79.9 KB |
|---|---|---|---|
| A already does it | 15 | 5026 | 6% |
| B structural remedy | 18 | 6023 | 7% |
| C project information | 70 | 18043 | 22% |
| D other | 119 | 50601 | 63% |

D without README.md: ~40628 bytes (~58% of the 12 agent files). B is concentrated in verifier (~1.6 KB), the shared finding_policy block (3 × 641 B), root-cause-analyst (~0.7 KB) and simplicity-guide (~0.4 KB). A is low only because most generic practice in these files is phrased as duplicate checklist/example/bounds restatements, which were counted as D (duplicate) rather than A.

## 5. Top 10 findings

1. **Biggest D deletion — template boilerplate, ~40 KB across 12 files.** role/mindset, focus, outputs, checklist, examples, bounds/does+never restate the actions or the description. Per file ~2.3 KB. The 400-byte 'As a delegated subagent Claude cannot ask mid-task…' paragraph appears verbatim 12 times (~4.8 KB) and could be one sentence or live once in the delivery layer.
2. **Biggest B gap — self-review has no A4 isolation.** It is the reviewer, yet `focus` lists "rationale for designs" as evidence and nothing orders code-before-rationale or withholds the author's description. A structural fix (read diff → form findings → then read author rationale → reconcile) is absent; the Verdict shape only mitigates premature approval.
3. **I0 is addressed by one agent only, partially.** simplicity-guide actions 1-3 order orient → restate purpose → question necessity before acting. No file in scope derives a success criterion from the purpose, and eleven agents start on the named scope at action 1. requirements-analyst (the agent whose job is 'the real requirement') never says to state the inferred purpose.
4. **Three files contain anti-I0/anti-R2 rules.** refactoring-expert scope-discipline ("touching file X does not grant license to refactor its callers"), requirements-analyst scope-anchoring + Never 'assume unstated reqs', system-architect scope-anchoring ("'while we're here' is out of scope") and mindset ("not about adjacent systems", "user's stated growth horizon"). These enforce the frame lock the owner wants to break; decide which way to go.
5. **README.md (~10 KB) is not delivered** (`context_loader.py:523` excludes README stems). Its Model Routing section (~2.6 KB of Fable/Sonnet pricing), Permission Framework, Agent Memory internals and the `.claude/rules/` pointers are maintainer text. If it is ever delivered, only the agent roster and Cross-Agent Conflict tables are C.
6. **A1 is handled by output shape, not by ordering.** finding_policy (3 × 641 B) refuses prompt filtering — a real mechanism. But no agent quarantines a prompt-embedded number or suspected cause: root-cause-analyst generates 'multiple hypotheses' without saying the user's suspect is one of them and must not head the list; refactoring-expert's tool-sourced baseline is the only number gate.
7. **A3 has two real gates, both narrow.** root-cause-analyst exploration_budget (three cycles then stop and ask) and verifier failure-record (different probe, never identical retry). No file has a general 'evidence invalidates the plan → re-plan' trigger or a post-compaction re-entry rule.
8. **R3 exists only as examples.** simplicity-guide 'should we add Redis?' and system-architect 'should we move to microservices?' both show a conditional/staged answer to a yes/no question, but as example rows (D). No rule forbids a bare yes/no or a recommended default; the agents' own Ask-First questions to the user also carry no 'present options without a default' rule.
9. **Exhortations dressed as B.** 'verify against current state before acting on them' (memory_guide ×12), 'A plan line is a hypothesis…' (verifier mindset), 'Assume flaws exist until proven otherwise' (self-review mindset), 'Follow evidence over assumption' (root-cause mindset), 'not absence of alternatives' (root-cause checklist). All D; the real mechanisms sit in verifier actions 4-5 and exploration_budget.
10. **A-class generic knowledge ~5 KB, concentrated in simplicity-guide** (anti_patterns + domain_exceptions ≈ 1.1 KB, methodology 0.4 KB) and in the actions blocks of quality-engineer, security-engineer, system-architect, technical-writer. security-engineer's two `sc-*` gotchas (610 B) are repo-only leaks shipped to every install.

Keep list (shortest form): every `description` routing gate, Ask-First trigger lists, memory category names, handoff/fallback routing, repo-index paths/budgets/naming, technical-writer naming-convention, verifier actions 1-3 (plan path, command sources, hash procedure), finding_policy (once, shared), verifier actions 4-6 + proof-written-ahead + failure-record, root-cause exploration_budget, simplicity-guide actions 1-3, repo-index action 1.

## 6. Not read

- Any file under `~/.claude/`, the repo `.claude/`, `docs/`, `CHANGELOG.md`, root `README.md` (isolation rule).
- Other agents referenced by name (backend-architect, performance-engineer, learning-guide, python-expert, deep-researcher, insight-analyst, project-manager, project-initializer, business-panel-experts, git-workflow, devops-architect, frontend-architect) — out of scope (first-half auditor).
- `commands/`, `modes/`, `core/FLAGS.md` referenced by README.md §Related.
- `src/superclaude/ARCHITECTURE.md` and `scripts/context_loader.py` were grepped only for delivery of agents/README, not read in full.

