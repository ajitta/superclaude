<component name="practices-reference" type="reference" parent="simplicity-coach">
  <meta>Referenced from SKILL.md — detailed templates for practices and task types</meta>

  <dependency_gate title="Question Your Dependencies">
Before add new library, ask three:
1. How many lines of library we actually use?
2. How long write those lines ourselves?
3. Confident stay safe + compatible in 6 months?
Import tens of thousands of lines for 3-line function = install time bomb.
Justified when: specialized domain (crypto, compression), mature stable API, use core functionality.
  </dependency_gate>

  <three_level_feedback title="Three Levels of Feedback">
When code fail, distinguish three levels:
1. Bug in code — fix it (immediate response)
2. Bug in expectations — test or requirement itself wrong (re-examine)
3. Bug in process — structural cause (most valuable)
Single process fix prevent many future bugs. Always record: "What is the structural cause?"
  </three_level_feedback>

  <daybook_template title="Engineering Daybook">
Keep `DAYBOOK.md` at project root:
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
Daybook build intuition. Intuition = accumulated experience you forgot.
  </daybook_template>

  <simplicity_review title="Simplicity Review Checklist">
After finish code, run through questions:
- Readability: Will I understand this code 6 months from now?
- Dependencies: Any imports or libraries can remove?
- Size: Can this function/module split smaller? Should it?
- Coupling: If this code change, what other code break?
- YAGNI: Code added "just in case"?
- Value: What value does this code deliver to user?
Act of consciously run through these questions is itself the value.
  </simplicity_review>

  <task_type_detail title="OSL Applied Per Task Type">
New Feature:
1. Orient: summarize goal, current state, completion criteria
2. Pick one core user scenario → write minimal code make it work
3. Get feedback → if direction right, add next scenario
4. Summarize learnings after each step

Code Review:
- Only as complex as need to be?
- Dependencies justified?
- Tests reveal process bugs, or only catch code bugs?
- Can break into smaller units?

Refactoring:
Goal: not "better" but simpler.
- Orient: What is complex? Why?
- Step: Apply just one small simplification
- Learn: Easier to understand? Still works?

Debugging:
1. How fix this bug? (immediate)
2. Why occur? (root cause)
3. How prevent this class of bug from recurring? (process improvement)
Record answer to third question.

Technology Selection:
- Evaluate reversibility — prefer easily reversible decisions
- List trade-offs explicitly
- "Both probably half right and half wrong" — seek synthesis
  </task_type_detail>
</component>