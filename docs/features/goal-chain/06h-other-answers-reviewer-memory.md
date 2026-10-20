---
status: draft
revised: 2026-10-20
---

# Follow-ups after 4.34.0: answers in the user's own words, reviewer memory

The two items [06e](./06e-ask-checkpoint.md) and [06g](./06g-ask-review-applied.md) left open, with the owner's rulings (both the ★ option of [remaining-work-ajitta-2026-10-20](../../plans/remaining-work-ajitta-2026-10-20.md) §0).

## 1. Answers in the user's own words count as `confirmed`

Problem: `/sc:brainstorm`'s decision modes had no rule for an answer outside the listed options (the form's Other text, or a sentence of the user's own). It fell to "When neither rule clearly applies, tag delegated", so `/sc:review --audit-delegated` re-decided it between models and the user's own choice could be overwritten ([06f](./06f-verify-ask.md) finding 3 and its note outside the branch; run 24's `D3 기타: …` answer in 06e).

Ruling (a): a reply in the user's own words that commits to one concrete choice is `confirmed`. The record holds the option it names, or its own text when it names none. A question, a hesitation or a condition ("not sure, maybe b?", "b if it is cheap") picks nothing and stays `delegated`.

Changed:
- `commands/brainstorm.md` `<decision_modes>`: the confirmed rule gains the own-words case and the hesitation case.
- `commands/intent.md` Checkpoint step: the exception "an Other text … even where the /sc:brainstorm Decision-mode tag step would say delegated" is gone, because brainstorm's rule now covers Other texts. One case is still the Checkpoint's own: naming the ★ in reply to that one question ("D2 추천" in chat after a declined form). Brainstorm's rules leave it delegated, because a blanket "as recommended" must stay delegated. A ★ picked in the form is confirmed under brainstorm's rules anyway, since the form returns the option's label.
- One consequence: before, any Other text in the Checkpoint form was `confirmed`. A hesitant Other text ("잘 모르겠는데 아마 b?") is now `delegated`, as the ruling asks.

The decision-mode probe stays deferred ([remaining-work](../../plans/remaining-work-ajitta-2026-10-20.md) §4a). Its case list now includes an Other text naming a new choice and a hesitant one.

## 2. Independent reviewers keep no memory

Problem: in run 28 (opus, 06e) the `self-review` agent, reviewing the branch, wrote `.claude/agent-memory/self-review/review_patterns.md` into the user's repo. The folder stayed untracked, and `--through` asked before deleting it. Every agent shipped `memory: project`, which a project install keeps and which stores memory at `.claude/agent-memory/<agent>/`. The canary workspaces ignore that path (`WS_GITIGNORE` in `evals/run_eval.py`), so the probes' clean-tree check never saw it.

Two facts from the current Claude Code docs (sub-agents → "Enable persistent memory"), checked before the ruling:
- `project` memory is meant to be shared through version control. `local` (`.claude/agent-memory-local/`) is described as memory that "shouldn't be checked into version control", but the docs do not say Claude Code ignores it in git. Other repos add it to `.gitignore` by hand, so option (b), `memory: local` for reviewers, would still leave an untracked folder.
- With memory enabled, Claude Code adds Read, Write and Edit to the agent. That is how `self-review`, whose `tools` are `Read, Grep, Glob`, could write a file. `verifier` checks that no project file changed and lists new untracked paths, yet its own memory folder would be one.

Ruling (a): `self-review` and `verifier` carry no `memory` field and no `<memory_guide>`. A stored verdict would reach their next review of the same work, which is the independence risk §4a N4 noted. The other three agents (`business-panel-experts`, `deep-researcher`, `repo-index`) keep `memory: project`.

Changed:
- `agents/self-review.md`, `agents/verifier.md`: `memory: project` and `<memory_guide>` removed.
- `.claude/rules/agent-authoring.md` § `memory` and `src/superclaude/agents/README.md`: the reviewer exception and its reason. The installer needed no change: `_rewrite_agent_memory_scope` replaces the first `memory: project` line and leaves a file without one as it is.
- Tests: `test_agent_structure.py` has `NO_MEMORY_AGENTS`; for those agents it requires the field and the section to be absent, and checks the names exist. `test_cli_install.py::test_install_leaves_independent_reviewers_without_memory` installs at user scope and checks both reviewers have no `memory:` line while `deep-researcher` gets `memory: user`. Mutation check: with `self-review.md` restored from `master`, the install test and `test_has_required_field[self-review-memory]` fail.
- Probes `intent-through-branch` and `intent-through-ask-headless`: a new check after the clean-tree one fails when any file sits under `.claude/agent-memory/` or `.claude/agent-memory-local/`. An empty directory, which install creates, passes. `test_eval_harness.py` grades two new end states: a memory file hidden from `git status` the way `WS_GITIGNORE` hides it (only the new check fails), and an empty memory directory (all pass).
- Upgrade, checked end to end: a `master` install at user scope into a scratch `CLAUDE_CONFIG_DIR`, a hand-written `agent-memory/self-review/MEMORY.md`, then `update` from this branch. Both reviewers lost their `memory:` line, `deep-researcher` kept `memory: user`, the user's memory file stayed, and `verify-drift` reported no drift.

Memory an earlier release already wrote stays where it is. Nothing deletes a user's files.

## Limits

- The own-words rule is wording only. No probe answers a question with an Other text: a headless run cannot answer a form, and the decision-mode probe is deferred.
- The memory check covers the two `--through` probes. Other probes still ignore `.claude/agent-memory*/` through `WS_GITIGNORE`, because the three agents that keep memory may write there.
