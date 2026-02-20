<component name="practices-reference" type="reference" parent="simplicity-coach">
  <meta>Referenced from SKILL.md — detailed templates for practices and task types</meta>

  <dependency_gate title="Question Your Dependencies">
Before adding a new library, always ask three questions:
1. How many lines of this library do we actually use?
2. How long to write those lines ourselves?
3. Confident it stays safe and compatible in 6 months?
Importing tens of thousands of lines for a 3-line function = installing a time bomb.
Justified when: specialized domain (crypto, compression), mature stable API, using core functionality.
  </dependency_gate>

  <three_level_feedback title="Three Levels of Feedback">
When code fails, distinguish three levels:
1. Bug in the code — fix it (immediate response)
2. Bug in expectations — test or requirement itself is wrong (re-examine)
3. Bug in the process — structural cause (most valuable)
A single process fix prevents many future bugs. Always record: "What is the structural cause?"
  </three_level_feedback>

  <daybook_template title="Engineering Daybook">
Maintain a `DAYBOOK.md` at the project root:
```markdown
## YYYY-MM-DD
### Orient
- Current state: ... | Goal: ... | Completion criteria: ...
### Steps and Learnings
- [Step] ... → [Learn] ...
### Decision Log
- [Decision] Chose Y over X. Reason: ...
- [Dependency] Added/removed library Z. Reason: ...
### Process Bugs
- Structural cause of this mistake: ...
### Notes for Tomorrow
- ...
```
A daybook builds intuition. Intuition = accumulated experience you've forgotten.
  </daybook_template>

  <simplicity_review title="Simplicity Review Checklist">
After completing code, run through these questions:
- Readability: Will I understand this code 6 months from now?
- Dependencies: Any imports or libraries that can be removed?
- Size: Can this function/module be split smaller? Should it?
- Coupling: If this code changes, what other code breaks?
- YAGNI: Code added "just in case"?
- Value: What value does this code deliver to the user?
The act of consciously running through these questions is itself the value.
  </simplicity_review>

  <task_type_detail title="OSL Applied Per Task Type">
New Feature:
1. Orient: summarize goal, current state, completion criteria
2. Pick one core user scenario → write minimal code to make it work
3. Get feedback → if direction is right, add next scenario
4. Summarize learnings after each step

Code Review:
- Only as complex as it needs to be?
- Dependencies justified?
- Tests reveal process bugs, or only catch code bugs?
- Can it be broken into smaller units?

Refactoring:
Goal: not "better" but simpler.
- Orient: What is complex? Why?
- Step: Apply just one small simplification
- Learn: Easier to understand? Still works?

Debugging:
1. How do we fix this bug? (immediate)
2. Why did it occur? (root cause)
3. How to prevent this class of bug from recurring? (process improvement)
Record the answer to the third question.

Technology Selection:
- Evaluate reversibility — prefer easily reversible decisions
- List trade-offs explicitly
- "Both are probably half right and half wrong" — seek a synthesis
  </task_type_detail>
</component>
