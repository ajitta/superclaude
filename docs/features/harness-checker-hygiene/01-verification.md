---
feature: harness-checker-hygiene
phase: verification
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 01. Verification — retirement and quoted attributes

Implementation base: master 19a17705. The parent independently reran the regressions and checks below; worker summaries are not the verification oracle. Headless behavioral sessions used: **0** (no ceiling imposed).

## Candidate 2 — retire unused harness checks

Current YAML parse: 43 tasks, 160 checks, zero consumers of tool_called or parallel_tool_calls_min. The seven hard gates and the task definitions are unchanged. AST comparison against the base confirms the existing gate-flag, hard-gate-set and Makefile gate-task pin tests are unchanged.

Removed from evals/run_eval.py:
- The two dispatch branches and their exclusive TaskResult fields, tools_called and max_parallel_tool_calls.
- Generic tool-name collection and per-message counting.
- Only the optional res parameter of _check_one and its forwarding argument; _parse_stream and _run_checks still receive their TaskResult.

The two obsolete tests and exclusive helper were replaced with retirement rejection and actual report-write/readback coverage. The mixed Skill test now exercises Bash/PowerShell extraction, Skill success/error, activation attempts, refusal/usage/result subtype and _run_checks. It does not infer shell execution from prose.

Compatibility: new results.json rows omit the two retired fields. Retained report values are asserted exactly for success, refusal and error rows; existing result files and historical release/measurement records remain unchanged. No tracked external reader was found; external readers outside the repository are unknown. evals/README.md and the new CHANGELOG entry disclose this change.

## Candidate 3 — quoted-attribute tokenization

Only TAG_RE and its comment changed in author_check.py. Quoted single- and double-attribute spans are opaque, including literal opening/closing angle-bracket references and greater-than characters. Four capture groups, tolerant placeholder handling, HTML void elements and code/comment masking are preserved.

Regression cases assert whole token/capture groups (including self-closing), both quote forms/opposite quotes, single-line inferred XML and N4 stripping, explicit-XML multiline attributes, real unclosed/misnested/orphan-closing tags and frontmatter-adjusted line numbers. A targeted test checks the real RULES_DELEGATION.md in default and explicit XML modes; that source document was not edited.

Existing limits deliberately not expanded: multiline-first-root automatic format inference and multiline-tag N4 stripping. These are pre-existing line-oriented consumer limitations, not regressions introduced here; see the handoff.

## Parent red → green evidence

The parent temporarily stashed ONLY evals/run_eval.py and src/superclaude/cli/author_check.py after both workers finished, leaving the new tests in place. The original implementations produced **55 failed, 9 passed**, exit 1, across the retirement/schema tests and TestQuotedTagAttributes. The stash restored cleanly, exit 0; no unrelated state was stashed. Local raw output: .hermes/hygiene-parent-red.log.

- Harness retirement/schema cases: 5 original-code failures (two missing ValueErrors, three reports still carrying retired keys).
- Quoted-attribute matrix: 50 original-code failures and 9 already-passing controls.
- After restoration, the parent ran the five target suites together: **342 passed**.

Commands (all from the repository root):

```bash
uv run --no-sync pytest tests/unit/test_eval_harness.py::test_retired_check_types_are_rejected tests/unit/test_eval_harness.py::test_report_omits_retired_tool_metrics_preserves_retained_fields tests/unit/test_author_check.py::TestQuotedTagAttributes -q --tb=no
uv run --no-sync pytest tests/unit/test_eval_harness.py tests/unit/test_author_check.py tests/unit/test_author_check_corpus.py tests/unit/test_sc_author_skill.py tests/unit/test_sc_prompt_skill.py -q
```

The first command is expected red only against the base implementations. It is not a failure left in the final branch.

## Integration checks

| Check | Parent result |
|---|---|
| uv run --no-sync pytest -q | Final run after review coverage hardening: 3648 passed, 4 skipped; exit 0 (earlier run: 3642 passed, 4 skipped) |
| uv run --no-sync ruff format --check src tests evals | 237 files already formatted |
| uv run --no-sync ruff check src tests evals | All checks passed |
| author-check RULES_DELEGATION.md, default inference | 0 errors, 0 warnings; exit 0 |
| author-check RULES_DELEGATION.md, --format xml | 0 errors, 0 warnings; exit 0 |
| git diff --check | Clean |
| CR-byte checks | Zero on every changed file and initial lifecycle document |
| Source/task boundary | No diff in evals/tasks.yaml, fixtures, Makefile, core or scripts |
| Added-line security scan | No secret-assignment, shell=True/os.system, dynamic eval/exec or pickle hits |

The separate tests/unit/scripts suite was not run: no script file changed, as explicitly accepted in the plan. No model-effect inference is made from these deterministic results. No behavioral baseline, canary sessions or install sync was needed for the selected scope.

## Independent implementation review

Independent read-only review passed: no security concerns or logic errors. The reviewer traced all affected consumers and confirmed the deferred multiline limits remained untouched. One nonblocking coverage suggestion was accepted: a combined-attribute matrix entry now covers empty single/double quoted values, an unquoted value and whitespace before a self-closing delimiter. This added no production change; the checker target suites subsequently passed 304 tests.

## Commits

| Batch | Commit | Verification before commit |
|---|---|---|
| Intent | 5bff3e86 | 81 plan-checklist/version-consistency tests passed |
| Candidate 2 | 73d41ecb | Parent harness suite: 44 passed; make format/lint passed |
| Candidate 3 | 4c0a2c24 | Parent checker/corpus/skill suites: 304 passed; ruff and both CLI modes clean |

CHANGELOG entries were staged with their corresponding code batch, not postponed to the documentation commit. No unrelated file was staged.

## Approved conditions versus implementation

| Item | Approved condition | Actual | Revert cost |
|---|---|---|---|
| Candidate 2 | Remove unused checks and exclusive support; disclose JSON removal | Implemented within the three-file worker allowlist; parent owns CHANGELOG | Revert the harness batch |
| Candidate 3 | Quote-aware tokenizer only, four groups preserved, source instruction unchanged | Implemented within the two-file worker allowlist; infer_format/_sentences unchanged | Revert the checker batch |
| Multiline limits | Explicitly defer the two line-oriented consumers | Still deferred; explicit structural checks covered | No extra change to revert |
| Parallelism | Disjoint workers; shared writes/commits parent-owned | Followed | None |

No implementation deviation identified. The only post-review addition was the accepted test-only coverage hardening above; no extra behavior, model session or scope change was introduced.
