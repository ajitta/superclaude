---
feature: reframing-anchoring
status: complete
revised: 2026-10-17
---

# 05. Restructure alternatives and decision boundary

## Decision record (2026-10-17, owner, in chat)

| Question | Decision | Applied |
|---|---|---|
| Q1 prerequisite repairs | Approved as recommended: source + tests only, installed configs untouched, other lean cuts excluded | Hooks print nothing on allow (`destructive_guard`, `loop_guard`, `file_size_guard`); `merge_hooks_to_settings` refuses a non-object settings file; `context_loader` caches only delivered contexts and matches triggers on the scannable prompt; `context explain` mirrors it. 12 new tests, red→green; CHANGELOG `[Unreleased]`. |
| Q2 direction | Alternative 4 as recommended: one thin common transition in the kernel, measured before anything ships | Trial rule `purpose_before_action` lives in `evals/arms/RULES_CANDIDATE.md` (shipped `RULES.md` + 1,056 bytes; `test_candidate_arm_is_shipped_kernel_plus_one_delta` pins the delta). New harness arm `sc-candidate`. `src/superclaude/core/RULES.md` is unchanged until the pilot reads out. Pilot: 2 I0 tasks × {sc-full, sc-candidate} × {sonnet, opus} × 3 = 24 sessions under the repaired hooks. **Result: 0/12 → 11/12** ([06-pilot.md](./06-pilot.md)). |
| Q3 deferred cuts | Deferred behind Q2 as recommended | No lean cut applied. |
| Q4 ship the rule to `core/RULES.md` | Approved as recommended (2026-10-17) | `123c6a22`: rule added, `scope_discipline` amended, candidate arm reset to shipped, CHANGELOG + ARCHITECTURE. `make canary-gates` 7/7 ([07-release-gate.md](./07-release-gate.md)). Merge/push/release on instruction. |

## Goal

Make the model distinguish the requested action from the outcome it is meant to achieve, seek relevant evidence, and check the result against that outcome. Do not turn inferred purpose into invented user intent or unauthorized scope expansion. Keep the framework smaller than an exhaustive workflow manual.

This is a comparison, not implementation approval. Verified audit synthesis: [03-analysis.md](./03-analysis.md). Measurement corrections: [02a-measurement.md](./02a-measurement.md).

## 1. Common prerequisite, not a blind deletion batch

Repair normal-hook auto-approval, invalid-settings overwrite, early context-cache commits and quoted-trigger injection. Keep those repairs separate from content behavior changes. Both experiment arms must use the same corrected execution/hook behavior. An installed-framework-versus-vanilla comparison remains useful for total-system behavior, but cannot isolate the effect of one content rule.

A/D classifications and ponytail lean estimates are proposed cuts, not a common automatically approved batch. First preserve semantics, routing and safety delivery. Do not mix catalog deletions or broad deduplication into the first purpose-inference experiment.

## 2. Four alternatives

| Alternative | What changes | Why it might help | Main cost or risk | Evidence today |
|---|---|---|---|---|
| **1. Targeted gates** | Keep core architecture; add a purpose/evidence transition only to implement, troubleshoot, analyze and other selected commands. | Smallest surface change; easy to compare one command path. | Ordinary requests and agent auto-routing can bypass it; repeated gates accumulate again. | I0 fixtures motivate trying it; no treatment test yet. |
| **2. Mechanism-first lean kernel** | Replace procedural kernel content with a small set of criteria-first, evidence-revision and isolation mechanisms; move specific workflow detail on demand. | Broad default reach; less generic procedure. | “Be skeptical” can replace “follow best practices” without fixing purpose inference; large rewrite mixes several causes. | Genuine isolation mechanisms already exist; A1/A4 treatment benefit not established here. |
| **3. Hook-enforced reminders/state** | Loader/session/compaction events inject checks and maintain re-entry state. | Mechanical delivery at chosen events; can reduce reliance on remembering a rule. | A reminder is not a hard behavioral guarantee; extra state, false triggers and loader failures. Main model has already seen the user prompt, so this cannot retroactively hide its anchor. | Existing loader has correctness bugs; no intervention evidence. Official event semantics still need verification if chosen. |
| **4. Intent-first, thin kernel** | One short common transition: action → evidence-backed purpose hypothesis → observable outcome → bounded action → verification. Selected commands provide domain-specific criteria; plans re-open only on invalidating evidence. | Directly targets the user's stated objective and reaches ordinary requests. | Wrong purpose inference, over-exploration, extra dialogue or scope creep if constraints are blurred. | Best fit to the I0 observation; effectiveness remains unmeasured. |

The alternatives are not all mutually exclusive: 4 is the objective layer; a small portion of 2 can deliver it, and selected parts of 1 can refine it. Compare them before combining, rather than claiming the combination is already validated. No option is adopted by default.

**Recommendation:** first test **4 with a thin common kernel**, not a whole-tree rewrite. If a common rule shows no reliable benefit, test a targeted command transition (1) rather than adding more compulsory prose. Defer 3 unless a concrete delivery failure remains after the loader repairs.

## 3. Candidate contract for alternative 4

This is a behavioral design, not final prompt wording.

1. **Separate known constraints from inferred ends.** Preserve the requester's words and explicit limits. Treat an unstated purpose as a hypothesis grounded in the request and observed context, not as an instruction from the user. A customer reply may aim at resolving a complaint; retention is not automatically the goal for every customer message.
2. **Discover the evidence needed to evaluate the action.** Before committing to the proposed means, inspect the relevant context needed to tell whether it achieves the result. A filename is an entry point, not proof that all relevant facts live there. Stop discovery when enough evidence exists; no fixed multi-file scavenger hunt for a simple rename or translation.
3. **Define an observable result.** For a sync incident: the local job succeeds and checks still pass, not merely “retry exists.” For a reply: feasible next steps and accurate dates, not merely “a polite email exists.” These are proxies; do not claim to have measured actual retention or satisfaction.
4. **Respect authorization.** Broader diagnosis is allowed within read permissions. Applying a broader change is not automatically allowed. Preserve explicit scope, security, privacy and destructive-operation gates. For a permitted, small local correction, state the interpretation when useful and proceed. If resolving the mismatch requires a new authorization, ask or return the exact blocker; headless mode is not permission to bypass it.
5. **Revise a plan on evidence, not discomfort.** If evidence invalidates the current means or criterion, revise the affected plan step and explain the boundary. After compaction or resume, re-check the purpose/constraint/next-step facts that matter; do not require a full fresh planning ceremony.
6. **Verify against the result.** Report what actually worked, what remains uncertain, and any gap between the action requested and outcome achieved. Do not expose hidden reasoning or force a purpose preamble on every response.

### Why “before receiving the anchor” needs a precise boundary

The main model already receives an anchor embedded in the user's initial request. A later instruction saying “consider your own criterion first” is an ordering request inside an already exposed context, not literal information isolation. Real pre-exposure isolation requires a fresh delegate/phase that does not receive the prior estimate or verdict. For now apply evidence/criterion-first before *additional* author rationale or prior-plan detail where practical, and distinguish that from actual blind review. Neither treatment has demonstrated benefit on these current-model fixtures yet.

### Preserve / change / do not add

- **Preserve:** verbatim `00-intent.md` provenance, user approval, destructive-operation protection, verification, and delegated review isolation.
- **Change candidate:** a separate inferred-purpose hypothesis and purpose-derived success check, plus a narrow evidence-invalidates-plan transition.
- **Do not add initially:** a new command family, universal intent file for every task, a compulsory clarification interview, a regex purpose classifier, or an automatic plan-rewrite hook.

## 4. Likely files and validation if chosen

First pilot: `src/superclaude/core/RULES.md`, possibly `core/PRINCIPLES.md` for a contradiction-free boundary; `evals/run_eval.py` and `tests/unit/test_eval_harness.py` only if a distinct candidate arm is needed. `sc-core-lite` currently replaces the kernel with its own file; it does not automatically represent a new arbitrary kernel design.

After evidence supports the pilot: `commands/intent.md`, `commands/implement.md`, `modes/MODE_Task_Management.md`, selected diagnosis commands and their tests. Keep inferred purpose separate from the requester's approved record; do not change all agent templates at once.

Test targets verified present:

- Safety/loader repairs: `uv run pytest tests/unit/test_safety_hooks.py tests/unit/test_file_size_guard.py tests/unit/test_loop_guard.py tests/unit/test_install_settings.py tests/unit/test_context_loader.py -q`.
- Harness changes: `uv run pytest tests/unit/test_eval_harness.py -q`.
- Content changes: `uv run pytest tests/unit/test_agent_structure.py tests/unit/test_command_structure.py -q`, plus the matching authoring-rule tests and `uv run superclaude author-check <changed file>` with co-loaded-file conflict checks.
- Integration: `uv run pytest -q`; scripts separately `uv run pytest tests/unit/scripts -o addopts=`; `uv run ruff format --check src tests`; `uv run ruff check src tests`.
- Before release after core changes: `make canary-gates`; count its selected tasks against the model-call ledger before launching. No Fable headless run, commit, merge, push or release without its required authorization.

Static section tests do not prove better intent inference. Preserve existing safety tests; do not relax them merely because a new prompt fails them.

## 5. Measurements and budget

Current usage is 144/180 headless sessions, leaving 36. No intervention has been tested yet.

Proposed first intervention allocation: **24 sessions** = two action-only I0 tasks × two arms (same corrected hooks, original content vs candidate content) × two models × three repetitions. This leaves **12 unallocated**. The original-versus-candidate comparison must be reproducible without overwriting previous run directories or substituting a different installed framework. Record source revision/diff, model identifiers, permission arguments, task IDs and run provenance. Do not spend the reserve automatically.

Before consuming those calls:

- Complete the focused current literature update and residual content coverage, without treating older prompting advice as current-model proof.
- Freeze scoring against the raw fixtures before looking at candidate outputs. Retain action completion and purpose proxies separately; audit false positives/negatives in the existing regex checks.
- Retrospectively exclude R3's contradictory format check from substantive conclusions. Do not create a new canary that demands disobedience to a valid explicit format request.
- Include negative behavior criteria (no unauthorized widening or commitments); enumerate their checks before implementation.

Three repetitions on two synthetic tasks is a pilot, not proof of generality or Fable performance. If the pilot does not support the candidate, report that and stop; do not add instructions until a favored result appears. Required release gates may need a separate allocation depending on their actual session count; request any cap change before running, not after.

## 6. Size and cost accounting

Baseline always-loaded chain is about 12.2 KB / 3.0k character-estimated tokens. Recorded total session input is larger under sc-full (sonnet +75.18%, opus +53.97% on the retained set); this is not a tokenizer measurement of prompt overhead.

Exact line/token deltas for alternatives do not exist before candidate wording is drafted. Report them as **not yet measured**, not invented forecasts. Aim for replacement rather than growth, but do not use a line target to remove a safety boundary. Catalog-wide repeated bytes are not bytes loaded per invocation. The raw ~5,000-line implementation and ~52-KB content cuts overlap and include routing changes; no net-saving total is approved.

## 7. Owner decisions

**Q1 — prerequisite repairs:** approve a source-only repair batch for the four verified safety/data/loader problems, leaving other lean cuts and installed configs untouched? Recommendation: yes, independently of the restructure choice.

**Q2 — direction:** choose which alternative to prototype, or continue design discussion before any behavioral edit. Recommendation: alternative 4 as a thin common transition, followed by the proposed 24-session controlled pilot. Alternatives 1, 2 and 3 remain available; no automatic selection.

These decisions do not authorize public component deletion, permission relaxation, modifying installed config, or any git commit/push. Remaining research/coverage can continue read-only within the already agreed audit scope.
