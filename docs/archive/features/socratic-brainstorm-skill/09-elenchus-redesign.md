---
status: complete
revised: 2026-10-02
---

# 09 — Redesign: from "Socratic questioning" to the elenchus

## 1. Why v1 was wrong

v1 (1.0.0) called itself Socratic but ran something else:

- **Six question types**: that taxonomy is Richard Paul's modern "Socratic questioning" from critical-thinking pedagogy. It does not come from the dialogues.
- **Diverge → converge with model options**: that is Osborn's brainstorming, which defers judgment. The elenchus judges at every step.
- **Contradictions were waited for, not constructed.** v1 surfaced a collision only if two answers happened to clash.
- **The "What is X?" question was one tactic among many**, although it is the core of the early dialogues.
- **Aporia was one of three verdicts**, although it is the usual ending.

The user caught this ("소크라테스의 대화법은 그게 아닐텐데") and chose to rebuild the core as elenchus (option a).

## 2. What the method is (sources)

All references are to Plato. Text was checked against Perseus (Lamb/Fowler translations) where a line is cited in SKILL.md.

| Element | Where | In the skill |
|---|---|---|
| "What is X?" seeks one form common to all cases, not examples | Euthyphro 5d, 6d-e; Meno 72a-c | Step 1-2 |
| Counterexample to a definition (too narrow) | Laches 190e-191c: courage as standing your ground vs the Scythians who fight retreating | Step 3 |
| Premises get the answerer's agreement, one at a time; short answers | Protagoras 334c-335c | Rules 1-2, Step 3 |
| Say only what you believe; sincere assent | Crito 49c-d; Gorgias 495a | Stance |
| Agreed premises contradict the thesis → revise | the standard elenchus as reconstructed by Vlastos, "The Socratic Elenchus" (1983) | Step 4-5 |
| Socrates disclaims knowledge | Apology 21d | Stance |
| Aporia as gain: knowing you don't know | Meno 84a-c; Theaetetus 210b-c | Step 6 |
| Midwife: the questioner has no offspring of his own; he tests whether the other's offspring is real or a wind-egg | Theaetetus 150b-151d, 157c-d | Intro, Step 5 |

## 3. How it stays a *brainstorm*

The ideas come from the revisions. Each time a definition falls, the user states a new one, and the move between them is a direction they had not stated before ("고민 없음 → 질리지 않는 선택 → 같이 먹는 사람 취향"). The record lists these births. The model contributes no ideas during the dialogue. Advice is available only after the dialogue ends, on request, labeled as the model's and as not Socratic.

## 4. What changed (2.0.0)

| v1 | v2 |
|---|---|
| Frame: mode (develop/stress), depth (quick/standard/deep) | Removed. The method has one shape. |
| Steelman the idea | Find X, the concept the idea stands on, and ask what it is |
| Six question types + tactics | Premise questions aimed at the definition: too broad, too narrow, stated goal, consequence |
| Contradiction surfaced if it appears | Contradiction constructed from agreed premises and laid out as ①②→ |
| Step 3 Diverge: user options, then ≤3 model options | Removed. Revisions are the ideas; model options only after the dialogue, on request |
| Step 4 Converge: criteria, confirmed/delegated | Removed |
| Verdict sharpened / open / refuted | aporia / holding (provisional) / stopped before testing |
| `question-bank.md`, `brief-template.md` | `elenchus-patterns.md`, `record-template.md` |

Kept: one ask per message (the compound-ask rule found by v1 probing), short phone turns, quote only real words, stop signals, explicit-only invocation, spec-only frontmatter.

## 5. Distribution

`portable-skills/releases/socratic-brainstorm.zip` is now committed (the user asked for it in git). `dist/` is gitignored, so the packager writes to `portable-skills/releases/`. The zip is byte-reproducible (fixed timestamps and modes), so rebuilding with no source change leaves git clean. `test_committed_zip_matches_source` fails when the committed zip lags the source; the mutation check (append a line to a reference, rerun) failed as expected and passed after reverting.

## 6. Probes

Two scripted dialogues, the same user lines on both engines. Claude Code 2.1.284 / Sonnet 5.5 (`claude -p --resume`); Codex CLI 0.158.0 / `gpt-6.1-sol` (`codex exec resume`). n = 1 per cell per round; these record what happened.

- **lunch:** the user defines "좋은 추천" as "고민 안 하게 해 주는 거", then revises it twice.
- **retro:** the user opens with "너라면 어떻게 할 거야?", gives an example instead of a definition, and gets confused near the end.

**Round 1** (first v2 text):

- **Claude:** found X and asked "무엇인가요?". Broad counterexample (same menu every day). Laid out ①②, asked "어디를 고칠까요?", named each shift. In retro it declined the advice request and offered to switch to advice. Defect: the result labels were invented ("아직 시험 중", "중단 (미검증)").
- **Codex:** spent turns re-confirming ("~라는 뜻인가요?") instead of probing. In retro it **wrote the revised definitions for the user** ("…시간이라고 보면 될까요?"), which is the midwife delivering the baby. It also could not read the reference files: on this VM, Codex's bwrap sandbox fails (`loopback: Failed RTM_NEWADDR`), so it printed an improvised record and said why.

**Fixes:**

- The definition is restated as a statement in the same message as the first premise question; a confirm-only turn is forbidden.
- If the user's answer already conflicts with the definition, lay out the contradiction in the next message.
- "The user writes the revised definition, not you": never offer one for approval.
- Exactly three result labels (aporia / holding / stopped before testing); print all template sections.

**Round 2** (current text; Codex run with `--dangerously-bypass-approvals-and-sandbox` so it can read the references, which is the normal case on a working sandbox):

| | lunch | retro |
|---|---|---|
| Claude | X found → restatement + premise in one turn → ①② contradiction → user's revision → shift named + next premise → second ①② contradiction → **aporia**, full template | Declined to advise, offered the switch. Pushed for a definition, not an example ("그건 예시네요… 무엇 때문일까요?", Euthyphro move). Too-broad counterexample on the user's revision (sprint planning also decides changes). Answered the confusion by explaining the link, then one goal-check premise. Result **stopped before testing**, full template |
| Codex | Same shape as Claude: restatement + premise, contradiction, "어디를 고칠까요?" ×2, no definitions offered. **aporia**, full template | Restatement + premise; contradiction laid out; shift named + next premise; goal-check premise after the confusion. **stopped before testing** |

**Remaining imperfection:** in Claude retro turn 3, the model summarized "회고는 무언가를 바꾸는 일이네요" from an answer that was a premise, not a definition. That is a light form of writing the definition for the user. Recorded here; no further fix because one more rule risks making the dialogue stiff.

## 7. Environment note

Codex `-s read-only` on this VM can't run shell commands (bwrap needs netlink permission the OCI kernel/container denies). The skill still works there, because the core rules are in SKILL.md, which Codex reads from its own context, but the reference files are unreachable. On a normal workstation the sandbox works.
