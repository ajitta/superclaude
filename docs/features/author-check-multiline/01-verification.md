---
feature: author-check-multiline
phase: verification
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 01. Verification — author-check multiline consumers

Branch fix/author-check-multiline from master 02f31d7b. Intent commit 252d37b7; fix commit a1d6ca7a. Headless behavioral sessions used: **0** (owner cap 0).

## Change (`src/superclaude/cli/author_check.py`)

| Site | Before | After |
|---|---|---|
| `infer_format` | `TAG_RE.match(stripped)` on the first content **line** | `TAG_RE.match(masked, pos)` at the first content offset of the comment-masked body; a multiline match counts only when `_is_multiline_tag` accepts it; HTML-led bodies still return `md` |
| `_sentences` | `TAG_RE.sub(" ", line)` per line | `_blank_tags(body)`: every tag blanked character-for-character except newlines (same shape as `_mask_comments`), multiline matches only when `_is_multiline_tag` accepts them; per-line prefix stripping, sentence split and `_normalize` unchanged |
| new `_is_multiline_tag(body, match)` | — | the match starts a line (only whitespace before it) and every continuation line is attribute-shaped (`name="…"`, `name='…'`, `name=bare`, repeated) optionally ending in `>`/`/>`, or the bare closer; quoted values are collapsed first so a value may span lines |

Untouched: `TAG_RE`, `_STRUCT_RE`, the X1/X2 scan, `is_placeholder`, `closed`/`is_void`, capture groups, rule codes.

## Reproductions before → after (sandbox, `check()` without `--format`)

| Case | Before (02f31d7b) | After (a1d6ca7a) |
|---|---|---|
| `<component\n  name="x"\n  type="agent">\n<flow>\n- Do the thing.\n</component>` | `infer_format` → `md`; findings `[]` (false clean; `--format xml` gave `X2 line 4 "<flow> is never closed"`) | `xml`; `X2 line 4` (line 7 behind a 3-line frontmatter) |
| `<guide>\n<step\n note="x">Run the full test suite before every commit.</step>\n</guide>` with `--with other.md` holding the sentence | no N4; extracted sentence `notexrun the full test suite before every commit` | `N4 line 3` (line 6 behind frontmatter) |
| Control: same with a single-line `<step note="x">` | `N4 line 2` | `N4 line 2` |
| Control: `<div\n  align="center">…</div>\n# Title` | `md`, no X-codes | `md`, no X-codes |
| Control (reviewer hazard): Markdown ``Use the `<agent-message ` prefix.`` / duplicated sentence / `> quoted` | `N4 line 4` | `N4 line 4` — the cross-line `TAG_RE` match is rejected by the placement rule |
| Control: `infer_format("<custom-note is a term we use\nfor things.\n> quoted\n# Title")` | `md` | `md` |
| Control: duplicates on lines 2 and 6 around a multiline `<step\n note="a"\n other='b'>` | — | `[2, 6]` |
| Control: ≥5-word sentence inside a multiline `note="…"` attribute | not extracted (the tail glue made it a different string) | not extracted (the tag is blanked) |

The reviewer's prediction that the attribute-text case would be red on HEAD was wrong — it passes on both sides for different reasons; it is recorded as a control.

## Deterministic evidence (red → green)

`git stash push -q -- src/superclaude/cli/author_check.py` → run → `git stash pop -q` → run.

| Suite | Implementation stashed | Implementation |
|---|---|---|
| `TestMultilineTagConsumers` + `test_corpus_bodies_infer_as_xml` | **9 failed, 63 passed** — `infer_format_multiline_first_root` ×4 (`md`), `auto_format_reports_x2_after_multiline_root` ×2 (`[]`), `n4_sees_sentence_after_multiline_opener` ×2 (`[]`), `multiline_tag_predicate` (no such helper); the four controls and all 61 corpus cases passed | all pass |
| `tests/unit/test_author_check.py` + `tests/unit/test_author_check_corpus.py` | — | 343 passed |

## Whole-tree diff gate

Script over `git ls-files '*.md'` (559 files): `check(p)` and `check(p, fmt="xml")`, findings as `(mode, code, line, message)` per file, snapshot on 02f31d7b vs a1d6ca7a. **3,892 findings before, 3,892 after, 0 files differing.** Consistent with 0 multiline openers in the tree; any difference would have been a bug in the placement rule.

## Integration checks (repo root)

| Check | Result |
|---|---|
| `uv run --no-sync pytest -q` | 3727 passed, 4 skipped |
| `uv run --no-sync ruff format --check src tests` / `ruff check src tests` | clean |
| `git diff --name-only \| xargs file \| grep -i crlf` | empty |
| `tests/unit/scripts` | not re-run: no file under `src/superclaude/scripts/` changed |

## Closed by decision, not measurement

No model session was spent; the checker is deterministic and the whole-tree diff is the behavioral oracle for shipped content. The reading "document the one-line limit instead" (plan §1.4 B) was rejected because it would pin a false clean after the previous round had already widened the tag grammar.
