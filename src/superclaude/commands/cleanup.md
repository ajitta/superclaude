---
description: Systematic code cleanup — remove dead code and optimize project structure. On request only — the user's /sc:cleanup or a workflow step that names it. Not for tidying one function or import — edit directly.
---
<component name="cleanup" type="command">

  <role command="/sc:cleanup">
    <mission>Clean code systematically, remove dead code and optimize project structure</mission>
  </role>

  <syntax>/sc:cleanup [target] [--type code|imports|files|docs|all] [--safe|--aggressive] [--interactive] [--dry-run|--apply]</syntax>

  <flow>
  1. Analyze: find cleanup candidates and check each one is safe to change.
  2. Plan: pick the approach and decide whether to delegate to an agent.
  3. Execute: clean per --type. For --type docs, run the checks in the validator checks section in order (R1 standalone-valid, R2 cross-feature `[[...]]` flag, R3 slug-overlap promotion suggestion, then the slug-duplicate lint and README index regeneration).
  4. Validate: confirm no functionality was lost (tests pass).
  5. Report: summarize the changes and recommend follow-up maintenance.
  </flow>

  <flags>
  - --type code|imports|files|docs|all: what to clean; actions per type in the outputs table and the Execute step.
  - --safe: change only the safe tier of the auto-fix threshold (unused imports, dead variables); list approval-required items (file deletions, exported functions, config files, shared modules) without changing them; unrelated to the global --safe-mode.
  - --aggressive: also change approval-required items, each after the user approves it; remove code with no static reference only after a search for dynamic references (string lookups, reflection, config) finds none.
  - --interactive: show each change group and apply it only after the user accepts it; under --dry-run nothing is applied and the accepted groups form the preview.
  - --dry-run: read-only preview for any --type, nothing applied; for --type docs, what it reports is in the validator checks section.
  - --apply: required for any --type docs change; without it --type docs only reports. Changes are limited to frontmatter shape and README `## Documents` regeneration; see the manual-gate gotcha.
  </flags>

  <outputs note="Per --type flag">
| Type | Actions | Report |
|---|---|---|
| code | Remove dead code | Console: removed items + line count |
| imports | Remove unused imports | Console: removed imports per file |
| files | List orphan and empty files; delete each batch after the user confirms it | Console: listed paths + deleted file list |
| docs | R1-R3 validator (standalone docs valid, cross-link form, slug-overlap) + slug-duplicate lint; with --apply, frontmatter shape fixes + README index regeneration | Console: violations + promotion candidates + changed files (with --apply) |
| all | All above | Console: combined summary |
  </outputs>


  <tools>
  - Read/Grep/Glob: analyze and detect patterns
  - Edit: apply safe changes
  - Bash: delete files the user confirmed
  - TaskCreate/TaskUpdate: track progress
  - Agent: delegate large-scale cleanups
  </tools>

  <validator_checks note="--type docs only">
    - R1-standalone-valid: a standalone doc in `docs/{specs,plans,research,analysis}/` is valid on its own; it is flagged only when R3 finds a second doc with its slug. No date cutoff applies.
    - R2-cross-feature-link-form: Grep `\[\[[a-z0-9-]+\]\]` pattern across `docs/features/*/*.md` (skip fenced code blocks to avoid false positives on syntax examples). Each match = warning "use relative path per core/rules/RULES_DOCS.md cross-links rule (`../<other-slug>/NN-<phase>.md`); slug refs not supported". Standalone-doc matches not flagged (legacy tolerated).
    - R3-slug-overlap: Build slug set from (a) `docs/features/<slug>/` dir names + (b) standalone filename slugs (extract per `<slug>-<suffix?>-<username>-YYYY-MM-DD.md` pattern, strip suffix/username/date). Any slug appearing in ≥2 places = "consider promotion" suggestion — surface as "candidate: /sc:promote-feature <slug>". Suggestion-only; never auto-migrate.
    - R-existing-slug-lint: Pre-existing per core/rules/RULES_DOCS.md `<doc_output_convention>` formatter mention. Detects same slug used by two standalone docs of same type.
    - R-existing-readme-regen: Auto-regenerate `docs/features/*/README.md` `## Documents` section from current file list when running with `--apply` flag. Read-only with `--dry-run`.
  </validator_checks>

  <examples>

| Input | Output |
|---|---|
| `src/ --type code --safe` | Conservative cleanup |
| `--type imports --safe` | Unused import analysis |
| `--type all --interactive` | Multi-domain with guidance |
| `components/ --aggressive` | Thorough cleanup |
| `--type docs --dry-run` | Preview what --apply would change, nothing applied |
| `--type docs` | Report doc violations and promotion candidates, no changes |
| `--type docs --apply` | Fix frontmatter shape + regenerate README `## Documents` |

  <example name="aggressive-without-review" type="error-path">
    - Input: /sc:cleanup --type all --aggressive (on an unfamiliar codebase)
    - Why wrong: an aggressive cleanup without understanding the codebase risks removing code that looks unused but is referenced dynamically.
    - Correct: /sc:cleanup --type all --dry-run first, review the result, then /sc:cleanup --type all --safe
  </example>

  </examples>


  <gotchas>
  - scope-check: clean only files in the requested scope; never touch adjacent directories.
  - verify-unused: confirm a file is truly unused (grep for references) before listing it for deletion.
  - code-block-false-positive: R2 `[[...]]` pattern matches markdown wiki-syntax but also literal `[[...]]` examples inside fenced code blocks; pre-filter ` ``` ` blocks before matching to avoid noise.
  - slug-overlap-noise: R3 may flag legitimately distinct features sharing kebab prefix (e.g., `auth-flow` vs `auth-v2`). Output is suggestion-only; user judges per case. False positives are tolerable.
  - manual-gate: the --type docs validator never auto-migrates. Without --apply it only reports; --apply is required for any change and is limited to frontmatter shape fixes and README `## Documents` regeneration. Bulk promotion is /sc:promote-feature scope.
  </gotchas>

  <bounds>
    <does>cleans systematically, checks safety before each change, deletes files only after the user confirms the listed paths.</does>
    <never>removes code without analysis, overrides exclusions, or breaks functionality.</never>
  </bounds>

  <auto_fix_threshold>
    <safe>Unused imports, dead variables</safe>
    <approval_required>File deletions (empty or orphan files: list the paths, one confirmation per batch), exported functions, config files, shared modules</approval_required>
  </auto_fix_threshold>

  <handoff next="/sc:test /sc:build"/>
</component>