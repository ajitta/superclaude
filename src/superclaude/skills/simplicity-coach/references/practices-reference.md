<component name="practices-reference" type="reference" parent="simplicity-coach">
  <meta>Referenced from SKILL.md — detailed templates for practices and task types</meta>

  <dependency_gate title="Question Your Dependencies">
Dependency Gate questions + justification criteria: see assets/dependency-audit-checklist.md (SSOT). Import tens of thousands of lines for 3-line function = install time bomb.
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
</component>