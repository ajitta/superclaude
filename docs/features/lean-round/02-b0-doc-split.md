---
feature: lean-round
phase: implementation
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# 02. B0 — size split of the oversized prior-round docs

Base: `fix/lean-round-2` at `30a08be3`. Eight files under `docs/features/reframing-anchoring/` exceeded the 25,000-byte target of `core/rules/RULES_DOCS.md` Size (two were above the 30,000-byte read guard). Each was split into `<stem>-1.md`, `-2.md` (`-3.md` where needed) with the text unchanged; the originals were removed and the folder README re-pointed.

## Method

A script (scratch, not committed) streamed each file and cut it only at a structural boundary — a `## ` heading preferred, then `### `, then a table row — so that no part exceeds 24,000 bytes. Added markup per part, and nothing else:

- part 1: one blockquote line under the H1 naming the parts;
- part N≥2: an H1 `<title> — part N of M`, one continuation line linking part 1, and — when the cut fell inside a section — `## <section> (continued)` plus the table's header and separator rows when the cut fell inside a table.

Check performed before writing: every original line appears, in order, in the concatenation of the parts (subsequence test); every part ≤ 25,000 bytes; LF only.

## Result

| Original (bytes) | Parts (bytes) |
|---|---|
| `03a-analysis-core.md` (29,284) | 19,635 · 9,970 |
| `03b-analysis-modes-skills.md` (51,346) | 23,442 · 22,295 · 6,320 |
| `03c-analysis-agents-first.md` (60,621) | 23,545 · 23,472 · 14,479 |
| `03d-analysis-agents-second.md` (59,121) | 23,555 · 23,101 · 13,369 |
| `03e-analysis-commands-first.md` (49,764) | 23,577 · 22,121 · 4,789 |
| `03f-analysis-commands-second.md` (37,089) | 23,374 · 14,184 |
| `04-ponytail-audit.md` (37,546) | 16,129 (§1) · 21,726 (§2) |
| `04b-ponytail-content-structure.md` (44,644) | 22,506 · 22,520 |

Links updated: `docs/features/reframing-anchoring/README.md` (document list), `docs/features/lean-round/README.md`. `03-analysis.md` cites the reports by letter (03a, 04b) without file links, so it needed no change. No other file in the repo linked the eight names (`rg` over the tree, excluding the files themselves).

## Naming note

`RULES_DOCS.md` Size describes a feature-doc size split as new `NNa-` letter siblings. The letters 03a–03f, 04a, 04b were already taken, and a fresh letter per part (03g = second half of 03b …) would hide which report a part belongs to, so the plan's `-1/-2` suffix was used instead. The owner can ask for a rename; the content is identical either way.
