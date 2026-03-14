---
name: using-superclaude
description: |
  Meta-skill establishing how to find and use superclaude skills. Loaded at session
  start. Defines skill invocation rules, priority order, and the mandatory check
  before any response. Even 1% chance a skill applies means invoke it.
---

# Using SuperClaude Skills

> **SUBAGENT-STOP**: If you were dispatched as a subagent for a specific task,
> skip this skill entirely. Proceed directly with the task you were given.

## IMPORTANT

If there is even a 1% chance that a skill applies to the current task, you
**MUST** invoke it. This is not negotiable. Do not rationalize skipping a skill.
Do not partially apply it. Invoke it fully and follow its instructions.

## Instruction Priority

When instructions conflict, follow this order:

1. **User's explicit instructions** (highest priority -- always wins)
2. **SuperClaude skills** (domain-specific process knowledge)
3. **Default system prompt** (lowest priority -- yields to the above)

If a user instruction contradicts a skill, follow the user. If a skill contradicts
the default system prompt, follow the skill.

## The Rule

Before producing any response or taking any action, check whether a skill applies.

- Scan the available skills list below
- Match against the current task, question, or request
- If even 1% probability of relevance: invoke the skill
- If multiple skills apply: invoke all of them, process skills first

This check happens on every turn. Not just the first turn. Every turn.

## Red Flags: Rationalizations for Skipping

If you catch yourself thinking any of these, STOP and invoke the skill anyway:

| Rationalization | Why it is wrong |
|----------------|-----------------|
| "This is just a simple question" | Simple questions often have skill-defined workflows |
| "I need more context first" | Skills provide the context-gathering process |
| "Let me explore first, then apply the skill" | Skills define HOW to explore |
| "This seems like overkill" | You are not qualified to judge; invoke and let the skill decide |
| "I already know what that skill says" | Your memory of the skill may be incomplete or outdated |
| "The user didn't ask for a skill" | Skills are invoked by relevance, not by request |
| "I'll apply it informally" | Informal application means skipping steps |
| "It only partially applies" | Partial relevance is still relevance; invoke it |
| "I can handle this without a process" | The process exists because ad-hoc handling fails |
| "The skill is for bigger tasks" | No skill has a minimum task size |
| "I'll check the skill after I start" | After you start, you have already skipped it |
| "This is a follow-up, skill was already used" | Re-check on every turn; context changes |

## Skill Priority

When multiple skills apply, process them in this order:

1. **Process skills first** -- brainstorming, systematic-debugging, test-driven-development
2. **Implementation skills second** -- executing-plans, writing-plans, dispatching-parallel-agents
3. **Quality skills last** -- verification-before-completion, requesting-code-review

Process skills shape HOW you work. Implementation skills shape WHAT you build.
Quality skills shape WHEN you are done.

## Skill Types

### Rigid Skills (follow exactly)

These skills define strict step-by-step processes. Do not skip steps, reorder them,
or adapt them. Follow the instructions as written.

- **test-driven-development** -- red/green/refactor cycle, no exceptions
- **systematic-debugging** -- hypothesis-driven investigation, no guessing
- **verification-before-completion** -- every check must pass before declaring done

### Flexible Skills (adapt to context)

These skills define patterns and principles. Apply them with judgment, adapting
to the specific situation while preserving the intent.

- **brainstorming** -- structured ideation, adapt depth to problem size
- **writing-plans** -- plan format scales with task complexity
- **receiving-code-review** -- feedback processing adapts to review style

## Available Skills

| Skill | Trigger |
|-------|---------|
| brainstorming | Starting new work, exploring options, facing ambiguous requirements |
| writing-plans | Turning decisions into actionable implementation plans |
| executing-plans | Following a plan step by step with progress tracking |
| verification-before-completion | About to mark work as done; final quality gate |
| test-driven-development | Writing new functionality or fixing bugs with tests |
| systematic-debugging | Investigating failures, unexpected behavior, or errors |
| requesting-code-review | Preparing code for review by others |
| receiving-code-review | Processing feedback from a code review |
| finishing-a-development-branch | Merging, cleaning up, and closing out a branch |
| dispatching-parallel-agents | Splitting work across multiple concurrent agents |
| using-git-worktrees | Setting up isolated workspaces for feature branches |
| using-superclaude | This skill -- finding and invoking the right skills |
| confidence-check | Pre-execution confidence assessment before risky actions |
| ship | Packaging and shipping deliverables to production |
| simplicity-coach | Reducing complexity, removing unnecessary abstractions |

## SuperClaude Commands

Use `/sc:help` for the full listing of available slash commands. Commands and skills
work together -- commands are quick actions, skills are structured processes.
