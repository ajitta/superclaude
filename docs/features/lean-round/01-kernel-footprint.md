---
feature: lean-round
phase: intent
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# Phase 0: always-loaded kernel footprint

Measured on 2026-10-18 at base `30a08be3` (v4.28.0), branch `fix/lean-round-2`, before implementation or installed-content changes. Read raw UTF-8 bytes and decoded character counts using `uv run --no-sync python` and `pathlib.Path`; source files were not modified.

`src/superclaude/CLAUDE_SC.md` contains exactly three imports:

- `@core/FLAGS.md`
- `@core/PRINCIPLES.md`
- `@core/RULES.md`

| File relative to `src/superclaude/` | UTF-8 bytes | Decoded characters |
|---|---:|---:|
| `CLAUDE_SC.md` import stub | 50 | 50 |
| `core/FLAGS.md` | 5,172 | 5,115 |
| `core/PRINCIPLES.md` | 2,169 | 2,157 |
| `core/RULES.md` | 5,925 | 5,894 |
| Imported content only | **13,266** | **13,166** |
| Including import stub | **13,316** | **13,216** |

Character-count heuristic: imported content is 13,166 / 4 = **3,291.5 estimated tokens**. This is not a tokenizer measurement or total session input. The import stub is counted separately so import directives are not confused with loaded rule content. On-demand modules, hooks, component catalogs, user/project instructions, and conversation context are excluded.

The [earlier baseline](../reframing-anchoring/01-baseline.md) recorded 12,083 imported bytes (FLAGS 5,172 + PRINCIPLES 2,169 + RULES 4,838). Current imported content is 1,183 bytes larger; this comparison is footprint only and does not establish a performance change. RULES was subsequently changed for the [purpose-inference pilot](../reframing-anchoring/06-pilot.md).

No new headless evaluations were run in Phase 0: **0/40 sessions used**. The earlier five-canary baseline was at ceiling and cannot justify deleting instructions as behaviorally redundant. New dry-run and real evaluation results belong to the later verification batch; no such result is claimed here.
