---
status: complete
revised: 2026-10-03
---

# 13 — Independent review and fixes

## 1. Setup

- **Reviewer:** a separate Claude Code run (`claude -p --model opus --effort high`) on a disposable clone. Base was `16b8fbd`, before this feature; the change under review was the whole feature.
- **Stripped before dispatch:** implementation records (08-12), self-verdicts in the README, and the history banners.
- **Sources:** official and third-party texts in `../sources/`.
- **Limits:** at most 8 live `claude -p` runs; no edits.
- **Run:** 53 turns, about $3.9. The reviewer also ran 7 Codex sessions on Codex 0.160.0.

## 2. Findings and fixes

Each finding was reproduced or re-checked before fixing.

| ID | Sev | Finding | Reproduced? | Fix |
|---|---|---|---|---|
| H1 | high | Codex registers a skill folder that contains `.claude-plugin/plugin.json` as `<name>:<name>`, so `$socratic-elenchus` does not resolve | **Partly.** On this machine with `gpt-6.1-sol`, `$socratic-elenchus` still produced the right first question. The session log shows why: without a registered skill, the model ran `rg`/`find` across the home directory and read the SKILL.md itself. The control (no manifest) and `$name:name` read the skill directly. The name was not registered; the model recovered by searching. | The manifest moved out of the source folder into `portable-skills/plugin-manifests/<name>.json`, and `package.py` injects it into the zip only. After the fix, Codex read `.agents/skills/<name>/SKILL.md` directly for both `$socratic-elenchus` and `$socratic-brainstorm` (session logs). |
| M1 | med | No test guarded Codex naming | yes | `test_codex_invocation_name_is_the_folder_name`: no `.claude-plugin/` or `.codex-plugin/` in the source, and the sidecar `default_prompt` uses `$<name>`. Mutation: putting `.claude-plugin/` back fails 2 tests. Changing `default_prompt` to `$name:name` fails 1. |
| M2 | med | README said `.claude/skills/` copies ignore the manifest; the Claude Code docs say such a folder loads as `<name>@skills-dir` after workspace trust | yes (`ccskills.md:158`) | Fixed by the same move: the source folders are plain skills again. README "Layout" section explains both effects. |
| M3 | med | `socratic-brainstorm` headings still said "Probe (elenchus)", "Diverge (maieutics)", "Open (aporia)": the framing the user rejected | yes | Headings renamed to Probe / Diverge / Open. 3.2.0. |
| M4 | med | Feature docs still described a one-skill design | yes | 04-design banner rewritten: what still holds, what was replaced and where. 11 marked superseded in part. 12 links here. |
| M5 | med | 02-research said "Customize › Skills" for the upload | yes | Row rewritten: the Help Center path at research time vs the working Plugins path. |
| M6 | med | Zip not byte-reproducible on Windows (`ZipInfo.create_system` is 0 on win32; CRLF checkouts) | yes | `create_system = 3`, and text files are normalized to LF before zipping. `test_zip_build_is_os_independent` monkeypatches `sys.platform = "win32"`. Mutation: removing the pin fails it. |
| L1 | low | Version check skipped when `metadata.version` is absent; regex matched `spec-version` first | yes | The frontmatter parser now reads `metadata` as a map. A missing version is an error. Tests cover a missing version and a `spec-version` look-alike. |
| L2 | low | Validator did not reject `skills/` or `bin/` in the folder (`skills/` voids single-skill loading; claude.ai refuses `bin/`) | yes | `FORBIDDEN_DIRS = skills, bin, .claude-plugin, .codex-plugin`; parametrized test. |
| L3 | low | "Early dialogues" overclaims: the midwife is Theaetetus, and the Meno passages are transitional | agree | The description says "Socratic dialogues". The intro names the early dialogues as the method's home and marks Meno/Theaetetus as aids. "Wind-egg" is cited at 151e. |
| L4 | low | Two "Find X" examples weren't "what is X?" questions; a live run asked two forms in one message | yes | Examples rewritten as "what is a good retrospective?" and "what is open to everyone?". Step 1 says to ask exactly one "X란 무엇인가요?" form. |
| L5 | low | Restating without confirmation lets the refutation hit the model's paraphrase; "every later message is a premise or contradiction" ruled out example-forcing and pushback handling | agree | The restatement must keep the user's key words, or flag "제 말로 옮기면". Messages after the first may also force a definition or answer a pushback. |
| L6 | low | Result labels left a gap (one test passed, then stop); "To check" not in the template; Korean title in an English template | yes | Added **partly tested**. "To check" is now a template section. The title is English and gets translated like the other headers. |
| L7 | low | Brainstorm's ~6-line cap conflicts with numbering all options; brief list omitted Criteria and Not tested | yes | The options message may exceed the cap, with one line per option. Both sections are now named in Step 5. |
| L8 | low | Stale file:line citations in 02-research §1 | yes (re-grepped) | Corrected to current lines. |
| L9 | low | Broken `related:` path in the feature README | yes | `../../../portable-skills/README.md`. |
| L10 | low | Codex budget stated as "2% / 8,000 chars" | yes | "~2% of the context window (8,000 chars only when the window is unknown)" in 02 and 03. |
| L11 | low | README said "Yes" for Codex cloud tasks; 02 tags it INFERRED | yes | README says "Probably … inferred …; not tested". |
| L12 | low | Invoke table missed the synced (claude.ai upload) name | partly | Row added: listed under `claude.ai sync`; the full name may carry `anthropic-skills:`. Not verified here. |
| obs | – | Elenchus changed a quoted ending ("의미가 없다" for "의미 없지") | agree | Rule 4 now names this case: the ending counts, so change nothing inside quotes or drop the quotation marks. |
| obs | – | One brainstorm run picked `develop` although money was mentioned | noted | Not changed: n = 1, and the mode is stated with a reason so the user can override. |

**Unsupported-by-sources** (the reviewer's list): the plugin-upload manifest requirement, the mobile upload screen, and the Paul attribution. The first rests on claude.com/docs/plugins/build and the user's real error message (11). Neither was in `../sources/`; claude.com/docs is the source. The mobile items are the Help Center article and a community report, labeled as such in 02. The Paul attribution is standard (*Critical Thinking*, Paul & Elder) and stays.

## 3. Verification after fixes

- `package.py`: both skills ok. The zip contains `<name>/.claude-plugin/plugin.json` with the matching version, and the source folders have no `.claude-plugin/`.
- `claude plugin validate` on the unzipped release: passed. Loaded with `--plugin-dir`, it registered `socratic-elenchus:socratic-elenchus` and ran.
- Codex (`gpt-6.1-sol`, folders in `.agents/skills/`): `$socratic-elenchus` → "좋은 점심 메뉴 추천이란 무엇인가요?"; `$socratic-brainstorm` → asked for the idea in a sentence or two. Session logs show a direct `cat .agents/skills/<name>/SKILL.md` and no search.
- Claude Code with `.claude/skills/` copies in a fresh repo: `/socratic-elenchus …` opened with "좋은 추천이란 무엇인가요?".
- Marketplace: no `plugin.json` sits in the source folder any more, so the marketplace entry is the manifest. Each entry now carries `version`, and a test pins it to SKILL.md.
- Tests: `test_portable_skills.py` 21 passed. Mutation checks: manifest back in source, `create_system` pin removed, marketplace version drift, wrong sidecar name. Each failed its guard and passed after restoring.

## 4. Not verified

- The claude.ai upload of the current zips, and the mobile app. The reviewer found indirect evidence that an earlier upload succeeded: this account's sync manifest lists both skills with `source: plugin` at 3.0.0 / 1.0.0.
- `~/.claude/skills/` and trusted-workspace loading (no longer affected, since source folders carry no manifest).
- Codex cloud tasks and the ChatGPT desktop app.

## 5. claude.ai upload result (user, 2026-10-03)

- Customize › **Skills** rejected the 3.2.0 / 1.2.0 zip: "a skill cannot contain a plugin manifest. remove it or upload this content as a plugin".
- Customize › **Plugins** installed it.

The two screens have opposite rules: Plugins requires the manifest and Skills forbids it. The Plugins path is the documented one, and it works, so no separate skill-only zip is shipped. The README now names the screen and quotes the Skills error.

## 6. claude.ai marketplace skipped both plugins (user, 2026-10-03)

The user added `ajitta/claude-plugins` in claude.ai and got install errors for the two Socratic entries, and they were skipped. Cause: after §2 moved `plugin.json` out of the skill folders, the catalog's `git-subdir` sources pointed at folders with no manifest. Claude Code installs such a folder, with the marketplace entry acting as the manifest (verified in §3). claude.ai's marketplace does not; like Upload plugin, it needs `.claude-plugin/plugin.json`.

Fix: `package.py` now also writes `portable-skills/plugins/<name>/`, a committed copy of the skill folder plus the manifest. Both marketplaces point there. The test `test_plugin_dir_matches_skill_plus_manifest` requires the copy to equal the skill folder plus the manifest byte for byte; appending a line to a SKILL.md fails it. The skill folders stay manifest-free for Codex. Marketplace entries no longer carry `version`, because `plugin.json` owns it.

## 7. Catalog listing withdrawn (user decision, 2026-10-03)

The claude.ai marketplace still would not install the two entries from `ajitta/claude-plugins` after §6. The user dropped the catalog route, and the entries were removed (claude-plugins, commit "revert: drop the socratic entries"). These install paths remain:

- claude.ai: Upload plugin with `releases/<name>.zip` (user-confirmed working)
- Claude Code: `/plugin marketplace add ajitta/superclaude`, then `<name>@ajitta-socratic` (verified end to end)
- Codex: copy the folder into `.agents/skills/`

Not established: why claude.ai rejected the `git-subdir` entries. Candidates are git-subdir handling on claude.ai, or the plugin living in another repository than the marketplace. claude.ai did not report a specific error.

