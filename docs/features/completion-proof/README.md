---
feature: completion-proof
phase: implementing
owner: ajitta
created: 2026-10-20
updated: 2026-10-20
related: ../../research/superclaude-weakness-audit-ajitta-2026-10-20.md
---

# Completion proof, spec-gate isolation and the first multi-step probes

The round applies N1–N6 from the [weakness audit](../../research/superclaude-weakness-audit-ajitta-2026-10-20.md), revised after its [independent verification](../../research/superclaude-weakness-audit-verify-ajitta-2026-10-20.md). In short: a plan reaches `complete` only after its Proof ran at the current commit; the spec-gate review runs isolated and gets the original intent; README stops calling prose gates hard; brainstorm's decision-mode heuristic gets a default; two probes measure contracts between commands for the first time.

## Documents

- [00-prereg.md](./00-prereg.md): pre-registered rules for the two probes, written before any run
- [06-verify.md](./06-verify.md): independent verification (opus high), PASS WITH FIXES, S1 1 / S2 3 / S3 8; applied below
- [01-readout.md](./01-readout.md): results — both probes at ceiling on sonnet low (10/10 before and after N2; gate 10/10); after the verification fix every `Result:` line names the tested code commit (10/10)

## Verification applied

| Finding | Applied |
|---|---|
| F1 (S1) `Result:` sha not executable as written | `implement.md` Integrate: commit the code, run the Proof on that clean HEAD, record `Result: <that sha>` in a docs-only commit. `RULES_DOCS.md` plan condition now names "the last commit that changed code". Re-measured descriptively (01-readout, "After verification"); `make canary-gates` re-run. |
| F2 (S2) readout miscounts | 01-readout: 5 of 8 `Result:` lines named the baseline; B decision point reached 8/10. |
| F3 (S2) decision modes misclassify choices with a particle, pass rejections | `brainstorm.md`: label with a choice word or particle in any language counts; label words in a rejecting or evaluating context pick nothing. Shipped content stays English, so the Korean examples are described, not quoted. |
| F4 (S2) two grader mutations survived | `test_eval_harness.py`: task-not-done and an edited frozen test now fail the grade; both mutations re-checked red. |
| F5 (S3) earlier sentence and split plans | Index closes "when its last box is checked and its Proof has run"; the `RULES_DOCS` Proof clause applies to the plan (index). |
| F6 (S3) red Proof `Result:` unclear | A red or unrunnable run is recorded the same way. |
| F7 (S3) red re-run after `complete` | Sets the plan back to `implementing`; README `phase:` stays. |
| F8 (S3) `workflow_gates` SSOT | `/sc:implement -> /sc:review --scope branch (Large; optional for Medium) \| /sc:test`, with the Proof condition. |
| F9 (S3) N4 rule only in tools | Moved into the Gather step; the tools entry points to it; no feature folder → no intent file. |
| F10 (S3) CHANGELOG "before and after" | Fixed per probe. |
| F11 (S3) README chain labels, step table wording | Labels swapped back; table uses "code change after the `Result:` sha" / "last code commit". |
| F12 (S3) prereg frontmatter, readout time | Frontmatter to `{status, revised}`; body unchanged; readout says session start 17:00:15. File name kept (already cited). |
| Outside: `self-review` `memory: project` | Noted in 01-readout Limits as a future N4 probe item. |
