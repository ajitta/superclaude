---
status: complete
revised: 2026-09-30
---

# 09 — Follow-ups: interim retirement, CI, okf, unverified behaviors

Work done after [08-implementation.md](./08-implementation.md), covering the open items listed after 4.17.2.

## 1. Interim Opus 5.5 text retired (4.18.0)

**Trigger met.** Registered `anthropics/skills` as a marketplace in a fresh `CLAUDE_CONFIG_DIR`. The clone landed at `8a1541c` and holds both `## Migrating to Claude Opus 5.5` (L1867) and `## Migrating to Claude Sonnet 5.5` (L2072).

**Change** (`commands/prompt.md`, `scripts/context_loader.py`):

- The `interim (Opus 5.5 prompting guide)` marks are now plain `(Opus 5.5 prompting guide)` source marks. They hold guide-only facts the reference section does not carry, such as the unattended-run paragraph. Like every mirror row, they yield to the reference on conflict.
- **Fallback, one rule for every target.** If the reference lacks the target's section, the target's mirror column carries the rewrite, and the report says the section was missing. Reading "the nearest earlier section" is gone. The Opus 5 section carries the `high` default that Opus 5.5 retired, and the Sonnet 5 section carries effort advice the Sonnet 5.5 section replaces.
- `facts-not-memory` now lists two exceptions, not three. The `<bounds><fallback>`, the `opus55` example and the hook note (`context_loader.py`) all state the single rule.
- `max_tokens`: the reference's Opus 5.5 section says 64K "has worked well" for long agentic coding turns, and the guide says 128,000. Both are cited, with "cite the section read".
- **New.** When the hook note says no reference is on the machine, the command stops searching. Probe K1 showed why: told "no reference", Opus 5.5 ran `find /` and read another scratch project's copy.

## 2. CI repaired

Dispatching `Tests` on master showed that all three pytest jobs pass. That includes the doctor-PATH unit test, which fails only on this VM. Two other jobs failed:

| Job | Cause | Fix |
|---|---|---|
| Pytest Plugin Check | grepped `pytest --fixtures` for `confidence_checker`, `pm_context` and similar fixtures, which were removed with pm_agent in `b8cd144` | grep `pytest --markers` for the four markers the plugin registers |
| SuperClaude Doctor Check | ran `superclaude doctor` on a fresh runner with nothing installed (3/6 checks failed) | `superclaude install --scope user --force`, then `doctor --scope user` |

Run `36678700864` on `fix/ci-plugin-doctor`: all 7 jobs green.

**VM note.** The local doctor-PATH failure disappears once the CLI is installed with `uv tool install --editable .` (`~/.local/bin/superclaude`). The full suite on this VM is now 2650 passed, 0 failed.

## 3. okf bundle re-synced

14 concept descriptions (3 agents, 10 commands, 1 output style) were re-synced from source frontmatter: frontmatter, body lead and index entry. A re-run of the drift check reports 0. Core, mode and MCP concepts have no source frontmatter and were left alone. Logged in `okf/superclaude/log.md`.

## 4. Behaviors not probed in 03a

Setup: `claude -p`, Claude Code 2.1.284, SuperClaude installed from this branch. Criteria were written before the runs (`criteria.txt` in the session scratchpad). n = 1–2 per cell.

### `/sc:prompt` fallback (after §1)

| Run | Setup | Result |
|---|---|---|
| K1 | `--model opus55`, no reference in the project | **Contaminated.** The hook said no reference. The model ran `find /`, found the K2 arm's copy in a sibling dir, and used it. This led to the §1 stop-searching rule |
| K1b | Same, after removing every other copy | Pass. Mirror Opus column; "reference isn't on this machine"; unattended-run `[FILL]` slot; double-check deleted with tests and build kept as done criteria |
| K2 | `opus55`, full reference `8a1541c` | Pass. Read `## Migrating to Claude Opus 5.5` and cited it |
| K3 | `opus55`, reference truncated before the 5.5 sections | Pass. "no Opus 5.5 section ... I didn't use the Opus 5 section as a stand-in" |
| K4 | Sonnet session, same truncated reference | Pass. "I did not read the Sonnet 5 section as a substitute, so the Sonnet 5.5 mirror column carries this rewrite" |
| K5 | Sonnet session, no reference, a decoy copy in a sibling dir, after the stop-searching rule | Pass. One tool call (Read `agent.md`), no disk search, "not on this machine" |

### Sonnet 5.5 at `--effort low` and `xhigh` (guide G2, G4, G11)

| Cell | SuperClaude | Bare |
|---|---|---|
| `low`, one-line `mul` (G11: skipped check) | 2/2 ran an import-and-call check | 0/2 ran any check ("I didn't run or test it") |
| `low`, 6-part task (G2: early check-in) | 1/1 finished all 6 parts, no check-in; ran pytest in a temp venv | 1/1 finished all 6 parts, no check-in; ran pytest in a temp venv |
| `xhigh`, 3-part task (G4: self-started review or subagents) | 1/1: no Agent spawn, no extra review round; cleaned up its temp venv and `__pycache__` | 1/1: no Agent spawn; exercised the CLI edge cases by hand |

**Readings:**

- G11 reproduces at `low` exactly as at `medium` (03a P-C), with the same kernel effect (2/2 vs 0/2).
- The guide's G2 early check-in and G4 self-started reviewer subagents did not appear on these task sizes.
- G10 (interactive mid-turn messages) still cannot be probed headless and stays open.

## 5. Still open

- G10: an interactive Sonnet 5.5 session with SuperClaude hooks and a typed mid-turn message.
- G2 and G4 on long tasks (tens of minutes). The fixture tasks finish in under two minutes.

## 6. Second independent review (4.18.1)

A second `claude -p --model opus --effort high` reviewer (claude-opus-5-5, 50 turns, $3.67) checked everything after 4.17.0 in a disposable copy. Sections 08 §5 and this file were withheld from that copy. It found 2 high, 6 medium and 6 low defects. Each finding was re-checked against the code before it was acted on.

| # | Finding | Severity | Resolution |
|---|---|---|---|
| H1 | The hook searched only `claude_base()` and `~/.claude`. A user-scope SuperClaude beside a project-scope claude-api skill, or a `CLAUDE_CONFIG_DIR`, was reported as "no reference", and the §1 stop rule then forbade looking | high | New `migration_reference_roots()` searches the project `.claude`, `claude_base()`, `CLAUDE_CONFIG_DIR` and `~/.claude`. The note names those roots, and the rule now says "don't search outside `.claude` directories". Two tests added; the fake-HOME scenario was reproduced and now finds the project copy |
| H2 | `runner_unavailable()` searched the whole output with unanchored patterns. A real failure quoting "No module named pytest", a missing `pytest_asyncio` plugin, or `No rule to make target 'test-data.json', needed by 'test'` came back as "not run" | high | Each pattern must match a whole line. Any pytest session line (`collected`, the summary, `N passed/failed`) forces "tests ran", and exit 0 is never classified. The reviewer's `make test` case now reports "Tests FAILED" end to end |
| M3 | `npm test --silent` prints nothing when the script is missing, so the npm pattern never fired; the `npm init` placeholder script was reported as FAILED | medium | `package.json` is checked before running. A missing, empty or `no test specified` script means no command. Make's `` `test' `` quoting is accepted, `uv: not found` is classified, and pytest exit 5 reports "collected no tests" |
| M4 | The Sonnet self-check row said "replace", but the verification cell covered only prompts that change code, so non-code prompts had no rule | medium | The row now uses the same scope: on non-code prompts it deletes. Canary N1 (airline support prompt): "Removed, not replaced ... because that swap applies only to prompts that change code" |
| M5 | The `(Opus 5.5 prompting guide)` mark still covered the whole request config, most of which the reference carries | medium | The request config is now attributed to the reference's Opus 5.5 subsections; the mark remains only on the unattended paragraph and the 128,000 figure |
| M6 | "Cite the section read" pointed at 64K/64,000 figures outside the range the hook names | medium | Both configs name the `### Breaking change 1` subsection to read. Canary N2: "`max_tokens`: 64,000, which the reference says has worked well ... The prompting guide gives 128,000" |
| M7 | The okf plain-language lead lost its sentence break (the source description has no final period) | medium | Restored |
| M8 | The CI marker check passed without the plugin, because `pyproject.toml` declares the same markers | medium | CI now checks the `SuperClaude: ` report header in `pytest --collect-only -q` output: 1 match with the plugin, 0 with `-p no:superclaude` |
| L9 | `04-design` resolution note claimed coverage that did not work | low | Rewritten to point here |
| L10 | The return-code guard was untested (mutation M2 survived) | low | `test_success_is_never_classified`. Six mutations of the hook are now all caught |
| L11 | Narration row cited only the guide | low | It now cites the guide and the reference section |
| L12 | A model section without a shifts heading borrowed the next model's range | low | The search is bounded to the model's own `## ` section. Test added; mutating back to an unbounded search makes it fail |
| L13 | Blank-line nits | — | Not in the real repo; an artifact of how the review copy was stripped |
| L14 | Missing `uv`, and pytest exit 5, reported as FAILED | low | Covered by M3 |
| Other | The feature README and 08 still said the interim text stays | low | Updated |

After the fixes: 2671 passed, 25 skipped, 0 failed; ruff is clean; the mirror table is still 13 × 4; `migration_reference_ranges()` on the 8a1541c reference is unchanged.
