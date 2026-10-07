# Session 2026-10-08: portable-skills single plugin, intent → release v4.23.0

## Outcome
- The two portable Socratic plugins are one plugin `socratic` 1.0.0. Released v4.23.0 (GitHub release, `stable` and tag → aab16e74). Feature merge @84c7eb46, bump @ee0ba808 / merge @aab16e74.
- Feature docs: `docs/features/portable-skills-single-plugin/` (00-intent, 02-research, 05-plan `status: complete`, README `phase: complete` @4426e24a).
- Also in the 4.23.0 CHANGELOG: the destructive_op_confirmation rewording from c450b742 (deferred from the 2026-10-07 session).
- After the release: this session memory committed (3aa00a46, merge 2e69c900); CI change below (430d8553, merge da9f3329); feature README marked complete (fb2ceac5, merge 4426e24a). The commit that updates this memory is the first `.serena`-only push.

## Decisions (as made)
- Plugin name `socratic`; marketplace name `ajitta-socratic` unchanged; plugin version 1.0.0, separate from skill `metadata.version` (now 3.3.0 / 1.3.0).
- `marketplace.json` top-level `renames`: {"socratic-brainstorm": "socratic", "socratic-elenchus": "socratic"}. Append-only; never remove.
- One manifest `portable-skills/plugin-manifest.json`; generated plugin keeps skills in `plugins/socratic/skills/<skill>/`; one zip `releases/socratic.zip`; per-skill zips removed after the user confirmed the claude.ai upload.
- User requirement: installed plugin has no Korean. Source SKILL.md + references rewritten in English (Korean only in README/docs examples); test `test_shipped_plugin_has_no_hangul`.
- User requirement: docs/index.html (nav + #plugins) updated; test `test_install_docs_match_the_marketplace` ties install commands to marketplace.json.
- User-raised gap (mid-implementation heads-up): the old "skill version == plugin version" test no longer coupled bumps. Replaced by `portable-skills/plugin-release.json` (not shipped): sha256 of skill files per plugin version; package.py and `test_release_record_matches_content` refuse changed files under an unchanged version. Pre-release escape: delete the record and rebuild.
- Release: user said "CANARY_OK=0" + proceed; the Makefile accepts only `1`, so ran `CANARY_OK=1 make release` on the evidence that the only core change since v4.22.0 was c450b742 (canary gates 7/7, identical at release).
- CI (user asked why docs-only pushes run CI): `test.yml` push and pull_request now carry `paths-ignore: ['.serena/**']` — no test reads `.serena/`. Docs in general stay in CI because the suite lints Markdown (plan checklist, version consistency, gotcha budget, portable-skills docs). `pages-build-deployment` is GitHub's branch deploy and cannot be path-filtered; left as is. `.github/workflows/README.md` notes that `make release` on a `.serena`-only HEAD needs `gh workflow run Tests --ref master` first.

## Problems and resolutions
- Removing a marketplace entry leaves installs `✘ failed to load` ("not found in marketplace") — found by probe; `renames` fixes it (02-research cases A–D).
- `.gitignore` unanchored `skills/` (npx skills artifacts) silently dropped `plugins/socratic/skills/` from commit 5fcfb00a; local tests passed on disk. Fixed with a negation (e6bf752f), then anchored all four rules to root (8be5ce25) and added gotcha `gitignore-unanchored-dir`. Same rule had hidden `src/superclaude/skills` on 2026-10-05.
- A test added in e15cb65c failed `ruff format --check` (added after the last `make format`); caught in final checks, formatted before merge.
- Bash heredocs with certain content (triple quotes, `①`) failed to parse in the Bash tool; scripts were written with Write and run as files.
- `git merge -F -` does not read stdin; use `-m`.

## Verification evidence
- Routing probe (Task 4, sonnet low, `--plugin-dir`, synced copies off via `--settings`): explicit 7/7 (baseline 7/7), Korean replies, ambiguous prompts carry the pointer line 4/4, "그만" → brief / record.
- Migration: local git probe (Task 5) and real GitHub after push: old 3.2.1/1.2.1 installs → one `socratic@ajitta-socratic` 1.0.0, `Skills (2)`, enabledPlugins rewritten.
- Final: full suite 2964 passed, 1 skipped (baseline 2953); master CI Tests 3.10/3.13 + lint/plugin/doctor success; Pages deploy success.
- CI change: YAML parses; the da9f3329 push (it touches test.yml) ran Tests and all three jobs succeeded.

## Open
- Not yet observed: a `.serena`-only push actually skipping Tests. The next push that only commits a session memory shows it (expect no Tests run for that SHA; Pages still runs).
- claude.ai Add-marketplace route with `renames`: user check, meaningful only if the marketplace was added there before.

## Pointers
- Plugin/marketplace behavior facts and the probe recipe: auto memory `reference_cc-plugin-marketplace-facts`.
- Plan with Deviations and Proof: `docs/features/portable-skills-single-plugin/05-plan.md`.
